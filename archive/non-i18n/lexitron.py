#!/usr/bin/env python3
# lexitron.py
# jcj 2019-02-20, 2019-05-29, 2019-07-06

'''
An application to exercise the functionality of the Lexicon class implemented
in lexicon.py. It can be used as a command-line tool or interactively using a
dumb-console, smart-terminal, or fully graphic interface.
'''

import sys
import os.path
import argparse
import configparser
from error import *

from lexGui import guiMain		# graphical user interface
from lexCon import conMain		# dumb-console user interface
from lexTerm import termMain	# smart-terminal user interface
from lexVer import DESCRIPTION

CONFIG_FILENAME = '.lexitronrc'
LEXICON_FILENAME = '/usr/share/dict/words'

def getDefaultLex():
	'''Try to get a default lexicon name from a configuration file,
	otherwise fall back on a hard-wired name'''
	result = LEXICON_FILENAME
	configFileName = os.path.join(os.path.expanduser('~'), CONFIG_FILENAME)
	if os.path.exists(configFileName):
		config = configparser.ConfigParser()
		try:
			config.read(configFileName)
		except Exception as err:
			error(FAIL, str(err))
		result = config['DEFAULT'].get('LexiconFile', result)
	return result

def main():
	'''Perform option and argument processing and file opening and closing'''
	
	parser = argparse.ArgumentParser(prog=PROGNAME, description=__doc__,
					formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-c', '--icase', action='store_true',
					help='ignore case')
	parser.add_argument('-d', '--idiac', action='store_true',
					help='ignore diacritics')
	parser.add_argument('-i', '--interface', choices={'c', 'g', 't'},
					default='c',
					help='user interface: (dumb) console, gui, (smart) terminal, '
					     'default: console')
	parser.add_argument('-l', '--lexicon', default=getDefaultLex(),
					help='specify lexicon file to use, '
					     'default specified in ~/%s, else: %s' % (CONFIG_FILENAME, LEXICON_FILENAME))
	parser.add_argument('-v', '--version', action='version', version=DESCRIPTION)
	parser.add_argument('-x', '--exec', action='append',
					help='execute the given console-style command '
					     '(implies -i c, can be given multiple times) '
						 'and then quit')
	args = parser.parse_args()
	if args.exec and args.interface != 'c':
		error(BADUSE, '-x/--exec implies -i c/--interface c')
	{ 'c': conMain, 'g':guiMain, 't':termMain }[args.interface](args.lexicon, args.icase, args.idiac, args.exec)
	sys.exit(0)

if __name__ == '__main__':
	main()

