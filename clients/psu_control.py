from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
from time import sleep

class PSUControl(QtGui.QGroupBox):
    has_new_state = False
    has_new_current = False
    has_new_volatage = False
    layout = None

    def __init__(self, config_name, reactor, cxn=None):
        config = __import__(config_name).PSUConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
        self.reactor = reactor
        self.cxn = cxn 
        QtGui.QDialog.__init__(self)
        self.connect()

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.select_device()
            self.populate_gui()
            yield self.connect_signals()
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
    
    def populate_gui(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.current_box = SuperSpinBox(self.current_range, self.current_decimals) 
        self.current_box.setFixedWidth(self.spinbox_width)
        
        self.voltage_box = SuperSpinBox(self.voltage_range, self.voltage_decimals)
        self.voltage_box.setFixedWidth(self.spinbox_width)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Current [A]: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.current_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Voltage [V]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.voltage_box, 3, 1)
        self.setLayout(self.layout)
        self.setFixedSize(120 + self.spinbox_width, 166)

    @inlineCallbacks
    def connect_signals(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.signal__update_values(self.update_id)
        yield server.addListener(listener=self.receive_values, source=None, ID=self.update_id)
        yield self.cxn.add_on_connect(self.server_name, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.server_name, self.disable)

        self.state_button.toggled.connect(self.on_new_state)
        self.current_box.returnPressed.connect(self.on_new_current)
        self.voltage_box.returnPressed.connect(self.on_new_voltage)
        self.setMouseTracking(True)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.write_values)
        self.timer.start(self.update_time)
        
        self.free = True

    @inlineCallbacks
    def request_values(self, c=None):
        server = yield self.cxn.get_server(self.server_name)
        s = yield server.state()
 
    def receive_values(self, c, signal):
        name, state, current, voltage, power = signal
        print signal
        if name == self.name:
            self.free = False
            if state:
                self.state_button.setChecked(1)
                self.state_button.setText('On')
            else:
                self.state_button.setChecked(0)
                self.state_button.setText('Off')
            if not self.current_box.hasFocus():
                self.current_box.display(current)
            if not self.voltage_box.hasFocus():
                self.voltage_box.display(voltage)
            self.free = True

    def on_new_state(self):
        if self.free:
            self.has_new_state = True
   
    def on_new_current(self):
        if self.free:
            self.has_new_current = True
    
    def on_new_voltage(self):
        if self.free:
            self.has_new_volatage = True

    @inlineCallbacks
    def write_values(self):
        if  self.has_new_state:
            self.has_new_state = False
            server = yield self.cxn.get_server(self.server_name)
            state = self.state_button.isChecked() #yield server.state(self.name)
            yield server.state(state)
        elif self.has_new_current:
            self.has_new_current = False
            server = yield self.cxn.get_server(self.server_name)
            yield server.current(self.current_box.value())
#            sleep(.5)
#            yield server.current()
        elif self.has_new_volatage:
            self.has_new_volatage = False
            server = yield self.cxn.get_server(self.server_name)
            yield server.voltage(self.voltage_box.value())
#            sleep(.5)
#            yield server.voltage()

#    def removeWidgets(self):
#        for i in reversed(range(self.layout.count())):
#            w = self.layout.itemAt(i).widget()
#            self.layout.removeWidget(w)
#            w.close()
                
    @inlineCallbacks
    def reinitialize(self):
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
    config_name = 'psu_config'
    widget = PSUControl(config_name, reactor)
    widget.show()
    reactor.run()
