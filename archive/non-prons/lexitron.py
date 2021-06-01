#!/usr/bin/env python3
# lexitron.py
# jcj 2019-02-20, 2019-05-29, 2019-07-06, 2020-02-11

'''
Exercise the functionality of the Lexicon class implemented in lexicon.py
through a variety of different interfaces and in various languages.
'''

# gettext must be installed before importing modules that use it
LOCALE_BASE = 'lexitron'
LOCALE_DIR = '/home/jason/locales'
import gettext
language = gettext.translation(LOCALE_BASE, localedir=LOCALE_DIR, fallback=True)
language.install(['pgettext']) # as well as the default _ for gettext
# Versions prior to Python 3.8 do not support pgettext. So...
try:
	pgettext
except NameError:
	from pgettext import pgettext
__ = pgettext
# _ as an alias for gettext.gettext has been installed in the builtins namespace,
# and pgettext will also have been installed if supported by the Python version

import sys
import os.path
import getopt
import configparser
from error import *             # PROGNAME and error

import lexVer                   # name and version strings
from lexCon import conMain		# dumb-console user interface
from lexTerm import termMain	# smart-terminal user interface
from lexGui import guiMain		# graphical user interface

CONFIG_FILENAME = '.lexitronrc'
LEXICON_FILENAME = '/usr/share/dict/words'
CONFIG_FORMAT = '''
    [DEFAULT]
    LexiconFile = /path/to/LexiconFile
'''

SUMMARY = _('''
Load a lexicon (a bare list of words) and provide facilities to check for word
inclusion, the existence of prefixes and suffixes, regular expressions, and
anagrams. Comparisons may be made ignoring case and/or diacritics. Queries can
be submitted on the command line or interactively via a dumb-console, smart-
terminal, or fully graphical interface.
''')

USAGE = __('Translator: Do not translate the options beginning with - or --, '
           'or any lower-case argument to the options, eg console. You may '
		   'translate any upper-case argument, eg COMMAND.',
'''
Usage: {programName} OPTIONS

OPTIONS:
    -h, --help            print this message and exit
    -v, --version         print version information and exit
    -c, --icase           ignore letter-case in matching
    -d, --idiac           ignore diacritics in matching
    -l, --lexicon LEX     use lexicon file LEX instead of the
                          default specified in {configFileName}, or
                          the ultimate default {ultimateDefaultLex}
    -i, --interface console|terminal|graphic 
                          use the specified kind of user interface,
                          default: console (only the first letter
                          of the interface designator is necessary)
    -x, --exec COMMAND    execute console-style command COMMAND
                          (may be used multiple times), then exit

A configuration file ~/{configFileName} may be used to specify a default
lexicon. At the minimum, the configuration file looks like this
(but without any indentation): {configFileFormat}''').format(
	programName=PROGNAME,
	configFileName=CONFIG_FILENAME,
	ultimateDefaultLex=LEXICON_FILENAME,
	configFileFormat=CONFIG_FORMAT)

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
	'''Perform option and argument processing'''
	interfaces = { 'c': conMain, 't': termMain, 'g': guiMain }
	options = { 'icase': False, 'idiac': False, 'interface': 'c',
	            'lexicon': getDefaultLex(), 'exec': [] }
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'cdi:hl:vx:',
	    	('icase', 'idiac', 'interface=', 'help',
			 'lexicon=', 'version', 'exec='))
	except getopt.GetoptError:
		error(BADUSE, USAGE)
	if args:
		error(BADUSE, USAGE)
	for o, a in opts:
		if o in ('-h', '--help'):
			print(SUMMARY + USAGE)
			sys.exit(OK)
		elif o in ('-v', '--version'):
			print(lexVer.DESCRIPTION)
			sys.exit(OK)
		elif o in ('-c', '--icase'):
			options['icase'] = True
		elif o in ('-d', '--idiac'):
			options['idiac'] = True
		elif o in ('-i', '--interface'):
			a = a[0].lower()
			if a not in 'ctg':
				error(BADUSE, USAGE)
			options['interface'] = a[0].lower()
		elif o in ('-l', '--lexicon'):
			options['lexicon'] = a
		elif o in ('-x', '--exec'):
			if options['interface'] != 'c':
				error(BADUSE, _('-x/--exec implies -i/--interface c'))
			options['exec'].append(a)
		else:
			assert False, _('Internal error: Unhandled option')
	interfaces[options['interface']](options)
	sys.exit(OK)

if __name__ == '__main__':
	main()

