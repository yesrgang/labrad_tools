from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

class CWControl(QtGui.QGroupBox):
    hasNewState = False
    hasNewFrequency = False
    hasNewAmplitude = False
    hasNewSweepState = False
    hasNewSweepRate = False
#    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, widget_config, reactor, cxn=None):
        self.wconfig = widget_config
        for key, value in self.wconfig.__dict__.items():
            setattr(self, key, value) # house server_name
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
        confstr = yield server.select_device_by_name(self.name)
        for key, value in eval(confstr).iteritems():
            setattr(self, key, value)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.frequency_box = QtGui.QDoubleSpinBox()
        self.frequency_box.setKeyboardTracking(False)
        self.frequency_range = tuple([x/self.frequency_units for x in self.frequency_range])
        self.frequency_box.setRange(*self.frequency_range)
        self.frequency_box.setSingleStep(self.frequency_stepsize)
        self.frequency_box.setDecimals(abs(int(np.floor(np.log10(self.frequency_stepsize*self.frequency_units)))))
        self.frequency_box.setAccelerated(True)
        self.frequency_box.setFixedWidth(self.spinbox_width)
        
        self.amplitude_box = QtGui.QDoubleSpinBox()
        self.amplitude_box.setKeyboardTracking(False)
        self.amplitude_box.setRange(*self.amplitude_range)
        self.amplitude_box.setSingleStep(self.amplitude_stepsize)
        self.amplitude_box.setDecimals(abs(int(np.floor(np.log10(self.amplitude_stepsize)))))
        self.amplitude_box.setAccelerated(True)
        self.amplitude_box.setFixedWidth(self.spinbox_width)
        
        self.sweepstate_button = QtGui.QPushButton()
        self.sweepstate_button.setCheckable(1)
        
        self.sweeprate_box = QtGui.QDoubleSpinBox()
        self.sweeprate_box.setKeyboardTracking(False)
        self.sweeprate_box.setRange(*self.sweeprate_range)
        self.sweeprate_box.setSingleStep(self.sweeprate_stepsize)
        self.sweeprate_box.setDecimals(abs(int(np.floor(np.log10(self.sweeprate_stepsize)))))
        self.sweeprate_box.setAccelerated(True)
        self.sweeprate_box.setFixedWidth(self.spinbox_width)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Frequency [MHz]: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequency_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Amplitude [Arb.]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitude_box, 3, 1)
        self.layout.addWidget(QtGui.QLabel('Sweep State: '), 4, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.sweepstate_button, 4, 1)
        self.layout.addWidget(QtGui.QLabel('Sweep Rate [Hz/s]: '), 5, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.sweeprate_box, 5, 1)
        self.setLayout(self.layout)
        self.setFixedSize(150 + self.spinbox_width, 166)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.server_name)
        yield server.signal__update_values(self.update_id)
        yield server.addListener(listener=self.receive_values, source=None, ID=self.update_id)
#        yield server.signal__update_state(self.state_id)
#        yield server.addListener(listener=self.receive_state, source=None, ID=self.state_id)
#        yield server.signal__update_frequency(self.frequency_id)
#        yield server.addListener(listener=self.receive_frequency, source=None, ID=self.frequency_id)
#        yield server.signal__update_amplitude(self.amplitude_id)
#        yield server.addListener(listener=self.receive_amplitude, source=None, ID=self.amplitude_id)
        yield self.cxn.add_on_connect(self.server_name, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.server_name, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.frequency_box.valueChanged.connect(self.onNewFrequency)
        self.amplitude_box.valueChanged.connect(self.onNewAmplitude)
        self.sweepstate_button.released.connect(self.onNewSweepState)
        self.sweeprate_box.editingFinished.connect(self.onNewSweepRate)
        self.setMouseTracking(True)
#        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)
        
        self.free = True

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.server_name)
        yield server.request_values(self.name)
 
#    def receive_state(self, c, signal):
#        name, state = signal
#        if name = self.name:
#            self.free = False
#            if state:
#                self.state_button.setChecked(1)
#                self.state_button.setText('On')
#            else:
#                self.state_button.setChecked(0)
#                self.state_button.setText('Off')
#            self.free = True
#
#    def receive_frequency(self, c, signal):
#        name, frequency = signal
#        if name = self.name:
#            self.free = False
#            self.frequency_box.setValue(frequency)
#            self.free = True
#
#    def receive_amplitude(self, c, signal):
#        name, amplitude = signal
#        if name = self.name:
#            self.free = False
#            self.amplitude_box.setValue(amplitude)
#            self.free = True
    
#    def enterEvent(self, c):
#        self.mouseHover.emit(True)
#
#    def leaveEvent(self, c):
#        self.mouseHover.emit(True)

    def receive_values(self, c, signal):
        name, state, frequency, amplitude, sweepstate, sweeprate = signal
        if name == self.name:
            self.free = False
            if state:
                self.state_button.setChecked(1)
                self.state_button.setText('On')
            else:
                self.state_button.setChecked(0)
                self.state_button.setText('Off')
            if not self.frequency_box.hasFocus():
                self.frequency_box.setValue(frequency/self.frequency_units)
            if not self.amplitude_box.hasFocus():
                self.amplitude_box.setValue(amplitude)
            if sweepstate:
                self.sweepstate_button.setChecked(1)
                self.sweepstate_button.setText('On')
            else:
                self.sweepstate_button.setChecked(0)
                self.sweepstate_button.setText('Off')
            if not self.sweeprate_box.hasFocus():
                self.sweeprate_box.setValue(sweeprate)
            self.free = True

    def onNewState(self):
        if self.free:
            self.hasNewState = True

    def onNewFrequency(self, c):
        if self.free:
            self.hasNewFrequency = True
   
    def onNewAmplitude(self, c):
        if self.free:
            self.hasNewAmplitude = True

    def onNewSweepState(self):
        if self.free:
            self.hasNewSweepState = True

    def onNewSweepRate(self):
        if self.free:
            self.hasNewSweepRate = True

    @inlineCallbacks
    def writeValues(self):
        if  self.hasNewState:
            server = yield self.cxn.get_server(self.server_name)
            is_on = yield server.state(self.name)
            yield server.state(self.name, not is_on)
            self.hasNewState = False
        elif self.hasNewFrequency:
            server = yield self.cxn.get_server(self.server_name)
            yield server.frequency(self.name, self.frequency_box.value()*self.frequency_units)
            self.hasNewFrequency = False
        elif self.hasNewAmplitude:
            server = yield self.cxn.get_server(self.server_name)
            yield server.amplitude(self.name, self.amplitude_box.value())
            self.hasNewAmplitude = False
        elif self.hasNewSweepState:
            server = yield self.cxn.get_server(self.server_name)
            is_on = yield server.sweepstate(self.name)
            yield server.sweepstate(self.name, not is_on)
            self.hasNewSweepState = False
        elif self.hasNewSweepRate:
            server = yield self.cxn.get_server(self.server_name)
            yield server.sweeprate(self.name, self.sweeprate_box.value())
            self.hasNewSweepRate = False
                
    @inlineCallbacks
    def reinitialize(self):
        yield self.get_configuration()

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    from redmaster_config import RedMasterConfig
    conf = RedMasterConfig()
    widget = CWControl(conf, reactor)
    widget.show()
    reactor.run()
