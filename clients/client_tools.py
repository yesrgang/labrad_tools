from PyQt4 import QtGui, QtCore, Qt
import numpy as np

class SuperSpinBox(QtGui.QLineEdit):
    def __init__(self, display_range, num_decimals, display_factor=1):
        super(SuperSpinBox, self).__init__()
        self.display_range = [d*display_factor for d in display_range]
        self.num_decimals = num_decimals
        self.display_factor = display_factor # multiply value before displaying
        #self.display(0.0)

    def keyPressEvent(self, c):
        super(SuperSpinBox, self).keyPressEvent(c)
        if c.key() == QtCore.Qt.Key_Up:
            self.step(up=1)
        if c.key() == QtCore.Qt.Key_Down:
            self.step(up=0)

    def step(self, up):
        text = self.text()
        value = float(text)/self.display_factor
        cursor_position = self.cursorPosition()
        decimal_position = len(text.split('.')[0]) +1
        if cursor_position < decimal_position:
            rel_position = decimal_position - cursor_position - 1
        else:
            rel_position = decimal_position - cursor_position
        if up:
            self.display(value + 10**rel_position/self.display_factor)
        else:
            self.display(value - 10**rel_position/self.display_factor)
        self.returnPressed.emit()

    def display(self, value):
        text = self.text()
        cursor_position = self.cursorPosition()
        decimal_position = len(text.split('.')[0]) +1
        if cursor_position < decimal_position:
            rel_position = decimal_position - cursor_position - 1
        else:
            rel_position = decimal_position - cursor_position

        value = sorted([self.display_range[0], value*self.display_factor, self.display_range[1]])[1]
        d = str(self.num_decimals)
        self.setText(str('{:0.'+d+'f}').format(value))
        
        text = self.text()
        decimal_position = len(text.split('.')[0]) +1
        if rel_position >= 0:
            self.setCursorPosition(decimal_position - rel_position-1)
        else: 
            self.setCursorPosition(decimal_position - rel_position)

    def value(self):
        return float(self.text())/self.display_factor
