# gui.py - jcj 2019-02-20

'''
GTK-based GUI for lexicon
'''

import sys
from lexicon import Lexicon, LexiconError
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

MENU_XML = '''
<?xml version="1.0" encoding="UTF-8"?>
<interface>
	<menu id='app-menu'>
		<section>
			<item>
				<attribute name='action'>app.about</attribute>
				<attribute name='label'>About...</attribute>
			</item>
		</section>
		<section>
			<item>
				<attribute name='action'>app.quit</attribute>
				<attribute name='label'>Quit</attribute>
			</item>
		</section>
	</menu>
</interface>
'''

class LexWindow(Gtk.ApplicationWindow):

	'''A window and associated controls to provide a GTK-based
	graphical user interface for the lexicon tool'''

	action = 'contains'      # the current action to be performed
	lex = None               # the current Lexicon object
	lexInfo = ''             # string describing the current lexicon
	caseInsensitive = None   # whether lexicon opened in case-insensitive mode
	entryField = None        # the Entry object that the user types into
	answers = None           # the ScrolledWindow/TextView containing the answers

	def __init__(self, title, lex, *args, **kwargs):

		# the outer window
		Gtk.ApplicationWindow.__init__(self, title=title, *args, **kwargs)
		self.set_border_width(10)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.connect('destroy', self.closeWindow)

		# a vertical box which will contain the main sections
		vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 5)
		self.add(vBox)

		# top section - file details
		hBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 5)
		self.lexInfo = Gtk.Label()
		self.lexInfo.set_justify(Gtk.Justification.LEFT)
		self.lexInfo.set_alignment(0, 0)
		button = Gtk.Button('Change Lexicon')
		button.connect('clicked', self.onChangeLexiconClicked)
		hBox.pack_start(self.lexInfo, True, True, 0)
		hBox.pack_end(button, True, True, 0)
		vBox.pack_start(hBox, True, True, 0)

		# next - case sensitivity
		grid = Gtk.Grid()
		grid.set_column_spacing(5)
		self.caseInsensitive = Gtk.CheckButton()
		self.caseInsensitive.connect('toggled', self.onCaseInsensitiveToggled)
		label = Gtk.Label('Case-insensitive matching')
		label.set_alignment(0, 0.5)
		grid.attach(self.caseInsensitive, 0, 0, 1, 1)
		grid.attach(label, 1, 0, 1, 1)
		vBox.pack_start(grid, True, True, 0)

		# box containing a label and an entry field
		hBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 5)
		label = Gtk.Label('Text or pattern:')
		label.set_alignment(0, 0.5)
		self.entryField = Gtk.Entry()
		self.entryField.set_width_chars(50)
		self.entryField.connect('activate', self.performAction)
		#self.entryField.connect('activate', self.clearAnswers)
		hBox.pack_start(label, True, True, 0)
		hBox.pack_end(self.entryField, True, True, 0)
		vBox.pack_start(hBox, True, True, 0)

		# box containing a group of radio buttons for selecting actions
		hBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 5)
		containsButton = Gtk.RadioButton.new_with_label_from_widget(None,
			'Contains')
		containsButton.connect('toggled', self.onButtonToggled, 'contains')
		hBox.pack_start(containsButton, True, True, 0)
		regexButton = Gtk.RadioButton.new_with_label_from_widget(containsButton,
			'Regex')
		regexButton.connect('toggled', self.onButtonToggled, 'regex')
		hBox.pack_start(regexButton, True, True, 0)
		prefixButton = Gtk.RadioButton.new_with_label_from_widget(regexButton,
			'With Prefix')
		prefixButton.connect('toggled', self.onButtonToggled, 'prefix')
		hBox.pack_start(prefixButton, True, True, 0)
		suffixButton = Gtk.RadioButton.new_with_label_from_widget(prefixButton,
			'With Suffix')
		suffixButton.connect('toggled', self.onButtonToggled, 'suffix')
		hBox.pack_start(suffixButton, True, True, 0)
		anagramsButton = Gtk.RadioButton.new_with_label_from_widget(suffixButton,
			'Anagrams')
		anagramsButton.connect('toggled', self.onButtonToggled, 'anagrams')
		hBox.pack_start(anagramsButton, True, True, 0)
		vBox.pack_start(hBox, True, True, 0)

		# bottom section - a scrollable viewing pane
		scrolledWindow = Gtk.ScrolledWindow()
		scrolledWindow.set_hexpand(False)
		scrolledWindow.set_vexpand(True)
		scrolledWindow.set_size_request(-1, 100)
		textView = Gtk.TextView()
		textView.set_wrap_mode(Gtk.WrapMode.WORD)
		textView.set_editable(False)
		self.answers = textView.get_buffer()
		scrolledWindow.add(textView)
		vBox.pack_start(scrolledWindow, True, True, 0)

		# now update the top parts to reflect the current lexicon
		self.lex = lex
		self.updateLexInfo()

	def updateLexInfo(self):
		self.lexInfo.set_markup('Lexicon: <b>%s</b>\nLength:  <b>%d</b>' % 
								(self.lex.fileName, self.lex.length()))
		self.caseInsensitive.set_active(self.lex.caseInsensitive)

	def onCaseInsensitiveToggled(self, widget):
		'''This requires the lexicon to be re-loaded'''
		self.lex = Lexicon(self.caseInsensitive.get_active(), self.lex.fileName)

	def performAction(self, widget):
		actions = { 'contains': self.lex.contains, 'regex': self.lex.regex, 
		            'prefix': self.lex.withPrefix, 'suffix': self.lex.withSuffix,
					'anagrams': self.lex.anagrams }
		answer = actions[self.action](self.entryField.get_text())
		if isinstance(answer, list): answer = ' '.join(answer)
		if not answer: answer = '[None]'
		self.answers.set_text(answer)

	def onButtonToggled(self, widget, name):
		self.action = name
		self.entryField.grab_focus()

	def error(self, status, message):
		if status == 0:
			primaryMessage = 'WARNING'
			messageType = Gtk.MessageType.WARNING
		else:
			primaryMessage = 'ERROR'
			message = Gtk.MessageType.ERROR
		dialog = Gtk.MessageDialog(self, 0, messageType,
					Gtk.ButtonsType.OK, primaryMessage)
		dialog.format_secondary_text(message)
		dialog.run()
		dialog.destroy()

	def onChangeLexiconClicked(self, widget):
		dialog = Gtk.FileChooserDialog('Select a lexicon file', self,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			'Select', Gtk.ResponseType.OK))
		dialog.set_default_size(800, 400)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			try:
				lex = Lexicon(False, dialog.get_filename())
			except Exception as err:
				self.error(0,
					"There was a problem using the chosen lexicon file:\n%s"
					% str(err))
			else:
				self.lex = lex
				self.updateLexInfo()
		dialog.destroy()

	def closeWindow(self, window):
		self.close()
		#sys.exit(0)

class Application(Gtk.Application):

	def __init__(self, title, lex, *args, **kwargs):
		super().__init__(*args, application_id="org.example.myapp",
					flags=Gio.ApplicationFlags.FLAGS_NONE,
					**kwargs)
		self.window = None
		self.title = title
		self.lex = lex

	def do_startup(self):
		Gtk.Application.do_startup(self)

		action = Gio.SimpleAction.new('about', None)
		action.connect('activate', self.onAbout)
		self.add_action(action)

		action = Gio.SimpleAction.new('quit', None)
		action.connect('activate', self.onQuit)
		self.add_action(action)

		builder = Gtk.Builder.new_from_string(MENU_XML, -1)
		self.set_app_menu(builder.get_object('app-menu'))

	def do_activate(self):
		if not self.window:
			self.window = LexWindow(self.title, self.lex, application=self)
			self.add_window(self.window)
		self.window.show_all()

	def onAbout(self, action, param):
		aboutDialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
		aboutDialog.present()

	def onQuit(self, action, param):
		self.quit()

def guiMain(lex):	
		app = Application('Lexicon Tool', lex)
		app.run(None)

