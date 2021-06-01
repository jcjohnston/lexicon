#! /usr/bin/env python3
# lexTerm.py -- smart-terminal interface for lexitron
# jcj 2019-07-08, 2020-02-11

'''A VT-100-style smart-terminal interface for lexitron'''

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
import textwrap
from error import *
from terminal import *

import lexicon
import lexVer
from lexBusy import busyWait

def interact(lex):

	def resize():
	    nonlocal nrows, xmax, ymax
	    xmax, ymax = scrsize()
	    if ymax < MIN_YMAX or xmax < MIN_XMAX:
	        message(_('Sorry, terminal must be at least '
			          '{min_horiz} x {min_vert} characters. ').format
			         (min_horiz=MIN_XMAX, min_vert=MIN_YMAX))
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
			display(__('Menu of distinct single-keypress choices available '
			           'to the user to see More matching entries. <whitespace> '
					   'includes the spacebar, the tab key, and Enter/Return.',
					   '[More] ←↑→↓ <whitespace> eX)it '), BOLD | color(GREEN))
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
	finished = { ord(__('Keypress: eX)it', 'X')),
	             ord(__('Keypress: eX)it', 'x')) }

	# Initialize window dimensions
	MIN_YMAX = 24
	MIN_XMAX = 70
	NCOLS = 16
	XOFFSET = 8
	YOFFSET = 2
	xmax = ymax = nrows = 0
	if not resize(): return

	# Initialize key -> (prompt, method) mappings
	cmdMap = { __('Keypress: Contains', 'C'): (_('Contains'), lex.contains),
			   __('Keypress: Prefix', 'P'): (_('Prefix'), lex.withPrefix),
			   __('Keypress: Suffix', 'S'): (_('Suffix'), lex.withSuffix),
			   __('Keypress: Regex', 'R'): (_('Regex'), lex.regex),
			   __('Keypress: Anagrams', 'A'): (_('Anagrams'), lex.anagrams),
			 }

	# Interactive loop
	banner = '— {programName} —'.format(programName=lexVer.NAME.upper())
	gotoxy(xmax // 2 - len(banner) // 2 - 1, 0)
	display(banner, BOLD | color(CYAN))
	while True:
		status(_('File: {file_name} ({number_of_entries:,d} entries)').format
		        (file_name=lex.fileName, number_of_entries=lex.length()))
		message(__('Menu of distinct single-keypress choices. Use the given format '
		           'if possible, eg C)hoice, otherwise the format K=Choice.',
		           'C)ontains, P)refix, S)uffix, R)egex, A)nagrams, Q)uit: '))
		ch = chr(getkey()).upper()
		if ch == __('Keypress: Q)uit', 'Q'):
			return
		elif ch not in __('Keypress: C)ontains, P)refix, S)uffix, R)egex, A)nagrams '
		                  'in that order.', 'CPSRA'):
			continue
		message(cmdMap[ch][0] + ': ')
		string = getstr().strip()
		if not string:
			continue
		answer = cmdMap[ch][1](string)
		if isinstance(answer, list):
			answer = ' '.join(answer)
		if not answer:
			answer = __('No matching entries', '[None]')
		showAnswer(answer)

def termMain(options):
	fileName = options['lexicon']
	caseBlind, diacBlind = options['icase'], options['idiac']
	try:
		lex = lexicon.Lexicon(fileName, caseBlind, diacBlind, busyWait)
	except lexicon.LexiconError as err:
		error(FAIL, str(err))		
	termwrap(interact, lex)
	sys.exit(OK)

def main():
	print(_('This module is part of the {programName} package.\n'
	        'It is not intended to be used stand-alone.').format
			(programName=lexVer.NAME))


if __name__ == '__main__':
	main()

