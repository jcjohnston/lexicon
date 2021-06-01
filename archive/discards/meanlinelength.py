#!/usr/bin/env python3
# meanlinelength.py
# jjohnston 2019-05-28

'''
Compute the mean line length of the input files.
Originally intended for dictionary files, to get mean word length.
'''

import sys
import os.path
import argparse

PROGNAME = os.path.basename(sys.argv[0])
OK, FAIL, BADUSE = 0, 1, 2

def error(status, message):
	'''Print warning or error message to stderr, and exit on error'''
	sys.stderr.write('%s: %s: ' %
				(PROGNAME, 'Warning' if status == OK else 'Error'))
	sys.stderr.write('%s\n' % message)
	if status != OK:
		sys.exit(status)

def process(infile):
	'''Perform the functionality of the script'''
	for lno, line in enumerate(infile):
		lno += 1
		sys.stdout.write('%5d: %s' % (lno, line))

def main():
	'''Perform option and argument processing and file opening and closing'''
	# Parse command line
	parser = argparse.ArgumentParser(prog=PROGNAME, description=__doc__)
	parser.add_argument('filename', nargs='*',
					help='file to process, default: standard input')
	args = parser.parse_args()
	nchars = 0
	nlines = 0
	# Set up files
	if not args.filename:
		args.filename = ['-']
	for filename in args.filename:
		if filename == '-':
			infile = sys.stdin
		else:
			try:
				infile = open(filename, 'r')		
			except Exception as err:
				error(FAIL, str(err))
		# Do the thing
		lines = [ line[:-1] for line in infile.readlines() ]
		nlines += len(lines)
		for line in lines:
			nchars += len(line)
		if infile is not sys.stdin:
			infile.close()
	mean = nchars / nlines
	print('%f non-newline characters per line' % mean)
	# Any cleanup needed
	sys.exit(OK)

if __name__ == '__main__':
	main()

