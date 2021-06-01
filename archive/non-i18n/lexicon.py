#!/usr/bin/env python3
# lexicon.py jcj 2019-02-20, 2020-01-23

'''A class to implement a lexicon with methods for prefixes and suffixes,
regular expressions, anagrams, etc'''

import bisect
import re
import unicodedata as ud
from collections import defaultdict

INTERVAL = 5   # How often in % is progress notified?
PASSES = 4   # How many times is each entry processed?

class LexiconError(Exception):
	pass

class Lexicon:

	def __init__(self, fileName, caseBlind=False, diacBlind=False, busyWait=None):
		'''Initialize an object representing a lexicon from a disk file
		consisting of one entry per line (unique but not necessarily sorted)
		with possible comment lines beginning with a hash sign.
		Methods are provided for lookup, with possible disregard of
		case and/or diacritics, of whole words, prefixes, suffixes,
		regular expressions, and anagrams. Lookup of whole words and anagrams
		is optimized.  Provision is made for callback to an optional
		function or method to display progress information.'''
		self.fileName = fileName
		self.caseBlind = caseBlind
		self.diacBlind = diacBlind
		if not busyWait:
			busyWait = lambda percent, message: None
		self.words = []                  # list of sorted, normalized words
		self.refs = defaultdict(list)    # dict from normalized words
		                                 # to lists of reference forms
										 # eg POLISH -> [Polish, polish]
		self.anags = defaultdict(list)   # dict from normalized anagrams
		                                 # to lists of anagrammatic forms
										 # eg abeert -> [beater, berate, rebate]
		try:
			f = open(fileName)
		except Exception as err:
			raise LexiconError(err)
		busyWait(0, 'Reading...')
		# Read in a list of lines, without showing any progress.
		# But then use the number of words read in to time progress updates
		lines = [ line.rstrip('\n') for line in f.readlines()
					if not line.startswith('#') ]
		self.numLines = len(lines)
		pcPerLine = 100 / (self.numLines * PASSES)   # NB result is a real
		pcDone = pcPerLine * self.numLines   # for the read itself
		# build dict of normalized forms in self.refs
		busyWait(round(pcDone), 'Normalizing...')
		for line in lines:
			pcDone += pcPerLine
			if pcDone % INTERVAL < pcPerLine:
				busyWait(round(pcDone), 'Normalizing...')
			self.refs[self.normalized(line, caseBlind, diacBlind)].append(line)
		# build sorted list of normalized word forms for lookup
		busyWait(round(pcDone), 'Sorting...')
		self.words = sorted(self.refs)   # includes only the keys
		pcDone += pcPerLine * self.numLines
		# build a separate dictionary of normalized anagram forms
		busyWait(round(pcDone), 'Hashing...')
		for line in lines: 
			pcDone += pcPerLine
			if pcDone % INTERVAL < pcPerLine:
				busyWait(round(pcDone), 'Hashing...')
			hash = self.anagramHash(line)
			self.anags[hash].append(line)
		busyWait(100, 'Done.')
		f.close()
	
	def normalized(self, s, caseBlind, diacBlind):
		'''Apply needed transformations to ignore case and/or accents'''
		if caseBlind:
			s = s.upper()
		if diacBlind:
			s = ud.normalize('NFKD', s)
			s = ''.join([c for c in s if not ud.combining(c)])
		return s
		
	def length(self):
		'''Return the number of entries'''
		return self.numLines

	def anagramHash(self, s):
		'''Create a unique hash for anagram purposes, ignoring
		order, letter-case, and all punctuation. Diacritics
		are ignored only if self.diacBlind is set'''
		# Unfortunately the \w class (Unicode 'word' characters)
		# includes the underscore, so _ must be special-cased
		s = s.replace('_', '')
		# Upper-case the string, remove all characters which are not \w,
		# and sort the result: thus all anagrammatic strings get the same hash
		return ''.join(sorted(re.sub(r'\W', '',
						self.normalized(s, True, self.diacBlind))))

	def contains(self, word):
		'''Return a list of matching words'''
		word = self.normalized(word, self.caseBlind, self.diacBlind)
		i = bisect.bisect_left(self.words, word)
		if i != len(self.words) and self.words[i] == word:
			return self.refs[word]
		else:
			return []

	def regex(self, pattern):
		'''Return list of matching words'''
		# we can normalize case but we can't do anything about diacritics
		flags = re.IGNORECASE if self.caseBlind else 0
		pattern = re.compile(pattern, flags)
		matches = []
		for word in self.words:
			m = pattern.search(word)
			if m:
				matches.extend(self.refs[word])
		return matches

	def hasPrefix(self, prefix):
		'''Return whether there is any word that begins with prefix'''
		prefix = self.normalized(prefix, self.caseBlind, self.diacBlind) 
		for word in self.words:
			if word.startswith(prefix):
				return True
		return False

	def withPrefix(self, prefix):
		'''Return a list of words with prefix'''
		prefix = self.normalized(prefix, self.caseBlind, self.diacBlind)
		return [ ' '.join(self.refs[w]) for w in self.words
					if w.startswith(prefix) ]

	def hasSuffix(self, suffix):
		'''Return whether there is any word that ends with suffix'''
		suffix = self.normalized(suffix, self.caseBlind, self.diacBlind)
		if self.caseBlind:
			suffix = suffix.upper()
		for word in self.words:
			if word.endswith(suffix):
				return True
		return False

	def withSuffix(self, suffix):
		'''Return a list of words with suffix'''
		suffix = self.normalized(suffix, self.caseBlind, self.diacBlind)
		return [ ' '.join(self.refs[w]) for w in self.words
					if w.endswith(suffix) ]


	def anagrams(self, word):
		'''Return a list of anagrams of word, ignoring case and punctuation''' 
		return self.anags.get(self.anagramHash(word), [])

def main():
	print('This module is intended to be imported rather than run standalone.')
	print('Use as "import lexicon" or "from lexicon import Lexicon, LexiconError".')

if __name__ == '__main__':
	main()

