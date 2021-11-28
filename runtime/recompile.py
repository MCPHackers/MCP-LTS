# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 16:54:36 2011

@author: ProfMobius
@version: v1.0
"""
import time
import os
import sys
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # Workaround for python 3.6's obtuse import system.
from commands import Commands


def main(conffile=None):
    commands = Commands(conffile)

    commands.logger.info('> Recompiling client...')
    recompile(0, commands)
        
    if commands.hasserver():
        commands.logger.info('> Recompiling server...')
        recompile(1, commands)

def recompile(side=0, commands=None):
    recomptime = time.time()
    if commands.checksources(side):
        commands.cleanbindirs(side)
        commands.recompile(side)
        commands.logger.info('> Done in %.2f seconds' % (time.time() - recomptime))

if __name__ == '__main__':
    parser = OptionParser(version='MCP %s' % Commands.MCPVersion)
    parser.add_option('-c', '--config', dest='config', help='additional configuration file')
    (options, args) = parser.parse_args()
    main(options.config)
