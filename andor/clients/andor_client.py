from PyQt4 import QtGui, QtCore
import numpy as np
import json
import sys
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import h5py
from twisted.internet.defer import inlineCallbacks
from time import strftime

from client_tools.connection import connection

from my_cmap import my_cmap

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel(r'x ($\mu$m)')
        self.ax.set_ylabel(r'y ($\mu$m)')
        self.ax.hold(False)

        self.fig.set_tight_layout(True)

        FigureCanvas.__init__(self, self.fig)

    def make_figure(self, image):

        self.ax.pcolormesh(image, vmin=np.mean(image), vmax=np.max(image), cmap=my_cmap)
        self.ax.set_aspect('equal')
        self.ax.autoscale(tight=True)

class ImageViewer(QtGui.QWidget):
    servername = 'yesr10_andor'
    update_id = 194320
    #data_directory = '/home/yertle/yesrdata/SrQ/data/{}/'
    data_directory = 'Z:\\SrQ\\data\\{}\\'
    name = 'ikon'

    def __init__(self, reactor):
        super(ImageViewer, self).__init__()
        self.reactor = reactor
        self.populate()
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        self.cxn = connection()
        yield self.cxn.connect()
        self.context = yield self.cxn.context()
        yield self.connectSignals()

    def populate(self):
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
    
    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        
    def receive_update(self, c, signal):
        print 'got signal!', signal
        signal = json.loads(signal)
        for key, value in signal.items():
            if key == self.name:
                record_name = value['record_name']
                record_type = value['record_type']
                data_directory = self.data_directory.format(strftime('%Y%m%d'))
                image_path = data_directory + record_name
                self.plot(image_path, record_type)
        print 'done signal'
    
    def plot(self, image_path, record_type):
        image = process_image(image_path, record_type)
        self.canvas.make_figure(image)
        self.canvas.draw()

def process_image(image_path, record_type):
    images = {}
    images_h5 = h5py.File(image_path, "r")
    for key in images_h5:
        images[key] = np.array(images_h5[key], dtype='float64')
    images_h5.close()
    if record_type == 'record_g': 
        n_lin = images["bright"] - images["dark"] + images["background"]
        image = n_lin
        image = np.flipud(np.fliplr(image))
        return image
    elif record_type == 'record_eg':
        ng_lin = images["bright"] - images["dark_g"] + images["g_background"] - images["bright_background"]
        ne_lin = images["bright"] - images["dark_e"] + images["e_background"] - images["bright_background"]
        image = ng_lin
        image = np.flipud(np.fliplr(image))
        return image

if __name__ == '__main__':
    app = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = ImageViewer(reactor)
    widget.show()
    reactor.run()
