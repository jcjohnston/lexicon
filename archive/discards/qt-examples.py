#!/usr/bin/env python3
# lexGui.py - PyQt5 GUI for lexitron

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QMessageBox, QLineEdit,
                             QAction, QGroupBox, QHBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.Qt import Qt

class Dialog(QDialog):

    def __init__(self):
        super().__init__()
        button = QPushButton('Click')
        button.clicked.connect(self.onClick)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(button)
        self.setLayout(mainLayout)
        self.setWindowTitle('Exemple de Bouton')

class MainWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'Lexicon Tool'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createHorizontalLayout()
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)


        '''
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        # create an Exit item in the File menu
        exitButton = QAction(QIcon('exit24.png'), '&Quit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Quitthe application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
        self.addAction(exitButton)

        statusBar = self.statusBar()
        '''
        '''
        self.textBox = QLineEdit(self)
        self.textBox.move(20, 20)
        self.textBox.resize(280, 40)

        self.button = QPushButton('Show text', self)
        self.button.move(20, 80)
        self.button.clicked.connect(self.onClick)
        '''

        '''
        self.statusBar().showMessage('No lexicon loaded yet')
        '''

        '''
        button = QPushButton('Change lexicon', self)
        button.setToolTip('Use this to load a different lexicon file')
        button.move(100, 70)
        button.clicked.connect(self.onClick)
        '''

        self.show()

        '''
        buttonReply = QMessageBox.question(self, 'MESSAGE',
                'Do you like PyQt5?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel)
        if buttonReply == QMessageBox.Yes:
            print('So you do like PyQt5!')
        elif buttonReply == QMessageBox.No:
            print('My, you _are_ hard to please!')
        else:
            print("Well if you won't play at all... <sniff>")
        '''

    def createHorizontalLayout(self):
        #self.horizontalGroupBox = QGroupBox('What is your favourite colour?')
        self.horizontalGroupBox = QGroupBox()
        layout = QHBoxLayout()

        buttonBlue = QPushButton('Blue')
        buttonBlue.clicked.connect(self.onClick)
        layout.addWidget(buttonBlue)

        buttonRed = QPushButton('Red')
        buttonRed.clicked.connect(self.onClick)
        layout.addWidget(buttonRed)

        buttonGreen = QPushButton('Green')
        buttonGreen.clicked.connect(self.onClick)
        layout.addWidget(buttonGreen)

        self.horizontalGroupBox.setLayout(layout)

    @pyqtSlot()
    def onClick(self):
        buttonName = self.sender().text()
        print('Clicked %s button' % buttonName)
        '''
        textBoxValue = self.textBox.text()
        QMessageBox.question(self, 'MESSAGE', 
            'You typed: ' + textBoxValue, QMessageBox.Ok,
            QMessageBox.Ok)
        self.textBox.setText('')
        '''

def main():
    '''Create a GUI and run event loop'''
    app = QApplication(sys.argv)
    window = MainWindow()
    #dialog = Dialog()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
