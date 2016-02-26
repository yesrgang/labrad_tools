from PyQt4 import QtGui
from rf_control3 import CWControl
from connection import connection
from twisted.internet.defer import inlineCallbacks

class RFControlConfig(object):
    def __init__(self):
        self.servername = 'yesr20_6dds'
        self.name = 'HODT AOM'
        self.update_id = 461100
        
        self.frequency_units = [(6, 'MHz')]
        self.frequency_digits = 4
        self.amplitude_units = [(0, 'arb')]
        self.amplitude_digits = 2
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100

class ManyChannels(QtGui.QWidget):
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.channels = ['HODT AOM', 'VODT AOM', 'dimple AOM']
        self.reactor = reactor
        self.cxn = cxn
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
            conf = RFControlConfig()
            conf.name = c
            w = CWControl(conf, reactor, self.cxn)
            self.layout.addWidget(w)
	    h = w.height()
	    wid = w.width()
        self.setFixedSize(650, 120) #wid*len(self.channels), h)
        self.setLayout(self.layout)


if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = ManyChannels(reactor)
    widget.show()
    reactor.run()
