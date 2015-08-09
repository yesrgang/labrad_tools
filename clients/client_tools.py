from PyQt4 import QtGui, QtCore, Qt
import numpy as np

class SuperSpinBox(QtGui.QLineEdit):
    """ it really is! """
    def __init__(self, display_range, units, num_decimals=1):
        super(SuperSpinBox, self).__init__()
        self.display_range = display_range
        self.units = units
        self.display_factor = 10.**units[0][0]
        self.unit = units[0]
        self.num_decimals = num_decimals
        self.setText('0.0')

    def keyPressEvent(self, c):
        if c.key() == QtCore.Qt.Key_Return:
            split_text = self.text().split(' ')
            if len(split_text) == 1:
                unit = self.unit
            else:
                unit = self.text().split(' ')[1]
            if unit != self.unit:
                for f, u in self.units:
                    if unit == u:
                        self.unit = u
                        self.display_factor = 10.**f
            try:
                self.display(self.value())
            except:
                self.display(0)
        super(SuperSpinBox, self).keyPressEvent(c)
        if c.key() == QtCore.Qt.Key_Up:
            self.step(up=1)
        if c.key() == QtCore.Qt.Key_Down:
            self.step(up=0)

    def step(self, up):
        """ if we press the up (down) key, increment (decrement)
            the digit to the left of the cursor by one """
        text = self.text().split(' ')[0]
        cursor_position = self.cursorPosition()
        decimal_position = len(text.split('.')[0]) +1
        rel_position = decimal_position - cursor_position
        if cursor_position < decimal_position:
            rel_position -= 1

        value = float(text)*self.display_factor
        step_size = 10.**rel_position*self.display_factor
        if up:
            self.display(value + step_size)
        else:
            self.display(value - step_size)
        self.returnPressed.emit()

    def display(self, value):
        text = self.text().split(' ')[0]
        cursor_position = self.cursorPosition()
        decimal_position = len(text.split('.')[0]) +1
        rel_position = decimal_position - cursor_position
        if cursor_position < decimal_position:
            rel_position -= 1

        value = sorted([self.display_range[0], value, self.display_range[1]])[1]
        self.display_factor, self.unit = self.format_number(value)
        self.setText(str('{:0.'+str(self.num_decimals)+'f}' + ' {}'.format(self.unit)).format(value/self.display_factor))
        decimal_position = len(self.text().split('.')[0]) +1
        cursor_position = decimal_position - rel_position
        if rel_position >= 0:
            cursor_position -= 1
        self.setCursorPosition(cursor_position)

    def format_number(self, value):
        """ take a number and express it in most appropriate units"""
        def log10(x):
            if x != 0:
                return np.log10(x)
            else:
                return 0
        factor = min(zip(*self.units)[0], key=lambda x:
                     abs(x-np.floor(log10(value))+1))
        for x, y in self.units:
            if x == factor:
                return 10.**x, y

    def value(self):
        return float(self.text().split(' ')[0])*self.display_factor

