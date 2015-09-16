from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
from client_tools import SuperSpinBox

class CWControl(QtGui.QGroupBox):
    hasNewFrequency = False
    hasNewPower = False
    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, configuration_filename, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.configuration_filename = configuration_filename
        self.reactor = reactor
        self.cxn = cxn 
        self.load_control_configuration()
        self.connect()

    def load_control_configuration(self):
        self.configuration = __import__(self.configuration_filename).RFControlConfig()
        for key, value in self.configuration.__dict__.items():
            setattr(self, key, value)

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
        server = yield self.cxn.get_server(self.servername)
        serverconf_str = yield server.select_device_by_name(self.name)
        for key, value in eval(serverconf_str).iteritems():
            setattr(self, key, value)

    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.frequency_box = SuperSpinBox(self.frequency_range, self.frequency_units, self.frequency_digits)
        #self.frequency_box = QtGui.QDoubleSpinBox()
        #self.frequency_box.setKeyboardTracking(False)
        #self.frequency_box.setRange(self.min_frequency, self.max_frequency)
        #self.frequency_box.setSingleStep(self.frequency_stepsize)
        #self.frequency_box.setDecimals(abs(int(np.floor(np.log10(self.frequency_stepsize)))))
        #self.frequency_box.setAccelerated(True)
        self.frequency_box.setFixedWidth(self.spinbox_width)
        self.frequency_box.display(0)
        
        self.amplitude_box = SuperSpinBox(self.amplitude_range, self.amplitude_units, self.amplitude_digits)
        #self.amplitude_box = QtGui.QDoubleSpinBox()
        #self.amplitude_box.setKeyboardTracking(False)
        #self.amplitude_box.setRange(self.min_amplitude, self.max_amplitude)
        #self.amplitude_box.setSingleStep(self.amplitude_stepsize)
        #self.amplitude_box.setDecimals(abs(int(np.floor(np.log10(self.amplitude_stepsize)))))
        #self.amplitude_box.setAccelerated(True)
        self.amplitude_box.setFixedWidth(self.spinbox_width)
        self.amplitude_box.display(0)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Frequency: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequency_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Amplitude: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitude_box, 3, 1)

	self.setWindowTitle(self.name + ' control')
        self.setLayout(self.layout)
        self.setFixedSize(100 + self.spinbox_width, 100)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update_state(self.state_id)
        yield server.addListener(listener=self.receive_state, source=None, ID=self.state_id)
        yield server.signal__update_frequency(self.frequency_id)
        yield server.addListener(listener=self.receive_frequency, source=None, ID=self.frequency_id)
        yield server.signal__update_amplitude(self.amplitude_id)
        yield server.addListener(listener=self.receive_amplitude, source=None, ID=self.amplitude_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.state_button.released.connect(self.onNewState)
        #self.frequency_box.valueChanged.connect(self.onNewFrequency)
        self.frequency_box.returnPressed.connect(self.onNewFrequency)
        #self.amplitude_box.valueChanged.connect(self.onNewPower)
        self.amplitude_box.returnPressed.connect(self.onNewPower)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        yield server.request_values()
 
    def receive_state(self, c, signal):
        self.free = False
        instrument, state = signal
        if instrument == self.name:
            if state:
                self.state_button.setChecked(1)
                self.state_button.setText('On')
            else:
                self.state_button.setChecked(0)
                self.state_button.setText('Off')
        self.free = True

    def receive_frequency(self, c, signal):
        self.free = False
        instrument, frequency = signal
        if instrument == self.name:
            self.frequency_box.display(frequency)
        self.free = True

    def receive_amplitude(self, c, signal):
        self.free = False
        instrument, amplitude = signal
        if instrument == self.name:
            self.amplitude_box.display(amplitude)
        self.free = True
    
    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            is_on = yield server.state()
            yield server.state(not is_on)

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewFrequency:
            server = yield self.cxn.get_server(self.servername)
            yield server.frequency(self.frequency_box.value())
            self.hasNewFrequency = False
        elif self.hasNewPower:
            server = yield self.cxn.get_server(self.servername)
            yield server.amplitude(self.amplitude_box.value())
            self.hasNewPower = False

    def onNewFrequency(self):
        if self.free:
            self.hasNewFrequency = True
   
    def onNewPower(self):
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

    def closeEvent(self, x):
        self.reactor.stop()

#if __name__ == '__main__':
#    a = QtGui.QApplication([])
#    import qt4reactor 
#    qt4reactor.install()
#    from twisted.internet import reactor
#    widget = CWControl('beta_offset_config', reactor)
#    widget.show()
#    reactor.run()
