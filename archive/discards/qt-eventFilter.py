# Alternative approaches to installing an event filter to capture specific keys.
# In these cases, the aim is to capture Up and Down arrows in a QLineEdit field
# called entryBox, within a window where self = MainWindow().

	# install with: self.entryBox.installEventFilter(self)
	# NB This one needs a Boolean return value
	def eventFilter(self, source, event):
		'''Event filter installed for QLineEdit instance self.entryBox to implement history.
		NB: It must be called eventFilter and be an attribute of MainWindow.
		See https://stackoverflow.com/questions/45368148/connecting-to-events-of-another-widget'''
		assert(source is self.entryBox)
		if event.type() == QEvent.KeyPress:
			key = event.key()
			if key == Qt.Key_Up:
				if self.histIndex > 0:
					self.histIndex -= 1
					source.setText(self.histLines[self.histIndex])
					self.resetFocusAndSelection()
				return True
			elif key == Qt.Key_Down:
				if self.histIndex < len(self.histLines) - 1:
					self.histIndex += 1
					source.setText(self.histLines[self.histIndex])
					self.resetFocusAndSelection()
				return True
		return super().eventFilter(source, event)

	# install with: self.entryBox.keyPressEvent = self.keyPressEvent
	# NB This one must not return any value
	def keyPressEvent(self, event):
		'''Event filter installed specifically for self.entryBox, to handle history.
		See https://stackoverflow.com/questions/45368148/connecting-to-events-of-another-widget,
		the "more hackish variation"'''
		source = self.entryBox
		key = event.key()
		if key == Qt.Key_Up:
			if self.histIndex > 0:
				self.histIndex -= 1
				source.setText(self.histLines[self.histIndex])
				self.resetFocusAndSelection()
		elif key == Qt.Key_Down:
			if self.histIndex < len(self.histLines) - 1:
				self.histIndex += 1
				source.setText(self.histLines[self.histIndex])
				self.resetFocusAndSelection()
		else:
			QLineEdit.keyPressEvent(source, event)

# A completely alternative approach is to set up the relevant keys as shortcuts.
# Then no other interference with automatic event-processing is necessary:


	histBackAction = QAction(LBL_BACK, self)
	histBackAction.setShortcut(Qt.Key_Up)
	histBackAction.triggered.connect(self.onHistory)
	histMenu.addAction(histBackAction)
	self.addAction(histBackAction)

	# ditto for Qt.Key_Down

	@pyqtSlot()
	def onHistory(self):
		command = self.sender().text()
		source = self.entryBox
		if command == LBL_BACK:
			if self.histIndex > 0:
				self.histIndex -= 1
				source.setText(self.histLines[self.histIndex])
				self.resetFocusAndSelection()
		elif command == LBL_FORWARD:
			if self.histIndex < len(self.histLines) - 1:
				self.histIndex += 1
				source.setText(self.histLines[self.histIndex])
				self.resetFocusAndSelection()
		else:
			assert False, 'Impossible command in onHistory'


