from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json
from client_tools2 import NeatSpinBox

class SequenceParameterControl(QtGui.QGroupBox):
    hasNewValue = False
    free = True
    layout = None

    def __init__(self, configuration, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn
        self.loadControlConfiguration(configuration)
        self.connect()

    def loadControlConfiguration(self, configuration):
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            self.populateGUI()
            yield self.connectSignals()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def getServerConfiguratiom(self):
        yield None

    def populateGUI(self):
        self.nameBox = QtGui.QLineEdit()
        self.nameBox.setFixedWidth(self.spinBoxWidth)
        self.valueBox = NeatSpinBox()
        self.valueBox.setFixedWidth(self.spinBoxWidth)
        self.valueBox.display(1.)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(QtGui.QLabel('parameter: '), 1, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.nameBox, 1, 1)
        self.layout.addWidget(QtGui.QLabel('value: '), 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.valueBox, 2, 1)
        self.setLayout(self.layout)
        self.setFixedSize(100 + self.spinBoxWidth, 70)

    @inlineCallbacks
    def connectSignals(self):
        yield self.cxn.add_on_connect(self.servername, self.reinit)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.valueBox.returnPressed.connect(self.onNewValue)
        self.setMouseTracking(True)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.updateTime)

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewValue:
            name = str(self.nameBox.text())
            value = float(self.valueBox.value())
            server = yield self.cxn.get_server(self.servername)
            yield server.update_sequence_parameters(json.dumps({name: value}))
            self.hasNewValue = False

    def onNewValue(self):
        if self.free:
            self.hasNewValue = True

    @inlineCallbacks	
    def reinit(self): 
        self.setDisabled(False)
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id, context=self.context)
        yield server.addListener(listener=self.receive_update, source=None,
                                 ID=self.update_id, context=self.context)
        yield server.notify_listeners()


    def disable(self):
        print 'oh no!'
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class ControlConfig(object):
    def __init__(self):
        self.servername = 'yesr20_conductor'
        self.update_id = 461028
        self.updateTime = 100 # [ms]
        self.spinBoxWidth = 80

if __name__ == '__main__':
    import sys
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = SequenceParameterControl(ControlConfig(), reactor)
    widget.show()
    reactor.run()
