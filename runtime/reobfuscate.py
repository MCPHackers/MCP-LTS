# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 16:54:36 2011

@author: ProfMobius
@version: v1.1
"""
from optparse import OptionParser
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from commands import Commands


def main(conffile=None):
    commands = Commands(conffile)

    commands.logger.info('== Reobfuscating client ==')
    reobfuscate(0, commands)

    if commands.hasserver():
        commands.logger.info('== Reobfuscating server ==')
        reobfuscate(1, commands)

def reobfuscate(side=0, commands=None):
    if commands.checkbins(side):
        commands.cleanreobfdir(side)
        commands.logger.info('> Gathering md5 checksums')
        commands.gathermd5s(side, True)
        if side == 0:
            commands.logger.info('> Compacting client bin directory')
        elif side == 1:
            commands.logger.info('> Compacting server bin directory')
        commands.packbin(side)
        commands.logger.info('> Creating reobfuscation config')
        commands.creatergcfg(reobf=True)
        if side == 0:
            commands.logger.info('> Reobfuscating client jar')
        elif side == 1:
            commands.logger.info('> Reobfuscating server jar')
        commands.applyrg(side, True)
        commands.logger.info('> Extracting modified classes')
        commands.unpackreobfclasses(side)

if __name__ == '__main__':
    parser = OptionParser(version='MCP %s' % Commands.MCPVersion)
    parser.add_option('-c', '--config', dest='config', help='additional configuration file')
    (options, args) = parser.parse_args()
    main(options.config)
