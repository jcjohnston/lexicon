#!/usr/bin/env python3
# lexBusy.py - routines to support text-based progress info in lexitron
# jcj 2020-02-07

'''Text-only busyWait function and associated strings'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. Meanwhile...
try:
	pgettext
except NameError:
	from pgettext import pgettext
__ = pgettext

import sys

phaseStrings = __('Progress loading lexicon (5 phases separated by ;)', 
	'Reading...;Normalizing...;Sorting...;Hashing...;Done.').split(';')

_prevPhase = None

def busyWait(phase, percent):
	'''A console-based callable for the lexicon module'''
	global _prevPhase
	if phase != _prevPhase:
		print(phaseStrings[phase], end=' ')
		sys.stdout.flush()
		_prevPhase = phase
	if percent == 100:
		print()

