from PyQt4 import QtGui, QtCore
import numpy as np
import json
import sys
import h5py
import matplotlib as mpl
from twisted.internet.defer import inlineCallbacks
from time import strftime

from client_tools.connection import connection

import pyqtgraph as pg
from cmap_to_colormap import cmapToColormap

cmap = mpl.cm.get_cmap('magma')
MyColorMap = pg.ColorMap(*zip(*cmapToColormap(cmap)))

from data_tools.process_image import process_image



class ImageViewer(QtGui.QWidget):
    servername = 'yesr10_andor'
    update_id = 734520
#    data_directory = '/home/yertle/yesrdata/SrQ/data/{}/'
    data_directory = 'Z:\\SrQ\\data\\{}\\{}'
    name = 'ikon'

    def __init__(self, reactor):
        super(ImageViewer, self).__init__()
        self.reactor = reactor
        self.populate()
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        self.cxn = connection()
        cname = '{} - {} - client'.format(self.servername, self.name)
        yield self.cxn.connect(name=cname)
        self.context = yield self.cxn.context()
        yield self.connectSignals()

    def populate(self):
        self.imageView = pg.ImageView()
        self.imageView.setColorMap(MyColorMap)
        self.imageView.show()
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addWidget(self.imageView)
        self.setLayout(self.layout)
    
    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        self.imageView.scene.sigMouseClicked.connect(self.handle_click)
        print 'connected!'

    def handle_click(self, mouseClickEvent):
        print 'click'
        print mouseClickEvent.double()
        if mouseClickEvent.double():
            scenePos = mouseClickEvent.scenePos()
            print scenePos
            pos = self.imageView.getView().mapSceneToView(scenePos)
            if not hasattr(self, 'crosshairs'):
                self.crosshairs = {
                    'x': pg.InfiniteLine(angle=90, pen='g'),
                    'y': pg.InfiniteLine(angle=0, pen='g'),
                    }
                self.imageView.addItem(self.crosshairs['x'])
                self.imageView.addItem(self.crosshairs['y'])
            
            self.crosshairs['x'].setPos(pos.x())
            self.crosshairs['y'].setPos(pos.y())
        
    def receive_update(self, c, signal):
        print 'got signal!', signal
        signal = json.loads(signal)
        for key, value in signal.items():
            if key == self.name:
                record_path = value['record_path']
                record_type = value['record_type']
                image_path = self.data_directory.format(*record_path)
                print 'ok'
                self.plot(image_path, record_type)
        print 'done signal'
    
    def plot(self, image_path, record_type):
        print image_path
        image = process_image(image_path, record_type)
        image = np.rot90(image)
        self.imageView.setImage(image, autoRange=False, autoLevels=False)

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == '__main__':
    app = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = ImageViewer(reactor)
    widget.show()
    reactor.run()
