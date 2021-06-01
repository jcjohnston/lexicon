#! /usr/bin/env python3
# lexCon.py -- console interface for lexitron
# jcj 2019-07-04

import sys
import shutil
import textwrap
import readline   # the mere import itself gives readline functionality
from error import *
import lexicon

PROMPT = '» '

def help():
	'''Summarize the available commands'''
	print('H)elp, C)ontains, P)refix, S)uffix, R)egex, A)nagrams, Q)uit')

def show(answer):
	'''Display answer, wrapping text if necessary'''
	if not answer:
		print('[None]')
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
		raise ValueError
	command = words[0][0].upper()
	data = ' '.join(words[1:])
	if command == 'A':
		show(lex.anagrams(data))
	elif command == 'C':
		show(lex.contains(data))
	elif command == 'P':
		show(lex.withPrefix(data))
	elif command == 'S':
		show(lex.withSuffix(data))
	elif command == 'R':
		show(lex.regex(data))
	else:
		print('! Unknown command')

	
def repl(lex):
	'''Perform a console-based REPL'''
	print('%s (%s)' % (lex.fileName, format(lex.length(), ',d')))
	help()
	while True:
		try:
			line = input(PROMPT)
		except (EOFError, KeyboardInterrupt):
			print()
			line = 'Q'
		line = line.strip()
		if not line: continue
		if line[0] in 'Hh':
			help()
			continue
		elif line[0] in 'Qq':
			break
		doCommand(lex, line)
		
def conMain(fileName, caseBlind=False, diacBlind=False, cmds=None):
	prevMessage = ''
	def busyWait(percent, message):
		nonlocal prevMessage
		if message != prevMessage:
			print(message, end=' ')
			sys.stdout.flush()
			prevMessage = message
		if percent == 100:
			print()
	try:
		lex = lexicon.Lexicon(fileName, caseBlind, diacBlind, None if cmds else busyWait)
	except lexicon.LexiconError as err:
		error(FAIL, str(err))		
	if cmds:
		for cmd in cmds:
			doCommand(lex, cmd)
	else:
		repl(lex)
	sys.exit(OK)

def main():
	print('This module is part of the lexitron package.')
	print('It is not intended to be used stand-alone.')

if __name__ == '__main__':
	main()

