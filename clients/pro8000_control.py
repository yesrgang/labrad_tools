from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
from client_tools import SuperSpinBox
import numpy as np

update_time = 100 # [ms]
servername = 'yesr13 PRO8000'

class LDC80xxClient(QtGui.QGroupBox):
    state_id = 461001
    current_id = 461002
    power_id = 461003
    hasNewCurrent = False
    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, configuration_filename, diode_name, reactor, cxn=None):
        self.configuration_filename = configuration_filename
        self.diode_name = diode_name
        self.reactor = reactor
        self.cxn = cxn 
        self.load_control_configuration()
        QtGui.QDialog.__init__(self)
        self.connect()
        #print self.gpib_device_id

    def load_control_configuration(self):
        self.configuration = __import__(self.configuration_filename).PRO8000Config()
        for key, value in self.configuration.__dict__.items():
            if key == 'diodes':
                for key2, value2 in self.configuration.diodes[self.diode_name].__dict__.items():
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.get_server_configuration()
            self.populateGUI()
            yield self.connectSignals()
            yield self.requestValues()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def get_server_configuration(self):
        server = yield self.cxn.get_server(self.servername)
        sysconf_str = yield server.get_system_configuration()
        for key, value in eval(sysconf_str).iteritems():
            setattr(self, key, value)
        yield server.select_device(self.gpib_device_id)
        ctlconf_str = yield server.get_controller_configuration(self.diode_name)
        for key, value in eval(ctlconf_str).iteritems():
            setattr(self, key, value)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        self.current_box = QtGui.QDoubleSpinBox()
        self.current_box.setKeyboardTracking(False)
        self.current_box.setRange(self.min_current, self.max_current)
        self.current_box.setSingleStep(self.step_size)
        self.current_box.setDecimals(abs(int(np.floor(np.log10(self.step_size)))))
        self.current_box.setAccelerated(True)
        self.power_box = QtGui.QDoubleSpinBox()
        self.power_box.setReadOnly(True)
        self.power_box.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.power_box.setDecimals(4)
        if self.layout is None:
            self.layout = QtGui.QGridLayout()
        self.layout.addWidget(QtGui.QLabel('<b>'+self.diode_name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Current [A]: '), 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.current_box, 2, 1)
        self.layout.addWidget(QtGui.QLabel('Power [mW]: '), 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.setLayout(self.layout)
        self.setFixedSize(200, 100)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update_state(self.state_id)
        yield server.addListener(listener=self.receiveState, source=None, ID=self.state_id)
        yield server.signal__update_current(self.current_id)
        yield server.addListener(listener=self.receiveCurrent, source=None, ID=self.current_id)
        yield server.signal__update_power(self.power_id)
        yield server.addListener(listener=self.receivePower, source=None, ID=self.power_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.current_box.valueChanged.connect(self.onNewCurrent)
        self.state_button.released.connect(self.onNewState)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeCurrent)
        self.timer.start(update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        yield server.request_values(self.diode_name)
 
    def receiveState(self, c, signal):
        self.free = False
        (diode_name, state) = signal
        if diode_name == self.diode_name: 
            if state:
                self.state_button.setChecked(1)
                self.state_button.setText('On')
            else:
                self.state_button.setChecked(0)
                self.state_button.setText('Off')
        self.free = True

    def receiveCurrent(self, c, signal):
        self.free = False
        (diode_name, current) = signal
        if diode_name == self.diode_name:
            self.current_box.setValue(current)
        self.free = True

    def receivePower(self, c, signal):
        self.free = False
        (diode_name, power) = signal
        if diode_name == self.diode_name:
            self.power_box.setValue(power*1e3)
        self.free = True
    
    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            is_on = yield server.state(self.diode_name)
            yield server.state(self.diode_name, not is_on)

    @inlineCallbacks
    def writeCurrent(self):
        if self.hasNewCurrent:
            server = yield self.cxn.get_server(self.servername)
            yield server.current(self.diode_name, self.current_box.value())
        self.hasNewCurrent = False

    def onNewCurrent(self, c):
        if self.free:
            self.hasNewCurrent = True
    
    def removeWidgets(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            self.layout.removeWidget(w)
            w.close()
                
    @inlineCallbacks
    def reinitialize(self):
        yield self.getConfiguration()
#        self.removeWidgets()
#        self.setDisabled(False)
#        yield self.connect()

    def disable(self):
        self.setDisabled(True)

#    def closeEvent(self, x):
#        self.reactor.stop()

class StateWidget(QtGui.QGroupBox):
    layout = None
    def __init__(self, reactor, cxn=None):
        self.servername = servername
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
            yield self.getConfiguration()
            self.populateGUI()
            yield self.connectSignals()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def getConfiguration(self):
        server = yield self.cxn.get_server(self.servername)
        sysconf_str = yield server.get_system_configuration()
        self.sysconf = eval(sysconf_str)
        yield server.select_device(self.sysconf['gpib_device_id'])
   
    def populateGUI(self):
        self.on_button = QtGui.QPushButton('On')
        self.off_button = QtGui.QPushButton('Off')
        if self.layout is None:
            self.layout = QtGui.QGridLayout()
        self.layout.addWidget(QtGui.QLabel('<b>ALL</b>'), 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.on_button, 1, 0)
        self.layout.addWidget(self.off_button, 2, 0)
        self.setLayout(self.layout)
        self.setFixedSize(120, 100)

    @inlineCallbacks
    def connectSignals(self):
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)
        self.on_button.clicked.connect(self.powerOn)
        self.off_button.clicked.connect(self.powerOff)

    @inlineCallbacks
    def powerOn(self, c):
        server = yield self.cxn.get_server(self.servername)
        yield server.system_state(True)

    @inlineCallbacks
    def powerOff(self, c):
        server = yield self.cxn.get_server(self.servername)
        yield server.system_state(False)

    def removeWidgets(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            self.layout.removeWidget(w)
            w.close()
                
    @inlineCallbacks
    def reinitialize(self):
        yield None
#         self.removeWidgets()
#         self.setDisabled(False)
#         yield self.connect()

    def disable(self):
        self.setDisabled(True)

#    def closeEvent(self, x):
#        self.reactor.stop()

class PRO8000Client(QtGui.QWidget):
    layout = None
    def __init__(self, reactor, cxn=None):
        self.servername = servername
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
            yield self.loadConfiguration()
            self.populateGUI()
            yield self.connectSignals()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def loadConfiguration(self):
        server = yield self.cxn.get_server(self.servername)
        sysconf_str = yield server.get_system_configuration()
        self.sysconf = eval(sysconf_str)

    def populateGUI(self):
        self.setWindowTitle(self.servername + ' Control')
        if self.layout is None:
            self.layout = QtGui.QHBoxLayout()
        for diode_name in self.sysconf['controller_order']:
            widget = LDC80xxWidget(diode_name, self.reactor, self.cxn)
            self.layout.addWidget(widget)
        widget = StateWidget(self.reactor)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        self.setFixedSize(200*len(self.sysconf['controller_order'])+150, 120)

    @inlineCallbacks
    def connectSignals(self):
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)
    
    def removeWidgets(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            self.layout.removeWidget(w)
            w.close()
                
    @inlineCallbacks
    def reinitialize(self):
        self.removeWidgets()
        self.setDisabled(False)
        yield self.loadConfiguration()
        self.populateGUI()

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = PRO8000Client(reactor)
    widget = LDC80xxClient('pro8000_config', '2D', reactor)
    widget.show()
    reactor.run()
