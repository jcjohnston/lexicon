#!/usr/bin/env python3

import curses
import time
_stdscr = None

def terminit():
    '''Initialize _stdscr in the standard way'''
    global _stdscr
    _stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()
    for color in range(1, 8):
        curses.init_pair(color, color, -1)
    _stdscr.keypad(1)

def termend():
    '''Restore the screen'''
    global _stdscr
    _stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    _stdscr = None

def test():
	while True:
		k = _stdscr.getch()
		_stdscr.addstr('%d\n' % k)
		_stdscr.refresh()
		if k == 27:
			time.sleep(3)
			return


def main():
	terminit()
	test()
	termend()

if __name__ == '__main__':
	main()
