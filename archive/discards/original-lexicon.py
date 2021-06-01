#!/usr/bin/env python3
# lexicon.py
# jcj 2018-07-30

'''
Implements a Lexicon class. Instances have methods to check for
membership of a word, words with particular prefixes or suffixes,
anagrams, etc. Can also be used case-insensitively.
'''

import sys
import os.path
import argparse
import bisect
import re
import readline

PROGNAME = os.path.basename(sys.argv[0])
OK, FAIL, BADUSE = 0, 1, 2

class Lexicon:

	DEFAULT_LEXFILE = '/usr/share/dict/words'

	def __init__(self, caseInsensitive=False, lexFile=DEFAULT_LEXFILE):
		'''Initialize a sorted lexicon, with entries all in capitals
		if caseInsensitive is True. The diskfile source is not expected
		to be sorted. Newlines are removed from all entries'''
		try:
			f = open(lexFile)
		except IOError as err:
			error(FAIL, str(error))
		self.words = [ w[:-1] for w in sorted(f.readlines()) ]
		self.caseInsensitive = caseInsensitive
		self.fileName = lexFile
		if self.caseInsensitive:
			# set() is used to eliminate any duplicates created by case-folding
			self.words = sorted(list(set([ w.upper() for w in self.words ])))
		f.close()

	def length(self):
		'''Return the number of entries'''
		return len(self.words)

	def contains(self, word):
		'''Return word itself (possibly case-folded) if present, or None'''
		if self.caseInsensitive:
			word = word.upper()
		i = bisect.bisect_left(self.words, word)
		if i != len(self.words) and self.words[i] == word:
			return self.words[i]
		else:
			return None

	def regex(self, pattern):
		'''Return list of matching words'''
		pattern = re.compile(pattern)
		matches = []
		for word in self.words:
			m = pattern.search(word)
			if m:
				matches.append(word)
		return matches

	def hasPrefix(self, prefix):
		'''Return whether there is any word that begins with prefix'''
		if self.caseInsensitive:
			prefix = prefix.upper()
		# surprisingly, this has quite adequate performance
		for word in self.words:
			if word.startswith(prefix):
				return True
		return False

	def withPrefix(self, prefix):
		'''Return a list of words with prefix'''
		if self.caseInsensitive:
			prefix = prefix.upper()
		return [ w for w in self.words if w.startswith(prefix) ]

	def hasSuffix(self, suffix):
		'''Return whether there is any word that ends with suffix'''
		if self.caseInsensitive:
			suffix = suffix.upper()
		# surprisingly, this has quite adequate performance
		for word in self.words:
			if word.endswith(suffix):
				return True
		return False

	def withSuffix(self, suffix):
		'''Return a list of words with suffix'''
		if self.caseInsensitive:
			suffix = suffix.upper()
		return [ w for w in self.words if w.endswith(suffix) ]

	def anagrams(self, word):
		'''Return a list of anagrams of word'''
		def anagrams_aux(dst, src, found):
			if len(src) == 0:   # base case, all letters used
				result = self.contains(dst)
				if result and result not in found:
					found.append(result)
			else:
				for i in range(len(src)):
					anagrams_aux(dst + src[i], src[:i] + src[i+1:], found)
		if self.caseInsensitive:
			word = word.upper()
		results = []
		anagrams_aux('', word, results)
		return results

def error(status, message):
	'''Print warning or error message to stderr, and exit on error'''
	sys.stderr.write('%s: %s: ' %
				(PROGNAME, 'Warning' if status == OK else 'Error'))
	sys.stderr.write('%s\n' % message)
	if status != OK:
		sys.exit(status)

def help():
	'''Summarize the available commands'''
	print('Commands (The part in upper case, but can be entered in either case):')
	print('Anagrams, Contains, HasPrefix, HasSuffix, WithPrefix, WithSuffix, Regex, Quit')
	
def main():
	'''Perform option and argument processing and file opening and closing'''
	# Parse command line
	parser = argparse.ArgumentParser(prog=PROGNAME, description=__doc__,
					formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-f', '--fold', action='store_true',
					help='match case-insensitively')
	parser.add_argument('-l', '--lexicon', nargs=1, default='/usr/share/dict/words',
					help='specify lexicon file to use')
	args = parser.parse_args()
	lex = Lexicon(args.fold, args.lexicon)
	print(lex.length(), lex.fileName)
	help()
	while True:
		try:
			line = input('@ ')
		except (EOFError, KeyboardInterrupt):
			print()
			line = 'Q'
		words = line.split()
		if not words: continue
		if len(words) != 2:
			if len(words) == 1:
				if words[0] in 'Hh':
					help()
					continue
				elif words[0] in 'Qq':
					break
				else:
					print('! Correct format is command (+ argument)')
					continue
		command = words[0].upper()
		data = words[1]
		if command == 'A':
			print(lex.anagrams(data))
		elif command == 'C':
			print(lex.contains(data))
		elif command == 'HP':
			print(lex.hasPrefix(data))
		elif command == 'HS':
			print(lex.hasSuffix(data))
		elif command == 'WP':
			print(lex.withPrefix(data))
		elif command == 'WS':
			print(lex.withSuffix(data))
		elif command == 'R':
			print(lex.regex(data))
		else:
			print('! Unknown command')
	# Set up files
	sys.exit(OK)

if __name__ == '__main__':
	main()

