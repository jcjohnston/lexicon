#!/usr/bin/env python3

import sys
from gi.repository import Gtk

if sys.argv:
	print('Console program!')
else:
	win = Gtk.Window(title='A Window')
	win.connect('destroy', Gtk.main_quit)
	win.show_all()
	Gtk.main()

