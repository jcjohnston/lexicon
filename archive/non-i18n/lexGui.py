#!/usr/bin/env python3
# lexGui.py - GUI written in Qt for Lexitron
# jcj 20190227, 20190423, 20191120, 20200125

import lexicon
from lexVer import NAME, DESCRIPTION

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from PyQt5.QtCore import QTimer, QEventLoop

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
		changeButton = QPushButton('Change &Lexicon', self)
		changeButton.clicked.connect(self.onChangeLexicon)
		# a pop-up progress bar
		self.progressBar = QProgressBar(self)
		self.progressBar.setGeometry(0, 0, 75, 10)
		self.progressBar.setMinimum(0)
		# for an infinite progress bar, set maximum to 0
		self.progressBar.setMaximum(100)
		self.progressBar.hide()
		# a checkbox for case-insensitive matching
		caseBlindCheckBox = QCheckBox('Ignore &Case', self)
		caseBlindCheckBox.setChecked(self.caseBlind)
		caseBlindCheckBox.stateChanged.connect(self.oncaseBlindChanged)
		# a checkbox for diacritic-blind matching
		diacBlindCheckBox = QCheckBox('Ignore &Diacritics', self)
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
		label = QLabel('String or pattern: ', self)
		self.entryBox = QLineEdit()
		self.entryBox.returnPressed.connect(self.onEnter)
		hBox.addWidget(label)
		hBox.addWidget(self.entryBox)
		container.setLayout(hBox)
		self.vBox.addWidget(container)

		# next: a group of radio buttons
		container = QWidget()
		hBox = QHBoxLayout()
		button1 = QRadioButton('&Word', container)
		button1.toggled.connect(self.onToggle)
		button2 = QRadioButton('&Regex', container)
		button2.toggled.connect(self.onToggle)
		button3 = QRadioButton('With &Prefix', container)
		button3.toggled.connect(self.onToggle)
		button4 = QRadioButton('With &Suffix', container)
		button4.toggled.connect(self.onToggle)
		button5 = QRadioButton('&Anagrams', container)
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
		fileMenu = menuBar.addMenu('&File')
		editMenu = menuBar.addMenu('&Edit')
		helpMenu = menuBar.addMenu('&Help')

		# File menu
		quitAction = QAction('&Quit', self)
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
		cutAction = QAction('Cu&t', self)
		cutAction.setShortcut('Ctrl+X')
		cutAction.triggered.connect(self.onEdit)
		editMenu.addAction(cutAction)
		self.addAction(cutAction)

		copyAction = QAction('&Copy', self)
		copyAction.setShortcut('Ctrl+C')
		copyAction.triggered.connect(self.onEdit)
		editMenu.addAction(copyAction)
		self.addAction(copyAction)

		pasteAction = QAction('&Paste', self)
		pasteAction.setShortcut('Ctrl+V')
		pasteAction.triggered.connect(self.onEdit)
		editMenu.addAction(pasteAction)
		self.addAction(pasteAction)

		editMenu.addSeparator()

		selectAllAction = QAction('Select &All', self)
		selectAllAction.setShortcut('Ctrl+A')
		selectAllAction.triggered.connect(self.onEdit)
		editMenu.addAction(selectAllAction)
		self.addAction(selectAllAction)

		# Help menu

		aboutAction = QAction('&About %s...' % self.title, self)
		aboutAction.triggered.connect(self.about)
		helpMenu.addAction(aboutAction)

	def resetFocusAndSelection(self):
		self.entryBox.setFocus()
		self.entryBox.selectAll()
	
	def loadLexicon(self, fileName, caseBlind=False, diacBlind=False):
		try:
			newLex = lexicon.Lexicon(fileName, caseBlind, diacBlind, self.busyWait)
		except lexicon.LexiconError as err:
			self.errorAlert('Could not load lexicon: "%s"' % str(err))
		else:
			self.lex = newLex
			self.fileName = fileName
			self.caseBlind = caseBlind
			self.diacBlind = diacBlind
		self.updateLexInfo()

	def updateLexInfo(self):
		if self.lex:
			self.lexLabel.setText('File: %s\nLength: %s entries' %
						(self.lex.fileName, format(self.lex.length(), ',d')))
		else:
			self.lexLabel.setText('[No file, no entries]\n')

	def about(self):
		QMessageBox.about(self, 'About Lexitron', DESCRIPTION);
	
	def errorAlert(self, message):
		QMessageBox.warning(self, 'Warning', message)
		self.resetFocusAndSelection()

	def busyWait(self, percent, message):
		self.lexLabel.setText('File: %s\n%s' %
					(self.lex.fileName if self.lex else '[Loading]', message))
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
					'Select lexicon file', '',
					'All Files (*)', options=options)
		if fileName:
			self.loadLexicon(fileName, self.caseBlind)
		self.resetFocusAndSelection()

	@pyqtSlot()
	def oncaseBlindChanged(self):
		self.caseBlind = not self.caseBlind
		self.lex = lexicon.Lexicon(self.lex.fileName, self.caseBlind, self.diacBlind, self.busyWait)
		self.updateLexInfo()
		self.resetFocusAndSelection()

	@pyqtSlot()
	def ondiacBlindChanged(self):
		self.diacBlind = not self.diacBlind
		self.lex = lexicon.Lexicon(self.lex.fileName, self.caseBlind, self.diacBlind, self.busyWait)
		self.updateLexInfo()
		self.resetFocusAndSelection()

	@pyqtSlot()
	def onEnter(self):
		actions = {
			'Word': self.lex.contains, 'Regex': self.lex.regex,
			'With Prefix': self.lex.withPrefix, 'With Suffix': self.lex.withSuffix,
			'Anagrams': self.lex.anagrams
			}
		answer = actions[self.action](self.entryBox.text())
		if isinstance(answer, list):
			answer = ' '.join(answer)
		if not answer:
			answer = '[None]'
		self.results.setText(answer)
		self.resetFocusAndSelection()

	@pyqtSlot()
	def onToggle(self):
		obj = self.sender()
		if obj.isChecked():
			self.action = obj.text().replace('&', '')
			self.resetFocusAndSelection()

	@pyqtSlot()
	def onEdit(self):
		editAction = self.sender().text().replace('&', '')
		focusWidget = QApplication.focusWidget()
		if focusWidget not in (self.entryBox, self.results):
			return
		if editAction == 'Cut':
			focusWidget.cut()
		elif editAction == 'Copy':
			focusWidget.copy()
		elif editAction == 'Paste':
			focusWidget.paste()
		elif editAction == 'Select All':
			focusWidget.selectAll()
		self.resetFocusAndSelection()

def guiMain(fileName, caseBlind=False, diacBlind=False, cmds=None):

	# QApplication must be called before any GUI elements are built
	application = QApplication([])
	# The following assignment is necessary to create a ref to MainWindow,
	# otherwise MainWindow immediately gets garbage-collected!
	mainWindow = MainWindow(NAME, fileName, caseBlind, diacBlind)
	# In Python3, we don't need exec_ since exec is not a reserved word
	application.exec()

def main():
	print('This module is part of the lexitron package.')
	print('It is not intended to be used stand-alone.')

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
