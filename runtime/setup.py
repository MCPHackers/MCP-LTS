import sys
import shutil
import os.path
import configparser
import logging
import time
import urllib.request
import traceback
import platform
import zipfile
import json
import math
from datetime import datetime

class InstallMC:
    _default_config = 'conf/mcp.cfg'
    _version_config = 'conf/version.cfg'

    def __init__(self, logger=None, conffile=None):
        self.conffile = conffile
        self.readconf()
        if platform.system() == "Windows":
            self.platform = "windows"
        elif platform.system() == "Darwin":
            self.platform = "macosx"
        else:
            self.platform = "linux"
        self.confdir = self.config.get("DEFAULT", "DirConf")
        self.vers = self.config.get("DEFAULT", "DirVers")
        self.jardir = self.config.get("DEFAULT", "DirJars")
        self.tempdir = self.config.get("DEFAULT", "DirTemp")
        self.logdir = self.config.get("DEFAULT", "DirLogs")
        self.mcplogfile = self.config.get('MCP', 'LogFile')
        self.mcperrlogfile = self.config.get('MCP', 'LogFileErr')
        self.logger = logger
        if self.logger == None:
            self.startlogger()

    def startlogger(self):
        """
        Basically sets up a logger and different logger handlers for different levels and such.
        Code copied from commands.py:92
        :return:
        """
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.logger = logging.getLogger('MCPLog')
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(filename=self.mcplogfile, mode='w')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # File output of everything Warning or above
        eh = logging.FileHandler(filename=self.mcperrlogfile, mode='w')
        eh.setLevel(logging.WARNING)
        # create formatter and add it to the handlers
        formatterconsole = logging.Formatter('%(message)s')
        ch.setFormatter(formatterconsole)
        formatterfile = logging.Formatter('%(asctime)s - %(module)11s.%(funcName)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M')
        fh.setFormatter(formatterfile)
        eh.setFormatter(formatterfile)
        # add the handlers to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)
        self.logger.addHandler(eh)

    def start(self, scriptsonly=False):
        #Main entry function.
        print()
        self.logger.info("> Python: " + sys.version)

        self.logger.info("> Welcome to the RetroMCP setup script!")
        self.logger.info("> This script will automatically set up your MCP workspace.")

        if os.path.exists("src"):
            print()
            self.logger.info("! /src exists! Aborting.")
            self.logger.info("! Run cleanup in order to run setup again.")
            sys.exit()
        print()
        self.logger.info("> Setting up your workspace...")
        print()
        self.logger.info("> Making sure temp exists...")
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)
        self.logger.info("> Making sure jars/bin/natives exists.")
        if not os.path.exists(os.path.join(self.jardir, "bin", "natives")):
            os.makedirs(os.path.join(self.jardir, "bin", "natives"))

        if scriptsonly:
            print()
            self.logger.info("> Copying scripts...")
            for file in os.listdir(os.path.join("runtime", self.platform + "_scripts")):
                shutil.copy2(os.path.join("runtime", self.platform + "_scripts", file), ".")
        else:
            natives = {
                "windows": "http://files.betacraft.uk/launcher/assets/natives-windows.zip",
                "macosx": "http://files.betacraft.uk/launcher/assets/natives-osx.zip",
                "linux": "http://files.betacraft.uk/launcher/assets/natives-linux.zip"
            }
            print()
            self.logger.info("> Downloading libraries...")
            libtime = time.time()
            self.download("http://files.betacraft.uk/launcher/assets/libs-windows.zip", os.path.join(self.jardir, "bin", "libs.zip"))
            
            self.logger.info("> Downloading natives for your platform...")
            self.download(natives[self.platform], os.path.join(self.jardir, "bin", "natives.zip"))
            self.logger.info('> Done in %.2f seconds' % (time.time() - libtime))
            print()
            self.logger.info("> Extracting...")
            exttime = time.time()
            nativezip = zipfile.ZipFile(os.path.join(self.jardir, "bin", "libs.zip"))
            nativezip.extractall(os.path.join(self.jardir, "bin"))
            nativezip.close()
            if os.path.isfile(os.path.join(self.jardir, "bin", "libs.zip")):
                os.unlink(os.path.join(self.jardir, "bin", "libs.zip"))
            nativezip = zipfile.ZipFile(os.path.join(self.jardir, "bin", "natives.zip"))
            nativezip.extractall(os.path.join(self.jardir, "bin", "natives"))
            nativezip.close()
            if os.path.isfile(os.path.join(self.jardir, "bin", "natives.zip")):
                os.unlink(os.path.join(self.jardir, "bin", "natives.zip"))
            self.logger.info('> Done in %.2f seconds' % (time.time() - exttime))
            print()
            self.logger.info("> Copying scripts...")
            scripts_dir = 'unix_scripts' if self.platform != 'windows' else 'windows_scripts'

            for file in os.listdir(os.path.join("runtime", scripts_dir)):
                shutil.copy2(os.path.join("runtime", scripts_dir, file), ".")
            print()
            self.logger.info("> Setting up minecraft...")
            self.setupmc()


    def setupmc(self):
        self.logger.info("> If you wish to supply your own configuration, type \"custom\".")

        versions = []
        for version in os.listdir(self.vers):
            if os.path.isdir(os.path.join(self.vers, version)) and version not in ["custom","workspace"] and not os.path.exists(os.path.join(self.vers, version, "DISABLED")):
                versions.append(version)
        f = open(os.path.join("versions","versions.json"))
        versionsjson = json.load(f)
        inp = ""
        confname = inp
        foundmatch = False
        while not foundmatch:
            self.logger.info("> Current versions are:")
            versionslist = []
            for v in versions:
                for y in v.split(","):
                    x = versionsjson["client"][y]["time"]
                    versionslist.append({"time": x, "version": y})
            versionslist.sort(key = lambda x: datetime.strptime(x["time"], '%Y-%m-%d'))
            versionslist.reverse()
            rows = math.ceil(len(versionslist)/3)
            table_list = [[] for _ in range(rows)]
            for index, item in enumerate(versionslist):
                row_index = index % rows
                table_list[row_index].append(" - " + item["version"].ljust(15))

            table_str = "\n".join(["".join(i) for i in table_list])
            self.logger.info(table_str)
            print()
            self.logger.info("> What version would you like to install?")

            inp = str(input(": "))

            if inp == "custom":
                foundmatch = True
                confname = inp
            else:
                for y in versions:
                    for x in y.split(","):
                        if x == inp:
                            foundmatch = True
                            confname = y

        try:
            if os.path.exists(self.confdir):
                for patches in ["patches_client" , "patches_server"]:
                    if os.path.exists(os.path.join(self.confdir, patches)) and os.path.isdir(os.path.join(self.confdir, patches)):
                        shutil.rmtree(os.path.join(self.confdir, patches))
                for file in os.listdir(self.confdir):
                    if os.path.isfile(os.path.join(self.confdir, file)) and file not in ["mcp.cfg","versions.json"]:
                        os.unlink(os.path.join(self.confdir, file))
        except Exception as e:
            self.logger.info("> Couldn't clear config!")

        copytime = time.time()
        self.logger.info("> Copying config")
        self.copydir(os.path.join(self.vers, confname), self.confdir)
        with open(self._version_config, "a") as file:
            file.write('ClientVersion = ' + inp + '\n')
            if inp == "custom":
                file.write('ServerVersion = ' + inp + '\n')
            elif inp in versionsjson["client"]:
                if "server" in versionsjson["client"][inp]:
                    file.write('ServerVersion = ' + versionsjson["client"][inp]["server"] + '\n')
                elif inp in versionsjson["server"]:
                    file.write('ServerVersion = ' + inp + '\n')
        no_error = True
        try:
            if os.path.exists("eclipse"):
                shutil.rmtree("eclipse")
        except:
            no_error = False
            commands.logger.info("> Couldn't clear workspace!")
        if no_error:
            self.logger.info("> Copying workspace")
            workspace = 0
            try:
                workspace = versionsjson["client"][inp]["workspace_version"]
            except:
                pass
            self.copydir(os.path.join(self.vers, "workspace", "eclipse_" + str(workspace)), "eclipse")
            for proj in ["Client", "Server"]:
                p = os.path.join("eclipse", proj, proj + ".iml")
                if os.path.exists(p):
                    f = open(p,'r')
                    filedata = f.read()
                    f.close()

                    newdata = filedata.replace("$MCP_LOC$", os.getcwd().replace("\\", "/"))

                    f = open(p,'w')
                    f.write(newdata)
                    f.close()
                    
        self.logger.info('> Done in %.2f seconds' % (time.time() - copytime))
        
        if os.path.exists(os.path.join(self.jardir, "minecraft_server.jar")):
            os.unlink(os.path.join(self.jardir, "minecraft_server.jar"))
        if os.path.exists(os.path.join(self.jardir, "bin", "minecraft.jar")):
            os.unlink(os.path.join(self.jardir, "bin", "minecraft.jar"))
            
        if inp != "custom":
            self.logger.info("> Downloading Minecraft client...")
            clientdltime = time.time()
            self.download(versionsjson["client"][inp]["url"],
                          os.path.join(self.jardir, "bin", "minecraft.jar"))
            self.logger.info('> Done in %.2f seconds' % (time.time() - clientdltime))
            ver = inp
            serverdltime = time.time()
            if ver in versionsjson["server"] or "server" in versionsjson["client"][ver]:
                self.logger.info("> Downloading Minecraft server...")
                ver2 = ver
                if "server" in versionsjson["client"][ver]:
                    ver2 = versionsjson["client"][ver]["server"]
                dlname = "minecraft_server.jar"
                extract = False
                if versionsjson["server"][ver2]["url"].endswith(".zip"):
                    dlname = "minecraft_server.zip"
                    extract = True
                self.download(versionsjson["server"][ver2]["url"], os.path.join(self.jardir, dlname))
                if extract and os.path.exists(os.path.join(self.jardir, dlname)):
                    self.logger.info("> Extracting Minecraft server...")
                    serverzip = zipfile.ZipFile(os.path.join(self.jardir, dlname))
                    serverzip.extractall(self.jardir)
                    serverzip.close()
                    if os.path.exists(os.path.join(self.jardir, "minecraft-server.jar")):
                        os.rename(os.path.join(self.jardir, "minecraft-server.jar"),os.path.join(self.jardir, "minecraft_server.jar"))
                    if os.path.exists(os.path.join(self.jardir, dlname)):
                        os.unlink(os.path.join(self.jardir, dlname))
                self.logger.info('> Done in %.2f seconds' % (time.time() - serverdltime))
        else:
            self.logger.info('> Make sure to copy version jars into jars folder!')

    def download(self, url, dst):
        # Because legacy code is stupid.
        try:
            self.logger.debug("> Downloading \"" + url + "\"...")
            response = urllib.request.urlopen(url)
            data = response.read()
            with open(dst, "wb") as file:
                file.write(data)

            self.logger.debug("> Done!")
        except:
            print("> Unable to download \"" + url + "\"")

    def copydir(self, src, dst, replace=True):
        """
        Shutil's built in copytree function raises an exception if src exists.
        This is basically copytree minus the exceptions and added logging.
        :param src:
        :param dst:
        :param replace:
        :return:
        """
        for file in os.listdir(src):
            if os.path.isfile(os.path.join(src, file)):
                if os.path.exists(os.path.join(dst, file)) and not replace:
                    self.logger.debug("> Skipped file \"" + os.path.join(src, file) + "\": Already exists.")
                elif os.path.exists(os.path.join(dst, file)):
                    os.unlink(os.path.join(dst, file))
                    shutil.copy2(os.path.join(src, file), dst)
                    self.logger.debug("> Replaced file \"" + os.path.join(src, file) + "\".")
                else:
                    shutil.copy2(os.path.join(src, file), dst)
                    self.logger.debug("> Copied file \"" + os.path.join(src, file) + "\".")
            elif os.path.isdir(os.path.join(dst, file)):
                self.copydir(os.path.join(src, file), os.path.join(dst, file))
            else:
                os.makedirs(os.path.join(dst, file))
                self.copydir(os.path.join(src, file), os.path.join(dst, file))

    def readconf(self):
        """
        Reads config and creates a class from it.
        :return:
        """
        config = configparser.ConfigParser()
        with open(self._default_config) as config_file:
            config.read_file(config_file)
        if self.conffile is not None:
            config.read(self.conffile)
        self.config = config

    def writeCommand(self, command):
        if os.path.exists("runtime/command"):
            os.unlink("runtime/command")

        with open("runtime/command", "w") as file:
            file.write(command)


if __name__ == '__main__':
    installmc = InstallMC()

    if sys.argv.__len__() == 2:
        if sys.argv[1] == "scriptsonly":
            installmc.start(True)
        else:
            installmc.writeCommand(sys.argv[1])
            installmc.start()
    elif sys.argv.__len__() == 3:
        installmc.writeCommand(sys.argv[2])
        installmc.start(True)
    else:
        installmc.start()
