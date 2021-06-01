#! /usr/bin/env python3
# lexCon.py -- console interface for lexitron
# jcj 2019-07-04, 2020-02-11

'''
Pure command-line and dumb-console interfaces for lexitron
'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. So...
try:
	pgettext
except NameError:
	from pgettext import pgettext
__ = pgettext

import sys
import shutil
import textwrap
import readline   # the mere import itself gives readline functionality
from error import *

import lexicon
import lexVer
from lexBusy import busyWait

def help():
	'''Summarize the available commands'''
	print(__('Menu of distinct single-keypress choices. Use the given format '
	         'if possible, eg C)hoice, otherwise the format K=Choice',
	         'H)elp, C)ontains, P)refix, S)uffix, R)egex, A)nagrams, Q)uit'))

def show(answer):
	'''Display answer, wrapping text if necessary'''
	if not answer:
		print(__('No matching entries', '[None]'))
	elif isinstance(answer, list):
		rows, _ = shutil.get_terminal_size()
		lines = textwrap.wrap(' '.join(answer))
		for line in lines:
			print(line)
	else:
		print(answer)

def doCommand(lex, s):
	'''From either repl or command line, parse and execute the command'''
	words = s.split()
	if len(words) < 2:
		print(_('! Commands require at least one argument'))
		return
	command = words[0][0].upper()
	data = ' '.join(words[1:])
	if command == __('Keypress: A)nagrams', 'A'):
		show(lex.anagrams(data))
	elif command == __('Keypress: C)ontains', 'C'):
		show(lex.contains(data))
	elif command == __('Keypress: P)refix', 'P'):
		show(lex.withPrefix(data))
	elif command == __('Keypress: S)uffix', 'S'):
		show(lex.withSuffix(data))
	elif command == __('Keypress: R)egex', 'R'):
		show(lex.regex(data))
	else:
		print(_('! Unknown command'))

def repl(lex):
	'''Perform a console-based REPL'''
	PROMPT = '» '
	print(_('{fileName} ({fileLength:,d})').format
	      (fileName=lex.fileName, fileLength=lex.length()))
	help()
	while True:
		try:
			line = input(PROMPT)
		except (EOFError, KeyboardInterrupt):
			print()
			line = __('Keypress: Q)uit', 'Q')
		line = line.strip()
		if not line: continue
		if line[0] in __('Keypress: H)elp', 'Hh'):
			help()
			continue
		elif line[0] in __('Keypress: Q)uit', 'Qq'):
			break
		doCommand(lex, line)
		
def conMain(options):
	fileName = options['lexicon']
	caseBlind, diacBlind = options['icase'], options['idiac']
	cmds = options['exec']
	try:
		lex = lexicon.Lexicon(fileName, caseBlind, diacBlind,
		                      None if cmds else busyWait)
	except lexicon.LexiconError as err:
		error(FAIL, str(err))		
	if cmds:
		for cmd in cmds:
			doCommand(lex, cmd)
	else:
		repl(lex)
	sys.exit(OK)

def main():
	print(_('This module is part of the {programName} package.\n'
	        'It is not intended to be used stand-alone.').format
			(programName=lexVer.NAME))

if __name__ == '__main__':
	main()

