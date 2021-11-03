import shutil
import os
import sys
import time
import configparser
import platform
import traceback


class Cleanup:
    _default_config = 'conf/mcp.cfg'

    def __init__(self, conffile=None):
        self.conffile = conffile
        self.readconf()
        self.confdir = self.config.get("DEFAULT", "DirConf")
        self.tempdir = self.config.get("DEFAULT", "DirTemp")
        self.logdir = self.config.get("DEFAULT", "DirLogs")
        self.srcdir = self.config.get("DEFAULT", "DirSrc")
        self.bindir = self.config.get("DEFAULT", "DirBin")
        self.reobfdir = self.config.get("DEFAULT", "DirReobf")
        self.jardir = self.config.get("DEFAULT", "DirJars")
        self.mcplogfile = self.config.get('MCP', 'LogFile')
        self.mcperrlogfile = self.config.get('MCP', 'LogFileErr')
        if platform.system() == "Windows":
            self.systemext = "bat"
        else:
            self.systemext = "sh"

    def start(self):
        print("> Welcome to the RetroMCP cleanup script!")
        print("> Input 'y' to delete your workspace and set most of it to factory defaults.")
        print("> Input 's' if you want to only clear the source and bin folders")
        print("> Are you sure you want to clean up your workspace? [y/N/s]")
        b = True
        while b:
            inp = input(": ")
            clearsrc = False
            b = inp.lower() != "y" and inp.lower() != "s"
            if inp.lower() == "n":
                return
            if inp.lower() == "s":
                clearsrc = True
            if b:
                print("Invalid option!")
        print("> Are you *REALLY* sure you want to clean up your workspace? [y/N]")
        if clearsrc:
            print("> This deletes ALL your source files!")
        else:
            print("> This deletes ALL your source files and jars! This is NOT recoverable!")
        b = True
        while b:
            inp = input(": ")
            b = inp.lower() != "y"
            if inp.lower() == "n":
                return
            if b:
                print("Invalid option!")

        print("> Commencing the purge of the universe...")
        no_error = True

        print("> Deleting \"" + self.jardir + "\"...")
        deltime = time.time()
        # Delete jars while keeping server.properties.
        if not clearsrc:
            try:
                if os.path.exists(self.jardir):
                    if not os.path.exists(self.tempdir):
                        os.makedirs(self.tempdir)
                    #if os.path.exists(os.path.join(self.jardir, "server.properties")):
                    #    shutil.copy2(os.path.join(self.jardir, "server.properties"), self.tempdir)
                    shutil.rmtree(self.jardir)
                    os.makedirs(self.jardir)
                    #if os.path.exists(os.path.join(self.tempdir, "server.properties")):
                    #    shutil.copy2(os.path.join(self.tempdir, "server.properties"), self.jardir)
            except Exception as e:
                no_error = False
                print("> Couldn't clear \"" + self.jardir + "\"!")
                traceback.print_exc()

        cleardirs = [self.reobfdir, self.bindir, self.srcdir, self.tempdir]
        for dir in cleardirs:
            print("> Deleting \"" + dir + "\"...")
            try:
                if os.path.exists(dir):
                    shutil.rmtree(dir)
            except Exception as e:
                no_error = False
                print("> Couldn't clear \"" + dir + "\"!")
                traceback.print_exc()

        if not clearsrc:
            print("> Deleting non-default config...")
            try:
                if os.path.exists(self.confdir):
                    if os.path.exists(os.path.join(self.confdir, "patches_client")) and os.path.isdir(os.path.join(self.confdir, "patches_client")):
                        shutil.rmtree(os.path.join(self.confdir, "patches_client"))
                    if os.path.exists(os.path.join(self.confdir, "patches_server")) and os.path.isdir(os.path.join(self.confdir, "patches_server")):
                        shutil.rmtree(os.path.join(self.confdir, "patches_server"))
                    for file in os.listdir(self.confdir):
                        if os.path.isfile(os.path.join(self.confdir, file)) and file not in ["mcp.cfg"]:
                            os.unlink(os.path.join(self.confdir, file))
            except Exception as e:
                no_error = False
                print("> Couldn't clear \"" + self.confdir + "\"!")
                traceback.print_exc()

            print("> Deleting system specific files from root...")
            try:
                for file in ["decompile", "recompile", "reobfuscate", "startclient", "startserver", "updatemcp", "updatemd5"]:
                    if os.path.exists(file + "." + self.systemext) and os.path.isfile(file + "." + self.systemext):
                        os.unlink(file + "." + self.systemext)
            except Exception as e:
                no_error = False
                print("> Couldn't clear system specific files!")
                traceback.print_exc()

        if no_error and not clearsrc:
            os.unlink("cleanup." + self.systemext)
        elif not no_error:
            print("> Cleanup file has not been deleted because an error occurred earlier.")
        print('> Done in %.2f seconds' % (time.time() - deltime))
        # Using input() instead of pause because the batch gets deleted before the script is finished
        print('Press enter to continue...')
        input()

    def readconf(self):
        """
        Reads config and creates a class from it.
        Code copied from commands.py:126
        :return:
        """
        config = configparser.ConfigParser()
        with open(self._default_config) as config_file:
            config.read_file(config_file)
        if self.conffile is not None:
            config.read(self.conffile)
        self.config = config

if __name__ == '__main__':
    cleanup = Cleanup()
    cleanup.start()
