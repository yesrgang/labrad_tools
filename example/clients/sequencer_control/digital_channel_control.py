from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json

class DigitalManualControl(QtGui.QGroupBox):
    mouseHover = pyqtSignal(bool)
    layout = None

    def __init__(self, configuration, reactor=None, cxn=None):
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
        yield None

    def populateGUI(self):
        self.mode_button = QtGui.QPushButton()
        self.mode_button.setCheckable(1)
        self.mode_button.setFixedWidth(self.spinbox_width)

        self.manual_state_button = QtGui.QPushButton()
        self.manual_state_button.setCheckable(1)
        self.manual_state_button.setFixedWidth(self.spinbox_width)

        if self.layout is None:
            self.layout = QtGui.QGridLayout()

        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.mode_button, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Manual State: '), 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.manual_state_button, 2, 1)
        self.setLayout(self.layout)
        self.setFixedSize(150 + self.spinbox_width, 70)

    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None,
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.mode_button.released.connect(self.onNewMode)
        self.manual_state_button.released.connect(self.onNewManualState)
        self.setMouseTracking(True)
        self.mouseHover.connect(self.requestValues)
#        self.timer = QtCore.QTimer(self)
#        self.timer.timeout.connect(self.writeValues)
#        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        yield server.notify_listeners()

    def receive_update(self, c, signal):
        self.free = False
        signal = json.loads(signal)
        for s in signal:
            if signal[s]['name'] == self.name:
                update = signal[s]
        if update['mode'] == 'manual':
            self.mode_button.setChecked(1)
            self.mode_button.setText('Manual')
        else:
            self.mode_button.setChecked(0)
            self.mode_button.setText('Auto')
        if update['manual_state'] == True:
            self.manual_state_button.setChecked(1)
            self.manual_state_button.setText('On')
        else:
            self.manual_state_button.setChecked(0)
            self.manual_state_button.setText('Off')
        self.free = True

    def enterEvent(self, c):
        self.mouseHover.emit(True)

    def leaveEvent(self, c):
        self.mouseHover.emit(True)

    @inlineCallbacks
    def onNewMode(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            mode = yield server.channel_mode(self.name)
            if mode == 'manual':
                yield server.channel_mode(self.name, 'auto')
            else:
                yield server.channel_mode(self.name, 'manual')
    
    @inlineCallbacks
    def onNewManualState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            state = yield server.channel_manual_state(self.name)
            yield server.channel_manual_state(self.name, not state)

    @inlineCallbacks
    def reinitialize(self):
        pass

    def disable(self):
        self.setDisabled(True)

#    def closeEvent(self, x):
#        self.reactor.stop()

class ControlConfig(object):
    def __init__(self):
        self.name = '3D MOT AOM'
        self.servername = 'yesr20_digital_sequencer'
        self.update_id = 461024
        self.update_time = 100 # [ms]

        self.spinbox_width = 80

class ManyChannels(QtGui.QWidget):
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.channels = ['3D MOT AOM@A00', '3D MOT Shutter', '2D Mot Shutter', 'Zeeman Shutter']
        self.reactor = reactor
        self.cxn = cxn
#        self.populateGUI()
        self.connect()

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            self.populateGUI()
        except Exception, e:
            print e
            self.setDisabled(True)

    def populateGUI(self):
        self.layout = QtGui.QHBoxLayout()
        for c in self.channels:
            conf = ControlConfig()
            conf.name = c
            w = DigitalManualControl(conf, reactor, self.cxn)
            self.layout.addWidget(w)
        self.setLayout(self.layout)
        print '!'


if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = DigitalManualControl(ControlConfig(), reactor)
#    widget = ManyChannels(reactor)
    widget.show()
    reactor.run()
