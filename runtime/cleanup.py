import shutil
import os
import sys
import time
import configparser
import platform
import traceback
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Workaround for python 3.6's obtuse import system.
from commands import Commands

def main(conffile=None):
    commands = Commands(conffile)
    commands.logger.info("> Input 'y' to delete your workspace and set most of it to factory defaults.")
    commands.logger.info("> Input 's' if you want to only clear the source and bin folders")
    commands.logger.info("> Are you sure you want to clean up your workspace? [y/N/s]")
    b = True
    while b:
        inp = input(": ")
        clearsrc = False
        cleareclipse = True
        b = inp.lower() != "y" and inp.lower() != "s"
        if inp.lower() == "n":
            return
        if inp.lower() == "s":
            clearsrc = True
            cleareclipse = False
        if b:
            print("Invalid option!")
    commands.logger.info("> Are you *REALLY* sure you want to clean up your workspace? [y/N]")
    if clearsrc:
        commands.logger.info("> This deletes ALL your source files!")
    else:
        commands.logger.info("> This deletes ALL your source files and jars! This is NOT recoverable!")
    b = True
    while b:
        inp = input(": ")
        b = inp.lower() != "y"
        if inp.lower() == "n":
            return
        if b:
            print("Invalid option!")

    commands.logger.info("> Commencing the purge of the universe...")
    clear(commands, clearsrc, cleareclipse)
    # Pausing execution in python because the batch is already deleted
    os.system('pause')
    sys.exit()

def clear(commands, clearsrc=False, cleareclipse=True):
    no_error = True


    deltime = time.time()
    if not clearsrc:
        commands.logger.info("> Deleting \"" + commands.dirjars + "\"...")
        try:
            if os.path.exists(commands.dirjars):
                if not os.path.exists(commands.dirtemp):
                    os.makedirs(commands.dirtemp)
                shutil.rmtree(commands.dirjars)
                os.makedirs(commands.dirjars)
        except Exception as e:
            no_error = False
            commands.logger.info("> Couldn't clear \"" + commands.dirjars + "\"!")
            traceback.print_exc()

    cleardirs = [commands.dirreobf, commands.dirbin, commands.dirsrc, commands.dirtemp]
    if cleareclipse:
        cleardirs.append(commands.direclipse)
    for dir in cleardirs:
        commands.logger.info("> Deleting \"" + dir + "\"...")
        try:
            if os.path.exists(dir):
                shutil.rmtree(dir)
        except Exception as e:
            no_error = False
            commands.logger.info("> Couldn't clear \"" + dir + "\"!")
            traceback.print_exc()

    if not clearsrc:
        commands.logger.info("> Deleting config...")
        try:
            if os.path.exists(commands.dirconf):
                for patches in ["patches_client" , "patches_server"]:
                    if os.path.exists(os.path.join(commands.dirconf, patches)) and os.path.isdir(os.path.join(commands.dirconf, patches)):
                        shutil.rmtree(os.path.join(commands.dirconf, patches))
                for file in os.listdir(commands.dirconf):
                    if os.path.isfile(os.path.join(commands.dirconf, file)) and file not in ["mcp.cfg","versions.json"]:
                        os.unlink(os.path.join(commands.dirconf, file))
        except Exception as e:
            no_error = False
            commands.logger.info("> Couldn't clear \"" + commands.dirconf + "\"!")
            traceback.print_exc()

        commands.logger.info("> Deleting system specific files from root...")
        try:
            for file in ["decompile", "recompile", "reobfuscate", "startclient", "startserver", "switchversion", "updatemcp", "updatemd5"]:
                if os.path.exists(file + "." + systemext) and os.path.isfile(file + "." + systemext):
                    os.unlink(file + "." + systemext)
        except Exception as e:
            no_error = False
            commands.logger.info("> Couldn't clear system specific files!")
            traceback.print_exc()

    if no_error and not clearsrc:
        os.unlink("cleanup." + systemext)
    elif not no_error:
        commands.logger.info("> Cleanup file has not been deleted because an error occurred earlier.")
    commands.logger.info('> Done in %.2f seconds' % (time.time() - deltime))

if __name__ == '__main__':
    if platform.system() == "Windows":
        systemext = "bat"
    else:
        systemext = "sh"
    main()