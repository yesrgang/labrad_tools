from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

class SuperSpinBox(QtGui.QLineEdit):
    def __init__(self):
        super(superSpinBox, self).__init__()#display_range, num_decimals)
        self.num_decimals = 5
        self.display(0.0)

    def keyPressEvent(self, c):
        super(superSpinBox, self).keyPressEvent(c)
        if c.key() == QtCore.Qt.Key_Up:
            self.step(up=1)
        if c.key() == QtCore.Qt.Key_Down:
            self.step(up=0)

    def step(self, up):
        text = self.text()
        value = float(text)
        cursor_position = self.cursorPosition()
        decimal_position = len(text.split('.')[0]) +1
        if cursor_position < decimal_position:
            rel_position = decimal_position - cursor_position - 1
        else:
            rel_position = decimal_position - cursor_position
        if up:
            self.display(value + 10**rel_position)
        else:
            self.display(value - 10**rel_position)
        self.editingFinished.emit()
        # now put the cursor back where it was
        text = self.text()
        decimal_position = len(text.split('.')[0]) +1
        if rel_position >= 0:
            self.setCursorPosition(decimal_position - rel_position-1)
        else: 
            self.setCursorPosition(decimal_position - rel_position)

    def display(self, value):
        d = str(self.num_decimals)
        self.setText(str('{:0.'+d+'f}').format(value))

class VerdiControl(QtGui.QGroupBox):
    has_new_state = False
    has_new_shutter_state = False
    has_new_power = False

    layout = None

    def __init__(self, widget_config, reactor, cxn=None):
        super(VerdiControl, self).__init__()
        self.wconfig = widget_config
        for key, value in self.wconfig.__dict__.items():
            setattr(self, key, value) # house server_name
        self.reactor = reactor
        self.populate_gui()

    
    def populate_gui(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.shutterstate_button = QtGui.QPushButton()
        self.shutterstate_button.setCheckable(1)
        
        self.power_box = superSpinBox()
#        self.power_box.setKeyboardTracking(False)
#        self.power_box.setRange(*self.power_range)
#        self.power_box.setSingleStep(self.power_stepsize)
#        self.power_box.setDecimals(abs(int(np.floor(np.log10(self.power_stepsize)))))
#        self.power_box.setAccelerated(True)
        self.power_box.setFixedWidth(self.spinbox_width)
        
        self.c_box = superSpinBox()
#        self.power_box.setKeyboardTracking(False)
#        self.power_box.setRange(*self.power_range)
#        self.power_box.setSingleStep(self.power_stepsize)
#        self.power_box.setDecimals(abs(int(np.floor(np.log10(self.power_stepsize)))))
#        self.power_box.setAccelerated(True)
        self.c_box.setFixedWidth(self.spinbox_width)
        
        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Shutter State: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.shutterstate_button, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Power [W]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.layout.addWidget(QtGui.QLabel('Current [A]: '), 4, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.c_box, 4, 1)
        self.setLayout(self.layout)
        self.setFixedSize(140 + self.spinbox_width, 130)

        self.power_box.editingFinished.connect(self.print_power)

    def print_power(self):
        print self.power_box.text()

#    def removeWidgets(self):
#        for i in reversed(range(self.layout.count())):
#            w = self.layout.itemAt(i).widget()
#            self.layout.removeWidget(w)
#            w.close()
                
    @inlineCallbacks
    def enable(self):
        yield self.get_configuration()
#        self.removeWidgets()
#        self.setDisabled(False)
#        yield self.connect()

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    from verdi_config import VerdiConfig
    conf = VerdiConfig()
    widget = VerdiControl(conf, reactor)
    widget.show()
    reactor.run()
