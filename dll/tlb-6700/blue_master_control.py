from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json
from client_tools import SuperSpinBox

class TLB6700Control(QtGui.QGroupBox):
    hasNewPiezoVoltage = False
    hasNewDiodeCurrent = False
    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, configuration, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn
        self.load_control_configuration(configuration)
        self.connect()

    def load_control_configuration(self, configuration):
        for key, value in configuration.__dict__.items():
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
        serverconf_str = yield server.get_configuration()
        for key, value in json.loads(serverconf_str).items():
            setattr(self, key, value)

    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        self.state_button.setFixedWidth(self.spinbox_width)

        self.lock_button = QtGui.QPushButton()
        self.lock_button.setCheckable(1)
        self.lock_button.setFixedWidth(self.spinbox_width)

        self.piezo_voltage_box = SuperSpinBox(self.piezo_voltage_range,
                                              self.piezo_voltage_units,
                                              self.piezo_voltage_digits)
        self.piezo_voltage_box.setFixedWidth(self.spinbox_width)
        self.piezo_voltage_box.display(0)

        self.diode_current_box = SuperSpinBox(self.diode_current_range,
                                              self.diode_current_units,
                                              self.diode_current_digits)
        self.diode_current_box.setFixedWidth(self.spinbox_width)
        self.diode_current_box.display(0)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        
        self.layout.addWidget(QtGui.QLabel('Digital PID: '), 2, 0,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lock_button, 2, 1)
        
        self.layout.addWidget(QtGui.QLabel('Piezo Voltage: '), 3, 0,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.piezo_voltage_box, 3, 1)
        
        self.layout.addWidget(QtGui.QLabel('Diode Curent: '), 4, 0,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.diode_current_box, 4, 1)
        self.setLayout(self.layout)
        
        self.setWindowTitle(self.servername + ' control')
        self.setFixedSize(120 + self.spinbox_width, 125)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None,
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.lock_button.released.connect(self.onNewLockState)
        self.piezo_voltage_box.returnPressed.connect(self.onNewPiezoVoltage)
        self.diode_current_box.returnPressed.connect(self.onNewPower)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        yield server.request_values()

    def receive_update(self, c, signal):
        self.free = False
        update = json.loads(signal)
        if update['laser_state']:
            self.state_button.setChecked(1)
            self.state_button.setText('On')
        else:
            self.state_button.setChecked(0)
            self.state_button.setText('Off')
        if update['lock_state']:
            self.lock_button.setChecked(1)
            self.lock_button.setText('On')
        else:
            self.lock_button.setChecked(0)
            self.lock_button.setText('Off')
        self.piezo_voltage_box.display(update['piezo_voltage'])
        self.diode_current_box.display(update['diode_current'])
        self.free = True

    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            is_on = yield server.laser_state()
            yield server.laser_state(not is_on)

    @inlineCallbacks
    def onNewLockState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            is_on = yield server.set_digital_lock_state()
            yield server.set_digital_lock_state(not is_on)

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewPiezoVoltage:
            server = yield self.cxn.get_server(self.servername)
            yield server.piezo_voltage(self.piezo_voltage_box.value())
            self.hasNewPiezoVoltage = False
        elif self.hasNewDiodeCurrent:
            server = yield self.cxn.get_server(self.servername)
            yield server.diode_current(self.diode_current_box.value())
            self.hasNewDiodeCurrent = False

    def onNewPiezoVoltage(self):
        if self.free:
            self.hasNewPiezoVoltage = True

    def onNewPower(self):
        if self.free:
            self.hasNewDiodeCurrent = True

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
class ControlConfig(object):
    def __init__(self):
        self.name = 'Blue Master'
        self.servername = 'yesr20_tlb_6700'
        self.update_id = 461022
        self.update_time = 100 # [ms]

        self.diode_current_units = [(0, 'mA')]
        self.diode_current_digits = 1
        self.piezo_voltage_units = [(0, '%')]
        self.piezo_voltage_digits = 2
        self.spinbox_width = 80

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = TLB6700Control(ControlConfig(), reactor)
    widget.show()
    reactor.run()
