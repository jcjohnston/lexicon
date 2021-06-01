# lexGui.py jcj 2019-02-27, 2019-04-23, 2019-11-20, 2020-02-11, 2020-03-20,
#           2020-05-12, 2020-05-27

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
    from my.pgettext import pgettext
__ = pgettext

# standard-library imports
import os.path

# optional module imports
from PyQt5 import QtPrintSupport
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QTimer, QEventLoop

# private-module imports

from my.textutils import fmt

# project imports
import lexicon
from lexOut import *
from lexStrings import *

class LBL:
    '''Widget labels, including menus and menu items'''
    FILE = __('Menu', '&File')
    SAVE_AS = __('Menu|File', '&Save As...')
    PRINT = __('Menu|File', '&Print...')
    QUIT = __('Menu|File', '&Quit')
    EDIT = __('Menu', '&Edit')
    UNDO = __('Menu|Edit', '&Undo')
    REDO = __('Menu|Edit', '&Redo')
    CUT = __('Menu|Edit', 'Cu&t')
    COPY = __('Menu|Edit', '&Copy')
    PASTE = __('Menu|Edit', '&Paste')
    SELECT_ALL = __('Menu|Edit', 'Select &All')
    HISTORY = __('Menu', 'H&istory')
    BACK = __('Menu|History', '&Back')
    FORWARD = __('Menu|History', '&Forward')
    CLEAR_HISTORY = __('Menu|History', '&Clear')
    HELP = __('Menu', '&Help')
    ABOUT = __('Menu|Help', '&About {self.title}...')
    CHANGE_LEXICON = __('Button', 'Change &Lexicon')
    IGNORE_CASE = __('Checkbox', 'Ignore &Case')
    IGNORE_DIACS = __('Checkbox', 'Ignore &Diacritics')
    STRING = __('Label: Text string', 'String:')
    PATTERN = __('Label: Regular expression', 'Pattern:')
    # These are defined in lexConsts with their text-based counterparts:
    WORD = COMMANDS[CMD.WORD].LABEL
    RELATED = COMMANDS[CMD.RELS].LABEL
    HOMOPHONES = COMMANDS[CMD.HOMS].LABEL
    ANAGRAMS = COMMANDS[CMD.ANAG].LABEL
    REGEX = COMMANDS[CMD.REGX].LABEL

DEFAULT_STYLESHEET = '''
    body {}
    .headword  { color: red; }
    .synset { color: blue; }
    .rellist {}
    .relname { font-style: italic; }
    .reldata {}
    .words {}
'''

APP_ICON = os.path.join(ENV.APP_DIR, ENV.ICON_FILE)

class MainWindow(QMainWindow):

    def __init__(self, title, options):
        super().__init__()
        self.title = title
        self.options = options
        self.lex = None 
        self.action = None
        self.fileName = options[OPT.LEXICON]
        # initialise history mechanism
        self.histLines = []
        self.histIndex = -1
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
        self.loadLexicon(self.options)
        self.updateLexInfo()
        # initialize CSS styles for HTML output
        style = DEFAULT_STYLESHEET
        if options[OPT.STYLE]:
            try:
                with open(options[OPT.STYLE]) as f:
                    style = f.read()
            except IOError as err:
                self.errorAlert(str(err))
        self.results.document().setDefaultStyleSheet(style)
        # after each event, we re-set the focus to the entry field
        # and select all the text within it
        self.resetFocusAndSelection()

    def addWidgets(self):
        container = QWidget()
        grid = QGridLayout()
        # at top: label identifying lexicon,
        # with Change Lexicon button at the right
        self.lexLabel = QLabel(self)
        self.lexiconButton = QPushButton(LBL.CHANGE_LEXICON, self)
        self.lexiconButton.clicked.connect(self.onChangeLexicon)
        # language selection
        self.wnLabel = QLabel(self)
        self.wnLabel.setText(_('WordNet available in:'))
        self.languageSelect = QComboBox(self)
        self.languageSelect.addItems(languageNames())
        self.languageSelect.setCurrentText(languageName
                                           (self.options[OPT.LANGUAGE]))
        handler = lambda: self.onChangeLanguage(
                            self.languageSelect.currentText())
        self.languageSelect.currentIndexChanged.connect(handler) 
        # a pop-up progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(0, 0, 75, 10)
        self.progressBar.setMinimum(0)
        # for an infinite progress bar, set maximum to 0
        self.progressBar.setMaximum(100)
        self.progressBar.hide()
        # a checkbox for case-insensitive matching
        iCaseCheckBox = QCheckBox(LBL.IGNORE_CASE, self)
        iCaseCheckBox.setChecked(self.options[OPT.ICASE])
        iCaseCheckBox.stateChanged.connect(self.onChangeCheckBox)
        # a checkbox for diacritic-blind matching
        iDiacCheckBox = QCheckBox(LBL.IGNORE_DIACS, self)
        iDiacCheckBox.setChecked(self.options[OPT.IDIAC])
        iDiacCheckBox.stateChanged.connect(self.onChangeCheckBox)
        # pack them all in
        grid.addWidget(self.lexLabel, 0, 0)
        grid.addWidget(self.lexiconButton, 0, 1)
        grid.addWidget(self.wnLabel, 1, 0)
        grid.addWidget(self.languageSelect, 1, 1)
        grid.addWidget(self.progressBar, 0, 1)   # over Change Lexicon button
        #grid.addWidget(self.progressBar, 1, 0, 1, 2)   # span 2 columns
        grid.addWidget(iCaseCheckBox, 2, 0)
        grid.addWidget(iDiacCheckBox, 2, 1)
        container.setLayout(grid)
        self.vBox.addWidget(container)

        # next: an edit box with a label
        container = QWidget()
        hBox = QHBoxLayout()
        self.entryLabel = QLabel(LBL.STRING, self)
        self.entryBox = QLineEdit()
        self.entryBox.returnPressed.connect(self.onEnter)
        hBox.addWidget(self.entryLabel)
        hBox.addWidget(self.entryBox)
        container.setLayout(hBox)
        self.vBox.addWidget(container)

        # next: a group of radio buttons
        # they are auto-exclusive bc they belong to the same parent widget,
        # so they don't need to be added to a QButtonGroup
        container = QWidget()
        hBox = QHBoxLayout()
        self.wordButton = QRadioButton(LBL.WORD, container)
        self.wordButton.toggled.connect(self.onToggle)
        self.wordButton.setChecked(True)
        self.wordButton.setEnabled(False)
        self.relatedButton = QRadioButton(LBL.RELATED, container)
        self.relatedButton.toggled.connect(self.onToggle)
        self.relatedButton.setEnabled(False)
        self.homophonesButton = QRadioButton(LBL.HOMOPHONES, container)
        self.homophonesButton.toggled.connect(self.onToggle)
        self.homophonesButton.setEnabled(False)
        self.anagramsButton = QRadioButton(LBL.ANAGRAMS, container)
        self.anagramsButton.toggled.connect(self.onToggle)
        self.anagramsButton.setEnabled(False)
        self.regexButton = QRadioButton(LBL.REGEX, container)
        self.regexButton.toggled.connect(self.onToggle)
        self.regexButton.setEnabled(False)
        hBox.addWidget(self.wordButton)
        hBox.addWidget(self.relatedButton)
        hBox.addWidget(self.homophonesButton)
        hBox.addWidget(self.anagramsButton)
        hBox.addWidget(self.regexButton)
        container.setLayout(hBox)
        self.vBox.addWidget(container)

        # finally, a TextEdit field to display the HTML-formatted results
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setMinimumHeight(300)
        self.vBox.addWidget(self.results)

    def addMenuBar(self):

        # Calling QKeySequence() for shortcuts gives the standard
        # keychord for the platform concerned

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu(LBL.FILE)
        editMenu = menuBar.addMenu(LBL.EDIT)
        histMenu = menuBar.addMenu(LBL.HISTORY)
        helpMenu = menuBar.addMenu(LBL.HELP)

        # File menu
        saveAsAction = QAction(LBL.SAVE_AS, self)
        saveAsAction.setShortcut(QKeySequence.SaveAs)
        saveAsAction.triggered.connect(self.onSaveAs)
        fileMenu.addAction(saveAsAction)
        self.addAction(saveAsAction)    # see note at bottom re this and all
                                        # following self.addAction calls

        printAction = QAction(LBL.PRINT, self)
        printAction.setShortcut(QKeySequence.Print)
        printAction.triggered.connect(self.onPrint)
        fileMenu.addAction(printAction)
        self.addAction(printAction)

        quitAction = QAction(LBL.QUIT, self)
        quitAction.setShortcut(QKeySequence.Quit)
        quitAction.triggered.connect(self.close)
        fileMenu.addAction(quitAction)
        self.addAction(quitAction)   

        # NB re the six basic editing actions:
        # These, including their standard shortcuts, appear to be implemented by
        # PyQt5 itself, at least for the QLineEdit and QTextEdit widgets, so
        # these menu entries are, strictly-speaking, more or less redundant.
        # However, the working (non-standard) Alt+Letter accelerators show that
        # the menu entries are independently effective.

        # Edit menu
        undoAction = QAction(LBL.UNDO, self)
        undoAction.setShortcut(QKeySequence.Undo)
        undoAction.triggered.connect(self.onEdit)
        editMenu.addAction(undoAction)
        self.addAction(undoAction)

        redoAction = QAction(LBL.REDO, self)
        redoAction.setShortcut(QKeySequence.Redo)
        redoAction.triggered.connect(self.onEdit)
        editMenu.addAction(redoAction)
        self.addAction(redoAction)

        editMenu.addSeparator()
    
        cutAction = QAction(LBL.CUT, self)
        cutAction.setShortcut(QKeySequence.Cut)
        cutAction.triggered.connect(self.onEdit)
        editMenu.addAction(cutAction)
        self.addAction(cutAction)

        copyAction = QAction(LBL.COPY, self)
        copyAction.setShortcut(QKeySequence.Copy)
        copyAction.triggered.connect(self.onEdit)
        editMenu.addAction(copyAction)
        self.addAction(copyAction)

        pasteAction = QAction(LBL.PASTE, self)
        pasteAction.setShortcut(QKeySequence.Paste)
        pasteAction.triggered.connect(self.onEdit)
        editMenu.addAction(pasteAction)
        self.addAction(pasteAction)

        editMenu.addSeparator()

        selectAllAction = QAction(LBL.SELECT_ALL, self)
        selectAllAction.setShortcut(QKeySequence.SelectAll)
        selectAllAction.triggered.connect(self.onEdit)
        editMenu.addAction(selectAllAction)
        self.addAction(selectAllAction)

        # History menu

        histBackAction = QAction(LBL.BACK, self)
        histBackAction.setShortcut(Qt.Key_Up)
        histBackAction.triggered.connect(self.onHistory)
        histMenu.addAction(histBackAction)
        self.addAction(histBackAction)

        histFwdAction = QAction(LBL.FORWARD, self)
        histFwdAction.setShortcut(Qt.Key_Down)
        histFwdAction.triggered.connect(self.onHistory)
        histMenu.addAction(histFwdAction)
        self.addAction(histFwdAction)

        histMenu.addSeparator()

        histClearAction = QAction(LBL.CLEAR_HISTORY, self)
        histClearAction.triggered.connect(self.onHistory)
        histMenu.addAction(histClearAction)

        # Help menu

        aboutAction = QAction(fmt(LBL.ABOUT), self)
        aboutAction.triggered.connect(self.about)
        helpMenu.addAction(aboutAction)

    def resetFocusAndSelection(self):
        self.entryBox.setFocus()
        self.entryBox.selectAll()
    
    def loadLexicon(self, options):
        '''This is used where the attempt to load fileName might fail'''
        try:
            newLex = lexicon.Lexicon(options, busyWait=self.busyWait)
        except lexicon.LexiconError as err:
            errorMessage = str(err)
            self.errorAlert(
                fmt(_('Could not load lexicon: "{errorMessage}"')))
        else:
            self.lex = newLex
            self.options = options
        self.updateLexInfo()

    def updateLexInfo(self):
        if self.fileName:
            nHeads, nProns, nVars = self.lex.stats()
            fileName = os.path.basename(self.options[OPT.LEXICON])
            self.lexLabel.setText(fmt(_('File: {fileName}\n'
                                    '{nHeads:,d} /{nProns:,d} ({nVars:,d})/')))
        else:
            self.lexLabel.setText(_('File: [None]'))
        if not self.lex.hasWordNet:
            self.wnLabel.setText(_('[No WordNet available]'))
            self.languageSelect.setEnabled(False)
        self.wordButton.setEnabled(bool(self.fileName or self.lex.hasWordNet))
        self.relatedButton.setEnabled(self.lex.hasWordNet)
        self.homophonesButton.setEnabled(bool(self.fileName))
        self.anagramsButton.setEnabled(bool(self.fileName))
        self.regexButton.setEnabled(bool(self.fileName))

    def about(self):
        msgBox = QMessageBox(self, icon=QMessageBox.Information)
        msgBox.setWindowTitle(fmt(__('MessageBox Title',
             'About {ID.NAME}')))
        # unlike QTextEdit, QMessageBox has to be told to accept HTML
        msgBox.setTextFormat(Qt.RichText)
        description = fmt('{ID.NAME} {ID.VERSION} {ID.COPYRIGHT}')
        message = (fmt('<p align="center">{description}</p>'))
        if self.lex.hasWordNet:
            message += fmt('<p align="center">{ID.THANKS_RICH}</p>')
        message += fmt('<p align="center">{ID.HELP_RICH}</p>')
        msgBox.setText(message)
        msgBox.exec()
    
    def errorAlert(self, message):
        QMessageBox.warning(self, __('MessageBox Title', 'Warning'), message)
        self.resetFocusAndSelection()

    def busyWait(self, phase, percent):
        fileName = (os.path.basename(self.lex.fileName) if self.lex
                    else __('Reading lexicon file', '[Loading]'))
        phaseString = busyPhase(phase)
        self.lexLabel.setText(
            fmt(_('File: {fileName}\n{phaseString}')))
        QCoreApplication.processEvents()
        if percent == 0:
            self.lexiconButton.hide()
            self.progressBar.show()
        self.progressBar.setValue(percent)
        QCoreApplication.processEvents()
        # delay a little to show completion
        if percent == 100:
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec()
            self.progressBar.hide()
            self.lexiconButton.show()

    @pyqtSlot()
    def onEnter(self):
        text = self.entryBox.text()
        # record in history
        if not self.histLines or text != self.histLines[-1]:
            self.histLines.append(text)
        self.histIndex = len(self.histLines) - 1
        # dispatch based on currently chosen action
        width = 0
        actions = {
            LBL.WORD: lambda s:
                defsDisplay(self.lex, s, width) if self.lex.hasWordNet
                    else headsDisplay(self.lex, s, width),
            LBL.RELATED: lambda s: nymsDisplay(self.lex, s, width),
            LBL.HOMOPHONES: lambda s: wordsDisplay
                                      (self.lex.homophones(s), width),
            LBL.ANAGRAMS: lambda s: wordsDisplay(self.lex.anagrams(s), width),
            LBL.REGEX: lambda s: wordsDisplay(self.lex.regex(s), width),
            }
        try:
            answer = actions[self.action](text)
        except lexicon.LexiconError as err:   # must be from the re module
            errorMessage = str(err)
            self.errorAlert(
                fmt(_('There was a problem with the string or pattern:\n'
                  '"{errorMessage}"')))
        else:
            assert isinstance(answer, list), 'Unexpected non-list answer'
            if not answer:
                answer = [__('No matching entries', '[None]')]
            # setText would work, but the editor guesses whether it's plain
            # text or HTML; use setHtml or setPlainText to avoid guesswork
            self.results.setHtml(' '.join(answer))
        self.resetFocusAndSelection()

    @pyqtSlot()
    def onHistory(self):
        command = self.sender().text()
        source = self.entryBox
        if command == LBL.BACK:
            if self.histIndex > 0:
                self.histIndex -= 1
                source.setText(self.histLines[self.histIndex])
                self.resetFocusAndSelection()
        elif command == LBL.FORWARD:
            if self.histIndex < len(self.histLines) - 1:
                self.histIndex += 1
                source.setText(self.histLines[self.histIndex])
                self.resetFocusAndSelection()
        elif command == LBL.CLEAR_HISTORY:
            self.histLines = []
            self.histIndex = -1
        else:
            assert False, 'Impossible command in onHistory: %s' % command

    @pyqtSlot()
    def onChangeLexicon(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                    __('File-selection dialog', 'Select lexicon file'), '',
                    __('File-selection dialog', 'All Files (*)'),
                       options=options)
        if fileName:
            options = self.options
            options[OPT.LEXICON] = fileName
            self.fileName = fileName
            self.loadLexicon(options)
        self.resetFocusAndSelection()

    @pyqtSlot()
    def onChangeLanguage(self, language):
        self.options[OPT.LANGUAGE] = languageCode(language)
        self.lex.setLanguage(self.options[OPT.LANGUAGE])

    @pyqtSlot()
    def onChangeCheckBox(self):
        if self.sender().text() == LBL.IGNORE_CASE:
            self.options[OPT.ICASE] = not self.options[OPT.ICASE]
        else:   # must be LBL.IGNORE_DIAC
            self.options[OPT.IDIAC] = not self.options[OPT.IDIAC]
        self.lex = lexicon.Lexicon(self.options, busyWait=self.busyWait)
        self.updateLexInfo()
        self.resetFocusAndSelection()

    @pyqtSlot()
    def onToggle(self):
        obj = self.sender()
        if obj.isChecked():   # new action mode chosen
            self.action = obj.text()
            if self.action == LBL.REGEX:
                self.entryLabel.setText(LBL.PATTERN)
            else:
                self.entryLabel.setText(LBL.STRING)
            self.resetFocusAndSelection()

    @pyqtSlot()
    def onEdit(self):
        editAction = self.sender().text()
        focusWidget = QApplication.focusWidget()
        if focusWidget not in (self.entryBox, self.results):
            return
        if editAction == LBL.UNDO and focusWidget == self.entryBox:
            focusWidget.undo()
        elif editAction == LBL.REDO and focusWidget == self.entryBox:
            focusWidget.redo()
        elif editAction == LBL.CUT:
            focusWidget.cut()
        elif editAction == LBL.COPY:
            focusWidget.copy()
        elif editAction == LBL.PASTE:
            focusWidget.paste()
        elif editAction == LBL.SELECT_ALL:
            focusWidget.selectAll()
        self.resetFocusAndSelection()

    @pyqtSlot()
    def onPrint(self):
        dialog = QtPrintSupport.QPrintDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.results.document().print(dialog.printer())

    @pyqtSlot()
    def onSaveAs(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        suggested_name = (self.entryBox.text() + '_'
                        + self.action.lower().replace('&', '') + '.html')
        fileName, junk = QFileDialog.getSaveFileName(self,
            __('File-selection dialog', 'Save Lexitron output'),
            suggested_name,
            __('File-selection dialog', 'HTML Files (*.html *.htm)'),
            options=options)
        if fileName:
            with open(fileName, 'w') as f:
                f.write(self.results.toHtml())
        
def guiMain(options):
    # QApplication must be called before any GUI elements are built
    # Set application name (works for Ubuntu but not Mac)
    application = QApplication([ENV.DISPLAY_NAME])
    # Set application icon (works for Ubuntu and Mac)
    application.setWindowIcon(QIcon(APP_ICON))
    # The following assignment is necessary to create a ref to MainWindow,
    # otherwise MainWindow immediately gets garbage-collected!
    mainWindow = MainWindow(ID.NAME, options)
    # In Python3, we don't need exec_ since exec is not a reserved word
    application.exec()

if __name__ == '__main__':
    print(_('This module is part of the Lexitron package'))

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

An acknowledgement and discussion of what appears to be this bug appears here:

https://bugs.launchpad.net/appmenu-qt5/+bug/1380702

2020-05-18 Query whether all this is still the case in Ubuntu 18.04 with Gnome
replacing Unity
'''
