#! /usr/bin/env python3
# lexTerm.py -- smart-terminal interface for lexitron
# jcj 2019-07-08

import sys
import lexicon
import textwrap
from error import *
from terminal import *

def interact(lex):

	def resize():
	    nonlocal nrows, xmax, ymax
	    xmax, ymax = scrsize()
	    if ymax < MIN_YMAX or xmax < MIN_XMAX:
	        message('Sorry, terminal must be at least %d x %d characters. ' %
	                (MIN_XMAX, MIN_YMAX))
	        getkey()
	        return False
	    nrows = ymax - 4
	    return True

	def status(s):
	    gotoxy(0, ymax - 2)
	    clreol()
	    display(s[:xmax], BOLD | color(MAGENTA))

	def message(s):
	    gotoxy(0, ymax - 1)
	    clreol()
	    display(s[:xmax], BOLD | color(RED))

	def showAnswer(s):
		# lines should be filled and wrapped
		lines = textwrap.wrap(s, xmax - XOFFSET * 2)
		# need to show a screenful at a time
		pageFull = ymax - 5 - YOFFSET
		length = len(lines)
		start = 0
		while True:
			for i in range(pageFull):
				gotoxy(XOFFSET, YOFFSET + i)
				clreol()
				if start + i < length:
					display(lines[start+i])
			if start + i >= length:
				return
			gotoxy(XOFFSET, YOFFSET+pageFull)
			display('[More] ←↑→↓ <whitespace> eX)it ', BOLD | color(GREEN))
			while True:
				key = getkey()
				if key in finished:
					gotoxy(XOFFSET, YOFFSET + pageFull)
					clreol()
					message('')
					return
				if key in backwards:
					start = max(0, start - pageFull)
					break
				elif key in forwards:
					start = min(length - pageFull, start + pageFull)
					break


	# Initialize key bindings
	forwards = {KEY_RIGHT, KEY_DOWN, KEY_PGDN, KEY_END,
	            ord(' '), ord('\t'), ord('\n'), ord('\r')}
	backwards = {127, KEY_LEFT, KEY_UP, KEY_PGUP, KEY_HOME, KEY_BS, KEY_DEL}
	finished = { ord('X'), ord('x') }

	# Initialize window dimensions
	MIN_YMAX = 24
	MIN_XMAX = 70
	NCOLS = 16
	XOFFSET = 8
	YOFFSET = 2
	xmax = ymax = nrows = 0
	if not resize(): return

	# Initialize key -> (prompt, method) mappings
	cmdMap = { 'C': ('Contains', lex.contains),
			   'P': ('With prefix', lex.withPrefix),
			   'S': ('With suffix', lex.withSuffix),
			   'R': ('Regex', lex.regex),
			   'A': ('Anagrams', lex.anagrams),
			 }

	# Interactive loop
	banner = '— LEXITRON —'
	gotoxy(xmax // 2 - len(banner) // 2 - 1, 0)
	display(banner, BOLD | color(CYAN))
	while True:
		status('File: %s (%s entries)' % (lex.fileName,
			format(lex.length(), ',d')))
		message('C)ontains, withP)refix, withS)uffix, R)egex, A)nagrams, Q)uit: ')
		ch = chr(getkey()).upper()
		if ch == 'Q':
			return
		elif ch not in 'CPSRA':
			continue
		message(cmdMap[ch][0] + ': ')
		string = getstr().strip()
		if not string:
			continue
		answer = cmdMap[ch][1](string)
		if isinstance(answer, list):
			answer = ' '.join(answer)
		if not answer:
			answer = '[None]'
		showAnswer(answer)

def termMain(fileName, caseBlind=False, diacBlind=False, cmds=None):
	prevMessage = ''
	def busyWait(percent, message):
		nonlocal prevMessage
		if message != prevMessage:
			print(message, end=' ')
			prevMessage = message
		sys.stdout.flush()
		if percent == 100:
			print()
	try:
		lex = lexicon.Lexicon(fileName, caseBlind, diacBlind, busyWait)
	except lexicon.LexiconError as err:
		error(FAIL, str(err))		
	termwrap(interact, lex)
	sys.exit(OK)

def main():
	print('This module is part of the lexitron package.')
	print('It is not intended to be used stand-alone.')

if __name__ == '__main__':
	main()

