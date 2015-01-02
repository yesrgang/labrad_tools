from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

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
        self.cxn = cxn 
        self.connect()

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.select_device()
            self.populateGUI()
            yield self.connectSignals()
            yield self.request_values()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def select_device(self):
        server = yield self.cxn.get_server(self.server_name)
        confstr = yield server.select_device_by_name(self.name)
        for key, value in eval(confstr).iteritems():
            setattr(self, key, value)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.shutterstate_button = QtGui.QPushButton()
        self.shutterstate_button.setCheckable(1)
        
        self.power_box = QtGui.QDoubleSpinBox()
        self.power_box.setKeyboardTracking(False)
        self.power_box.setRange(*self.power_range)
        self.power_box.setSingleStep(self.power_stepsize)
        self.power_box.setDecimals(abs(int(np.floor(np.log10(self.power_stepsize)))))
        self.power_box.setAccelerated(True)
        self.power_box.setFixedWidth(self.spinbox_width)
        
        self.current_box = QtGui.QDoubleSpinBox()
        self.current_box.setReadOnly(True)
        self.current_box.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.current_box.setFixedWidth(self.spinbox_width)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Shutter State: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.shutterstate_button, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Power [W]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.layout.addWidget(QtGui.QLabel('Current [A]: '), 4, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.current_box, 4, 1)
        self.setLayout(self.layout)
        self.setFixedSize(140 + self.spinbox_width, 130)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.signal__update_values(self.update_id)
        yield server.addListener(listener=self.receive_values, source=None, ID=self.update_id)
        yield self.cxn.add_on_connect(self.server_name, self.enable)
        yield self.cxn.add_on_disconnect(self.server_name, self.disable)

        self.state_button.pressed.connect(self.on_new_state)
        self.shutterstate_button.pressed.connect(self.on_new_shutter_state)
        self.power_box.valueChanged.connect(self.has_new_power)
#        self.setMouseTracking(True)
#        self.mouseHover.connect(self.request_values)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.write_values)
        self.timer.start(self.update_time)
        
        self.free = True

    @inlineCallbacks
    def request_values(self, c=None):
        server = yield self.cxn.get_server(self.server_name)
        yield server.request_values(self.name)
 
    def receive_values(self, c, signal):
        name, state, shutterstate, power, current = signal
        if name == self.name:
            self.free = False
            if state:
                self.state_button.setChecked(1)
                self.state_button.setText('On')
            else:
                self.state_button.setChecked(0)
                self.state_button.setText('Off')
            if shutterstate:
                self.shutterstate_button.setChecked(1)
                self.shutterstate_button.setText('Open')
            else:
                self.shutterstate_button.setChecked(0)
                self.shutterstate_button.setText('Closed')
            if not self.power_box.hasFocus():
                self.power_box.setValue(power)
            self.current_box.setValue(current)
            self.free = True

    def on_new_state(self):
        if self.free:
            self.has_new_state = True
    
    def on_new_shutter_state(self):
        if self.free:
            self.has_new_shutter_state = True

    def has_new_power(self, c):
        if self.free:
            self.has_new_power = True
   

    @inlineCallbacks
    def write_values(self):
        if  self.has_new_state:
            self.has_new_state = False
            server = yield self.cxn.get_server(self.server_name)
            is_on = self.state_button.isChecked()
            yield server.state(self.name, not is_on)
        if  self.has_new_shutter_state:
            self.has_new_shutter_state = False
            server = yield self.cxn.get_server(self.server_name)
            is_on = self.shutterstate_button.isChecked()
            yield server.shutter_state(self.name, not is_on)
        elif self.has_new_power:
            server = yield self.cxn.get_server(self.server_name)
            yield server.power(self.name, self.power_box.value())
            self.has_new_power = False

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
