#!/usr/bin/env python3
# alert.py

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ErrorAlert(Gtk.Window):

	def __init__(self, status, message):

		Gtk.Window.__init__(self)
		if status == 0:
			primaryMessage = 'Warning'
			dialogType = Gtk.MessageType.WARNING
			buttonsType = Gtk.ButtonsType.OK
		else:
			primaryMessage = 'Error'
			dialogType = Gtk.MessageType.ERROR
			buttonsType = Gtk.ButtonsType.CANCEL
		dialog = Gtk.MessageDialog(self, 0, dialogType,
					buttonsType, primaryMessage)
		dialog.format_secondary_text(message)
		dialog.run()
		dialog.destroy()
		#self.destroy()

ErrorAlert(0, 'This is your first warning.')
ErrorAlert(0, 'This is your second warning.')
ErrorAlert(0, 'Now you die (but not really).')

input('Type any key to exit: ')



