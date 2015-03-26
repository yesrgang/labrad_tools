from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

class CWControl(QtGui.QGroupBox):
    hasNewFrequency = False
    hasNewPower = False
    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, widget_config, reactor, cxn=None):
        self.wconfig = widget_config
        #self.init_server_relationship = widget_config.init_server_relationship(self)
        for key, value in self.wconfig.__dict__.items():
            setattr(self, key, value) # house server_name, get_server_config
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
            self.populateGUI()
            yield self.connectSignals()
            yield self.requestValues()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def select_device(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.select_device_by_name(self.name)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.frequency_box = QtGui.QDoubleSpinBox()
        self.frequency_box.setKeyboardTracking(False)
        self.frequency_box.setRange(self.min_frequency, self.max_frequency)
        self.frequency_box.setSingleStep(self.frequency_stepsize)
        self.frequency_box.setDecimals(abs(int(np.floor(np.log10(self.frequency_stepsize)))))
        self.frequency_box.setAccelerated(True)
        self.frequency_box.setFixedWidth(self.spinbox_width)
        
        self.power_box = QtGui.QDoubleSpinBox()
        self.power_box.setKeyboardTracking(False)
        self.power_box.setRange(self.min_power, self.max_power)
        self.power_box.setSingleStep(self.power_stepsize)
        self.power_box.setDecimals(abs(int(np.floor(np.log10(self.power_stepsize)))))
        self.power_box.setAccelerated(True)
        self.power_box.setFixedWidth(self.spinbox_width)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Frequency [MHz]: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequency_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Power [dBm]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.setLayout(self.layout)
        self.setFixedSize(140 + self.spinbox_width, 100)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.signal__update_state(self.state_id)
        yield server.addListener(listener=self.receive_state, source=None, ID=self.state_id)
        yield server.signal__update_frequency(self.frequency_id)
        yield server.addListener(listener=self.receive_frequency, source=None, ID=self.frequency_id)
        yield server.signal__update_power(self.power_id)
        yield server.addListener(listener=self.receive_power, source=None, ID=self.power_id)
        yield self.cxn.add_on_connect(self.server_name, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.server_name, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.frequency_box.valueChanged.connect(self.onNewFrequency)
        self.power_box.valueChanged.connect(self.onNewPower)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.server_name)
        yield server.request_values()
 
    def receive_state(self, c, signal):
        self.free = False
        state = signal
        if state:
            self.state_button.setChecked(1)
            self.state_button.setText('On')
        else:
            self.state_button.setChecked(0)
            self.state_button.setText('Off')
        self.free = True

    def receive_frequency(self, c, signal):
        self.free = False
        frequency = signal
        self.frequency_box.setValue(frequency)
        self.free = True

    def receive_power(self, c, signal):
        self.free = False
        power = signal
        self.power_box.setValue(power)
        self.free = True
    
    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.server_name)
            is_on = yield server.state()
            yield server.state(not is_on)

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewFrequency:
            server = yield self.cxn.get_server(self.server_name)
            yield server.frequency(self.frequency_box.value())
            self.hasNewFrequency = False
        elif self.hasNewPower:
            server = yield self.cxn.get_server(self.server_name)
            yield server.power(self.power_box.value())
            self.hasNewPower = False

    def onNewFrequency(self, c):
        if self.free:
            self.hasNewFrequency = True
   
    def onNewPower(self, c):
        if self.free:
            self.hasNewPower = True

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

#    def closeEvent(self, x):
#        self.reactor.stop()

class SweepControl(QtGui.QGroupBox):
    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, widget_config, reactor, cxn=None):
        self.wconfig = widget_config
        for key, value in self.wconfig.__dict__.items():
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
            self.populateGUI()
            yield self.connectSignals()
            yield self.requestValues()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def select_device(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.select_device_by_name(self.name)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.sweeprate_box = QtGui.QDoubleSpinBox()
        self.sweeprate_box.setKeyboardTracking(False)
        self.sweeprate_box.setRange(self.min_frequency, self.max_frequency)
        self.sweeprate_box.setSingleStep(self.frequency_stepsize)
        self.sweeprate_box.setDecimals(abs(int(np.floor(np.log10(self.frequency_stepsize)))))
        self.sweeprate_box.setAccelerated(True)
        self.sweeprate_box.setFixedWidth(self.spinbox_width)
        
        self.power_box = QtGui.QDoubleSpinBox()
        self.power_box.setKeyboardTracking(False)
        self.power_box.setRange(self.min_power, self.max_power)
        self.power_box.setSingleStep(self.power_stepsize)
        self.power_box.setDecimals(abs(int(np.floor(np.log10(self.power_stepsize)))))
        self.power_box.setAccelerated(True)
        self.power_box.setFixedWidth(self.spinbox_width)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Sweep Rate [Hz/s]: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.sweeprate_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Power [dBm]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.setLayout(self.layout)
        self.setFixedSize(140 + self.spinbox_width, 100)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.signal__update_state(self.state_id)
        yield server.addListener(listener=self.receive_state, source=None, ID=self.state_id)
        yield server.signal__update_frequency(self.frequency_id)
        yield server.addListener(listener=self.receive_frequency, source=None, ID=self.frequency_id)
        yield server.signal__update_power(self.power_id)
        yield server.addListener(listener=self.receive_power, source=None, ID=self.power_id)
        yield self.cxn.add_on_connect(self.server_name, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.server_name, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.sweeprate_box.valueChanged.connect(self.onNewFrequency)
        self.power_box.valueChanged.connect(self.onNewPower)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.server_name)
        yield server.request_values()
 
    def receive_state(self, c, signal):
        self.free = False
        state = signal
        if state:
            self.state_button.setChecked(1)
            self.state_button.setText('On')
        else:
            self.state_button.setChecked(0)
            self.state_button.setText('Off')
        self.free = True

    def receive_frequency(self, c, signal):
        self.free = False
        frequency = signal
        self.sweeprate_box.setValue(frequency)
        self.free = True

    def receive_power(self, c, signal):
        self.free = False
        power = signal
        self.power_box.setValue(power)
        self.free = True
    
    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.server_name)
            is_on = yield server.state()
            yield server.state(not is_on)

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewFrequency:
            server = yield self.cxn.get_server(self.server_name)
            yield server.frequency(self.sweeprate_box.value())
            self.hasNewFrequency = False
        elif self.hasNewPower:
            server = yield self.cxn.get_server(self.server_name)
            yield server.power(self.power_box.value())
            self.hasNewPower = False

    def onNewFrequency(self, c):
        if self.free:
            self.hasNewFrequency = True
   
    def onNewPower(self, c):
        if self.free:
            self.hasNewPower = True

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

#    def closeEvent(self, x):
#        self.reactor.stop()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    from dds_rfconfig import BetaRFConfig
    conf = BetaRFConfig()
    widget = CWControl(conf, reactor)
    widget.show()
    reactor.run()
