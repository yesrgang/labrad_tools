import json
import h5py
import os
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from client_tools.connection import connection

class MplCanvas(FigureCanvas):
    def __init__(self):
#        self.fig = Figure()
#        self.axes = self.fig.add_subplot(111)
        fig, ax = plt.subplots(1)
        self.fig = fig
        self.ax = ax

        self.fig.set_tight_layout(True)

        FigureCanvas.__init__(self, self.fig)
        self.setFixedSize(600, 300)

#    def plot(self, y, label=None):
#        self.ax.set_xlabel('time [s]')
#        self.ax.set_ylabel('voltage [V]')
#        self.ax.plot(y, label=label)
#        self.ax.legend()

class PMTViewer(QtGui.QDialog):
    data_dir = 'Z:\\SrQ\\new_data\\'

    def __init__(self, pmt_name, reactor, cxn=None):
        super(PMTViewer, self).__init__(None)
        self.pmt_name = pmt_name
        self.reactor = reactor
        self.cxn = cxn

        self.update_id = np.random.randint(0, 2**31 - 1)
#        self.update_id = 6100034
        self.loading = False
        self.connect()
   
    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            cname = 'pmt - {} - client'.format(self.pmt_name)
            yield self.cxn.connect(name=cname)
#        self.context = yield self.cxn.context()

        self.populate()
        yield self.connect_signals()
        #self.replot()

    def populate(self):
        self.setWindowTitle(self.pmt_name)
        self.canvas = MplCanvas()
        self.nav = NavigationToolbar(self.canvas, self)
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addWidget(self.nav)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
       
        width = self.canvas.width()
        height = self.nav.height() + self.canvas.height() + 20
        self.setFixedSize(width, height)
        self.setWindowTitle('pmt_viewer')
#        yield self.replot()

    @inlineCallbacks
    def connect_signals(self):
        # pyqt signals

        # labrad signals
        pmt_server = yield self.cxn.get_server('pmt')
        yield pmt_server.select_device(self.pmt_name)
        yield pmt_server.signal__update(self.update_id)
        yield pmt_server.addListener(listener=self.receive_update, source=None, ID=self.update_id)

    @inlineCallbacks
    def receive_update(self, c, signal):
        if signal == self.pmt_name:
            pmt_server = yield self.cxn.get_server('pmt')
            data_json = yield pmt_server.retrive(-1)
            data = json.loads(data_json)
            record_name = data['record_name'].split('/')[6:]
            raw_data_path = self.data_dir + os.path.join(*record_name) + '.hdf5'
            self.replot(raw_data_path)

    def replot(self, data_path):
        with h5py.File(data_path) as h5f:
            gnd = h5f['gnd'][500:]
            exc = h5f['exc'][500:]
            bac = h5f['bac'][500:]
            self.canvas.ax.clear()
            self.canvas.ax.plot(gnd, label='gnd')
            self.canvas.ax.plot(exc, label='exc')
            self.canvas.ax.plot(bac, label='bac')
            self.canvas.ax.legend()
        self.canvas.draw()
    
    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = PMTViewer('blue_pmt', reactor)
    widget.show()
    reactor.run()
