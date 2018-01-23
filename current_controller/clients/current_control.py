import json
import numpy as np
import sys

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks

sys.path.append('../../client_tools')
from connection import connection
from widgets import SuperSpinBox

class CurrentControl(QtGui.QGroupBox):
    mouseHover = pyqtSignal(bool)
    def __init__(self, config, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
        self.load_config(config)
        self.connect()

    def load_config(self, config=None):
        if type(config).__name__ == 'str':
            config = __import__(config).ControlConfig()
        if config is not None:
            self.config = config
        for key, value in self.config.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def connect(self):
        self.cxn = connection()
        cname = '{} - {} - client'.format(self.servername, self.name)
        yield self.cxn.connect(name=cname)
        self.context = yield self.cxn.context()
        yield self.select_device()
        self.populateGUI()
        yield self.connectSignals()
        yield self.requestValues()

    @inlineCallbacks
    def select_device(self):
        server = yield self.cxn.get_server(self.servername)
        config = yield server.select_device(self.name)
        for key, value in json.loads(config).items():
            setattr(self, key, value)
        self.load_config()
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        self.current_box = QtGui.QDoubleSpinBox()
        self.current_box.setKeyboardTracking(False)
        self.current_box.setRange(*self.current_range)
        self.current_box.setSingleStep(self.current_stepsize)
        self.current_box.setDecimals(abs(int(np.floor(np.log10(self.current_stepsize)))))
        self.current_box.setAccelerated(True)
        self.power_box = QtGui.QDoubleSpinBox()
        self.power_box.setReadOnly(True)
        self.power_box.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.power_box.setDecimals(4)
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Current [A]: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.current_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Power [mW]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.setLayout(self.layout)
        self.setFixedSize(200, 100)

    @inlineCallbacks
    def connectSignals(self):
        self.hasNewState = False
        self.hasNewCurrent = False
        self.hasNewPower = False
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.current_box.valueChanged.connect(self.onNewCurrent)
        
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        for parameter in self.update_parameters:
            yield getattr(server, parameter)()
 
    def receive_update(self, c, signal):
        signal = json.loads(signal)
        for name, d in signal.items():
            self.free = False
            if name == self.name:
                if 'state' in self.update_parameters:
                    if d['state']:
                        self.state_button.setChecked(1)
                        self.state_button.setText('On')
                    else:
                        self.state_button.setChecked(0)
                        self.state_button.setText('Off')
                
                if 'current' in self.update_parameters:
                    self.current_box.setValue(d['current'])
    
                if 'power' in self.update_parameters:
                    self.power_box.setValue(d['power']*1e3)
        self.free = True
    
    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            is_on = yield server.state()
            if is_on:
                yield server.shutdown(True)
            else:
                yield server.warmup(True)

    def onNewCurrent(self):
        if self.free:
            self.hasNewCurrent = True
   
    def onNewPower(self):
        pass

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewCurrent:
            server = yield self.cxn.get_server(self.servername)
            yield server.current(self.current_box.value())
            self.hasNewCurrent = False

    def enterEvent(self, c):
        self.mouseHover.emit(True)
           
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class MultipleCurrentControl(QtGui.QWidget):
    def __init__(self, config_list, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.config_list = config_list
        self.reactor = reactor
        self.cxn = cxn
        self.connect()
 
    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        self.populateGUI()

    def populateGUI(self):
        self.layout = QtGui.QHBoxLayout()
        for config in self.config_list:
            widget = CurrentControl(config, self.reactor)
            self.layout.addWidget(widget)
        self.setFixedSize(200*len(self.config_list), 120)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        self.reactor.stop()
