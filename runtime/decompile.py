# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 16:54:36 2011

@author: ProfMobius
@version: v1.2
"""
import time
import os
import sys
import shutil
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Workaround for python 3.6's obtuse import system.
from commands import Commands
import recompile as recompile


def main(conffile, no_patch, rename, no_lvt):
    commands = Commands(conffile)
    commands.checkforupdates()

    cltdone = decompile_side(0, commands, no_patch, rename, no_lvt)
    srvdone = True
    if commands.hasserver():
        srvdone = decompile_side(1, commands, no_patch, rename, no_lvt)
    if not cltdone or not srvdone:
        commands.logger.info('== Post decompiling operations ==')
        commands.logger.info('> Recompiling')
        recompile.main(conffile)
    if not cltdone:
        commands.logger.info('> Generating the md5 (client)')
        commands.gathermd5s(0)
    if commands.hasserver():
        if not srvdone:
            commands.logger.info('> Generating the md5 (server)')
            commands.gathermd5s(1)


def decompile_side(side=0, commands=None, no_patch=False, rename=False, no_lvt=False):
    use_ff = os.path.exists(commands.fernflower)

    srcdir = None

    if side == 0:
        srcdir = commands.srcclient.replace('/', os.sep).replace('\\', os.sep)
    if side == 1:
        srcdir = commands.srcserver.replace('/', os.sep).replace('\\', os.sep)

    if not srcdir:
        commands.logger.info('!! Side is not provided !!')
        return True

    if not os.path.exists(srcdir):
        excconf = {0: commands.xclientconf, 1: commands.xserverconf}
        patchlk = {0: commands.patchclient, 1: commands.patchserver}
        excinput = {0: commands.rgclientout, 1: commands.rgserverout}
        excoutput = {0: commands.xclientout, 1: commands.xserverout}
        jarlk = {0: commands.jarclient, 1: commands.jarserver}
        sidelk = {0: commands.rgsrgsclient, 1: commands.rgsrgsserver}
        if side == 0:
            commands.logger.info('== Decompiling Client ==')
        if side == 1:
            commands.logger.info('== Decompiling Server ==')

        if commands.checkjars(side):
            currenttime = time.time()
            commands.logger.info('> Creating SRGS')
            commands.createsrgs(side)
            if os.path.exists(sidelk[side]) and not rename:
                commands.logger.info('> Applying Retroguard')
                commands.creatergcfg(reobf=False, keep_lvt=not no_lvt, keep_generics=False, rg_update=False)
                commands.applyrg(side)
            else:
                shutil.copyfile(jarlk[side], excinput[side])
            if os.path.exists(excconf[side]):
                commands.logger.info('> Applying MCInjector')
                commands.applyexceptor(side)
            else:
                shutil.copyfile(excinput[side], excoutput[side])
            commands.logger.info('> Unpacking jar')
            commands.extractjar(side)
            commands.logger.info('> Copying classes')
            commands.copycls(side)
            commands.logger.info('> Decompiling...')
            commands.applyff(side, rename)
            commands.logger.info('> Copying sources')
            commands.copysrc(side)
            if os.path.exists(patchlk[side]) and not no_patch:
                commands.logger.info('> Applying patches')
                commands.applyffpatches(side)
            if side == 0:
                commands.logger.info('> Replacing LWJGL constants')
                commands.process_annotate(side)
            commands.logger.info('> Done in %.2f seconds' % (time.time() - currenttime))
        else:
            return True
    else:
        if side == 0:
            commands.logger.warn('!! Client already decompiled. Run cleanup before decompiling again !!')
        if side == 1:
            commands.logger.warn('!! Server already decompiled. Run cleanup before decompiling again !!')
        return True

    return False


if __name__ == '__main__':
    parser = OptionParser(version='RetroMCP %s' % Commands.MCPVersion)
    parser.add_option('-r', '--ren', dest='rename', action='store_true', help='rename ambiguous classes', default=False)
    parser.add_option('-p', dest='no_patch', action='store_true', help='disable patches', default=False)
    parser.add_option('--nolvt', dest='no_lvt', action='store_true', help='remove local variable tables', default=False)
    parser.add_option('-c', '--config', dest='config', help='additional configuration file')
    (options, args) = parser.parse_args()
    main(options.config, options.no_patch, options.rename, options.no_lvt)
