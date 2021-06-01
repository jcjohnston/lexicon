#!/usr/bin/env python3
# lexGui.py - GUI written in Qt for Lexitron
# jcj 2019-02-27, 2019-04-23, 2019-11-20, 2020-02-11

'''
PyQt-based graphical user interface for lexitron
'''

## Support for gettext
# This file assumes that _ and pgettext have been injected
# into the builtins namespace by the '__main__' file.
# Python doesn't support pgettext until version 3.8. So...
try:
	pgettext
except NameError:
	from pgettext import pgettext
__ = pgettext

import lexicon
import lexVer
from lexBusy import phaseStrings

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from PyQt5.QtCore import QTimer, QEventLoop

# Labels used more than once
LBL_CUT = __('Menu|Edit', 'Cu&t')
LBL_COPY = __('Menu|Edit', '&Copy')
LBL_PASTE = __('Menu|Edit', '&Paste')
LBL_SELECT_ALL = __('Menu|Edit', 'Select &All')
LBL_WORD = __('Button Group 1', '&Word')
LBL_REGEX = __('Button Group 1', '&Regex')
LBL_WITH_PREFIX = __('Button Group 1', '&Prefix')
LBL_WITH_SUFFIX = __('Button Group 1', '&Suffix')
LBL_ANAGRAMS = __('Button Group 1', '&Anagrams')

class MainWindow(QMainWindow):

	def __init__(self, title, fileName, caseBlind=False, diacBlind=False):

		super().__init__()
		self.title = title
		self.fileName = fileName
		self.caseBlind = caseBlind
		self.diacBlind = diacBlind
		self.lex = None 
		self.action = None

		# set title (and size if desired)
		self.setWindowTitle(self.title)
		# create a vertical box to add things to
		self.vBox = QVBoxLayout()
		self.vBox.setSpacing(0)
		# add widgets to the vBox in a helper function
		self.addWidgets()
		container = QWidget()
		container.setLayout(self.vBox)
		self.setCentralWidget(container)
		# add a menubar
		self.addMenuBar()
		# centre the window on the screen
		screenSize = QDesktopWidget().screenGeometry()
		mySize = self.geometry()
		hpos = (screenSize.width() - mySize.width()) / 2
		vpos = (screenSize.height() - mySize.height()) / 2
		self.move(hpos, vpos)
		self.show()
		# load a lexicon
		self.loadLexicon(self.fileName, self.caseBlind, self.diacBlind)
		# after each event, we re-set the focus to the entry field
		# and select all the text within it
		self.resetFocusAndSelection()

	
	def addWidgets(self):

		# at top: label identifying lexicon,
		# with Change Lexicon button at the right
		container = QWidget()
		grid = QGridLayout()
		self.lexLabel = QLabel(self)
		self.updateLexInfo()
		changeButton = QPushButton(__('Button', 'Change &Lexicon'), self)
		changeButton.clicked.connect(self.onChangeLexicon)
		# a pop-up progress bar
		self.progressBar = QProgressBar(self)
		self.progressBar.setGeometry(0, 0, 75, 10)
		self.progressBar.setMinimum(0)
		# for an infinite progress bar, set maximum to 0
		self.progressBar.setMaximum(100)
		self.progressBar.hide()
		# a checkbox for case-insensitive matching
		caseBlindCheckBox = QCheckBox(__('Checkbox', 'Ignore &Case'), self)
		caseBlindCheckBox.setChecked(self.caseBlind)
		caseBlindCheckBox.stateChanged.connect(self.oncaseBlindChanged)
		# a checkbox for diacritic-blind matching
		diacBlindCheckBox = QCheckBox(__('Checkbox', 'Ignore &Diacritics'), self)
		diacBlindCheckBox.setChecked(self.diacBlind)
		diacBlindCheckBox.stateChanged.connect(self.ondiacBlindChanged)
		# pack them all in
		grid.addWidget(self.lexLabel, 0, 0)
		grid.addWidget(changeButton, 0, 1)
		grid.addWidget(self.progressBar, 1, 0)
		grid.addWidget(caseBlindCheckBox, 2, 0)
		grid.addWidget(diacBlindCheckBox, 2, 1)
		container.setLayout(grid)
		self.vBox.addWidget(container)

		# next: an edit box with a label
		container = QWidget()
		hBox = QHBoxLayout()
		label = QLabel(__('Text label', 'String or pattern: '), self)
		self.entryBox = QLineEdit()
		self.entryBox.returnPressed.connect(self.onEnter)
		hBox.addWidget(label)
		hBox.addWidget(self.entryBox)
		container.setLayout(hBox)
		self.vBox.addWidget(container)

		# next: a group of radio buttons
		container = QWidget()
		hBox = QHBoxLayout()
		button1 = QRadioButton(LBL_WORD, container)
		button1.toggled.connect(self.onToggle)
		button2 = QRadioButton(LBL_REGEX, container)
		button2.toggled.connect(self.onToggle)
		button3 = QRadioButton(LBL_WITH_PREFIX, container)
		button3.toggled.connect(self.onToggle)
		button4 = QRadioButton(LBL_WITH_SUFFIX, container)
		button4.toggled.connect(self.onToggle)
		button5 = QRadioButton(LBL_ANAGRAMS, container)
		button5.toggled.connect(self.onToggle)
		button1.setChecked(True)
		hBox.addWidget(button1)
		hBox.addWidget(button2)
		hBox.addWidget(button3)
		hBox.addWidget(button4)
		hBox.addWidget(button5)
		container.setLayout(hBox)
		self.vBox.addWidget(container)

		# finally, a TextEdit field to display the results
		self.results = QTextEdit()
		self.results.setReadOnly(True)
		self.results.setLineWrapMode(self.results.WidgetWidth)
		self.results.resize(200, 75)
		self.vBox.addWidget(self.results)

	def addMenuBar(self):

		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu(__('Menu', '&File'))
		editMenu = menuBar.addMenu(__('Menu', '&Edit'))
		helpMenu = menuBar.addMenu(__('Menu', '&Help'))

		# File menu
		quitAction = QAction(__('Menu|File', '&Quit'), self)
		quitAction.setShortcut('Ctrl+Q')
		quitAction.triggered.connect(self.close)
		fileMenu.addAction(quitAction)
		self.addAction(quitAction)   # see note at bottom re this and all
		                             # following self.addAction calls

		# NB re the four basic editing actions:
		# These, including their standard shortcuts, appear to be implemented by
		# PyQt5 itself, at least for the QLineEdit and QTextEdit widgets, so
		# that these menu entries are, strictly-speaking, more or less redundant.
		# However, the working (non-standard) Alt+Letter accelerators show that
		# the menu entries are independently effective.

		# Edit menu
		cutAction = QAction(LBL_CUT, self)
		cutAction.setShortcut('Ctrl+X')
		cutAction.triggered.connect(self.onEdit)
		editMenu.addAction(cutAction)
		self.addAction(cutAction)

		copyAction = QAction(LBL_COPY, self)
		copyAction.setShortcut('Ctrl+C')
		copyAction.triggered.connect(self.onEdit)
		editMenu.addAction(copyAction)
		self.addAction(copyAction)

		pasteAction = QAction(LBL_PASTE, self)
		pasteAction.setShortcut('Ctrl+V')
		pasteAction.triggered.connect(self.onEdit)
		editMenu.addAction(pasteAction)
		self.addAction(pasteAction)

		editMenu.addSeparator()

		selectAllAction = QAction(LBL_SELECT_ALL, self)
		selectAllAction.setShortcut('Ctrl+A')
		selectAllAction.triggered.connect(self.onEdit)
		editMenu.addAction(selectAllAction)
		self.addAction(selectAllAction)

		# Help menu

		aboutAction = QAction(__('Menu|Help', '&About {programTitle}...').format
		                        (programTitle=self.title), self)
		aboutAction.triggered.connect(self.about)
		helpMenu.addAction(aboutAction)

	def resetFocusAndSelection(self):
		self.entryBox.setFocus()
		self.entryBox.selectAll()
	
	def loadLexicon(self, fileName, caseBlind=False, diacBlind=False):
		try:
			newLex = lexicon.Lexicon(fileName, caseBlind, diacBlind, self.busyWait)
		except lexicon.LexiconError as err:
			self.errorAlert(_('Could not load lexicon: "{errorMessage}"').format
			                 (errorMessage=str(err)))
		else:
			self.lex = newLex
			self.fileName = fileName
			self.caseBlind = caseBlind
			self.diacBlind = diacBlind
		self.updateLexInfo()

	def updateLexInfo(self):
		if self.lex:
			self.lexLabel.setText(
				_('File: {fileName}\nLength: {numEntries:,d} entries').format
					(fileName=self.lex.fileName, numEntries=self.lex.length()))
		else:
			self.lexLabel.setText(_('[No file, no entries]\n'))

	def about(self):
		QMessageBox.about(self,
			__('MessageBox Title', 'About {programName}').format
				(programName=lexVer.NAME), lexVer.DESCRIPTION);
	
	def errorAlert(self, message):
		QMessageBox.warning(self, __('MessageBox Title', 'Warning'), message)
		self.resetFocusAndSelection()

	def busyWait(self, phase, percent):
		self.lexLabel.setText(
			_('File: {fileName}\n{progressPhase}').format
				(fileName=self.lex.fileName if self.lex else
					__('Reading lexicon file', '[Loading]'),
						progressPhase=phaseStrings[phase]))
		QCoreApplication.processEvents()
		if percent == 0:
			self.progressBar.show()
		self.progressBar.setValue(percent)
		QCoreApplication.processEvents()
		# delay a little to show completion
		if percent == 100:
			loop = QEventLoop()
			QTimer.singleShot(500, loop.quit)
			loop.exec()
			self.progressBar.hide()

	@pyqtSlot()
	def onChangeLexicon(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,
					__('File-selection dialog', 'Select lexicon file'), '',
					__('File-selection dialog', 'All Files (*)'), options=options)
		if fileName:
			self.loadLexicon(fileName, self.caseBlind)
		self.resetFocusAndSelection()

	@pyqtSlot()
	def oncaseBlindChanged(self):
		self.caseBlind = not self.caseBlind
		self.lex = lexicon.Lexicon(self.lex.fileName, self.caseBlind,
		                           self.diacBlind, self.busyWait)
		self.updateLexInfo()
		self.resetFocusAndSelection()

	@pyqtSlot()
	def ondiacBlindChanged(self):
		self.diacBlind = not self.diacBlind
		self.lex = lexicon.Lexicon(self.lex.fileName, self.caseBlind,
		                           self.diacBlind, self.busyWait)
		self.updateLexInfo()
		self.resetFocusAndSelection()

	@pyqtSlot()
	def onEnter(self):
		actions = {
			LBL_WORD: self.lex.contains,
			LBL_REGEX: self.lex.regex,
			LBL_WITH_PREFIX: self.lex.withPrefix,
			LBL_WITH_SUFFIX: self.lex.withSuffix,
			LBL_ANAGRAMS: self.lex.anagrams
			}
		try:
			answer = actions[self.action](self.entryBox.text())
		except lexicon.LexiconError as err:   # must be from the re module
			self.errorAlert(_('There was a problem with the string or pattern:\n'
			                  '"{errorMessage}"').format(errorMessage=str(err)))
		else:
			if isinstance(answer, list):
				answer = ' '.join(answer)
			if not answer:
				answer = __('No matching entries', '[None]')
			self.results.setText(answer)
		self.resetFocusAndSelection()

	@pyqtSlot()
	def onToggle(self):
		obj = self.sender()
		if obj.isChecked():
			self.action = obj.text()
			self.resetFocusAndSelection()

	@pyqtSlot()
	def onEdit(self):
		editAction = self.sender().text()
		focusWidget = QApplication.focusWidget()
		if focusWidget not in (self.entryBox, self.results):
			return
		if editAction == LBL_CUT:
			focusWidget.cut()
		elif editAction == LBL_COPY:
			focusWidget.copy()
		elif editAction == LBL_PASTE:
			focusWidget.paste()
		elif editAction == LBL_SELECT_ALL:
			focusWidget.selectAll()
		self.resetFocusAndSelection()

def guiMain(options):
	fileName = options['lexicon']
	caseBlind, diacBlind = options['icase'], options['idiac']
	# QApplication must be called before any GUI elements are built
	application = QApplication([])
	# The following assignment is necessary to create a ref to MainWindow,
	# otherwise MainWindow immediately gets garbage-collected!
	mainWindow = MainWindow(lexVer.NAME, fileName, caseBlind, diacBlind)
	# In Python3, we don't need exec_ since exec is not a reserved word
	application.exec()

def main():
	print(_('This module is part of the {programName} package.\n'
	        'It is not intended to be used stand-alone.').format
			(programName=lexVer.NAME))


if __name__ == '__main__':
	main()

'''
PyQt5+Unity Menu Bar Shortcut Issue
---------------------------------------

It appears that shortcuts added only to specific menu items do not work in this
environment (perhaps because the menu bar is hidden by default). The code above
implements a workaround:

	1) add the shortcut to the menu item (so that the shortcut hint displays),
	2) also add the shortcut to the main window instance itself (so that the
	   shortcut is actually triggered)

... which is suggested here:

https://stackoverflow.com/questions/45211004/shortcut-doesnt-work-in-pyqt5-in-tray-dropdown-menu

... and explained by Igeyer (posting of Mar 21, 2012, 8:58 PM) here:

https://forum.qt.io/topic/15107/solved-action-shortcut-not-triggering-unless-action-is-placed-in-a-toolbar/5

An acknowledgement and discussion of what appears to this bug appears here:

https://bugs.launchpad.net/appmenu-qt5/+bug/1380702

'''
