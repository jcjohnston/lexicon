#!/usr/bin/env python3
# filedrop.py - Test of file drop on PyQt5 application
# jcj 20190525

import sys
from os.path import basename
filenames = [basename(path) for path in sys.argv[1:]]
'''
print(filenames)
input('Press Enter to continue: ')
sys.exit(0)

'''
from PyQt5.QtWidgets import *
print(filenames)
app = QApplication(sys.argv)
'''
w = QWidget()
w.resize(250, 150)
w.move(300, 300)
w.setWindowTitle(';'.join(filenames))
'''
w = QLabel(';'.join(filenames))
w.move(300, 300)
w.show()
sys.exit(app.exec())
