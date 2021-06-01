#!/usr/bin/env python3
# lexVer.py - program descriptions for lexitron project
# jcj 2020-02-06, 2020-02-11

'''
Informative strings about lexitron
'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. Meanwhile...
try:
	pgettext
except NameError:
	from pgettext import pgettext
__ = pgettext

# These strings are not to be translated
NAME = 'Lexitron'
VERSION = 'v0.9'
COPYRIGHT = '(c) 2020 Jason C Johnston'
DESCRIPTION = '%s %s %s' % (NAME, VERSION, COPYRIGHT)

def main():
	print(_('This module is part of the {programName} package.\n'
	        'It is not intended to be used stand-alone.').format
			(programName=NAME))

if __name__ == '__main__':
	main()

