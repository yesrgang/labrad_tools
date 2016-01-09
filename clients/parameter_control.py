from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json
from client_tools import SuperSpinBox

class VarBox(QtGui.QLineEdit):
    def __init__(self):
        super(VarBox, self).__init__()

    def processString(self, string):
        string.replace(' ', '')
        if string[0] != '*':
            string = '*' + string
        return string

    def display(self, varname):
        varname = self.processString(varname)
        self.setText(varname)

    def read(self):
        text = self.text()
        varname = self.processString(text)
        self.display(varname)
        return varname

    def keyPressEvent(self, c):
        if c.key() == QtCore.Qt.Key_Return:
            self.read()
        else:
            super(VarBox, self).keyPressEvent(c)






if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = VarBox()
    widget.show()
    reactor.run()

