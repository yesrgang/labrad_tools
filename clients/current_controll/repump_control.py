from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json
from client_tools import SuperSpinBox

class LDC340Control(QtGui.QGroupBox):
    hasNewCurrent = False
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
        yield self.get_server_configuration()
        self.populateGUI()
        yield self.connectSignals()
        yield self.requestValues()

    @inlineCallbacks
    def get_server_configuration(self):
        server = yield self.cxn.get_server(self.servername)
        serverconf_str = yield server.select_device_by_name(self.name)
        for key, value in json.loads(serverconf_str).items():
            setattr(self, key, value)

    def populateGUI(self):
        self.stateButton = QtGui.QPushButton()
        self.stateButton.setCheckable(1)
        self.stateButton.setFixedWidth(self.spinbox_width)

        self.currentBox = SuperSpinBox(self.current_range,
                                       self.current_units,
                                       self.current_digits)
        self.currentBox.setFixedWidth(self.spinbox_width)
        self.currentBox.display(0)

        self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.stateButton, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Current: '), 2, 0,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.currentBox, 2, 1)
        self.setLayout(self.layout)
	self.setWindowTitle(self.servername + ' control')
        self.setFixedSize(120 + self.spinbox_width, 80)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receiveUpdate, source=None,
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.stateButton.released.connect(self.onNewState)
        self.currentBox.returnPressed.connect(self.onNewCurrent)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        yield server.send_update()

    def receiveUpdate(self, c, signal):
        self.free = False
        update = json.loads(signal)
        if update.has_key('state'):
            if update['state']:
                self.stateButton.setChecked(1)
                self.stateButton.setText('On')
            else:
                self.stateButton.setChecked(0)
                self.stateButton.setText('Off')
        if update.has_key('current'):
            self.currentBox.display(update['current'])
        self.free = True

    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        pass
        #self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            is_on = yield server.state()
            yield server.state(not is_on)

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewCurrent:
            server = yield self.cxn.get_server(self.servername)
            yield server.current(self.currentBox.value())
            self.hasNewCurrent = False

    def onNewPiezoVoltage(self):
        if self.free:
            self.hasNewPiezoVoltage = True

    def onNewCurrent(self):
        if self.free:
            self.hasNewCurrent = True

    @inlineCallbacks
    def reinitialize(self):
        yield self.get_configuration()

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()


class ControlConfig(object):
    def __init__(self):
        self.name = '707'
        self.servername = 'ldc340'
        self.update_id = 461027
        self.update_time = 100 # [ms]

        self.current_units = [(-3, 'mA')]
        self.current_digits = 2
        self.spinbox_width = 80

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = LDC340Control(ControlConfig(), reactor)
    widget.show()
    reactor.run()
