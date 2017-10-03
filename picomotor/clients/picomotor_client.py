import json
import numpy as np
import sys
from time import sleep

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks

from client_tools.connection import connection
from client_tools.widgets import IntSpinBox

class PicomotorClient(QtGui.QGroupBox):
    def __init__(self, config, reactor, cxn=None):
        self.load_config(config)
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
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
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
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
        self.position_box = IntSpinBox(self.position_range)
        self.position_box.setFixedWidth(self.spinbox_width)
        self.position_box.display(0)
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        label = QtGui.QLabel('{}: '.format(self.name))
        label.setFixedWidth(50)

        self.layout.addWidget(label, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.position_box, 0, 1)
        
        self.setWindowTitle(self.name + '_client')
        self.setLayout(self.layout)
        self.setFixedSize(80 + self.spinbox_width, 40)

    @inlineCallbacks
    def connectSignals(self):
        self.hasNewPosition = False
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.position_box.returnPressed.connect(self.onNewPosition)
        
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
        self.free = False
        for name, d in signal.items():
            if 'position' in self.update_parameters and name == self.name:
                self.position_box.display(d['position'])
        self.free = True
    
    def onNewPosition(self):
        if self.free:
            self.hasNewPosition = True

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewPosition:
            server = yield self.cxn.get_server(self.servername)
            yield server.position(int(self.position_box.value()))
            self.hasNewPosition = False
    
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class MultiplePicomotorClient(QtGui.QWidget):
    def __init__(self, config_list, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.config_list = config_list
        self.reactor = reactor
        self.populateGUI()
        self.cxn = cxn
 
    def populateGUI(self):
        self.layout = QtGui.QHBoxLayout()
        for mirror_config in self.config_list:
            column = QtGui.QWidget()
            internal_layout = QtGui.QVBoxLayout()
            for axis_config in mirror_config:
                widget = PicomotorClient(axis_config, self.reactor)
                internal_layout.addWidget(widget)
            column.setLayout(internal_layout)
            self.layout.addWidget(column)
#        self.setFixedSize(80 + widget.spinbox_width, 40*len(self.config_list))
        self.setLayout(self.layout)

    def closeEvent(self, x):
        self.reactor.stop()
