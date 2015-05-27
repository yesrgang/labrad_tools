from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
from client_tools import SuperSpinBox
import numpy as np

import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure

def H(x):
    return 0.5*(np.sign(x)+1)

def G(t1, t2):
    return lambda t: H(t2-t) - H(t1-t) 

class LinearRamp(object):
    def __init__(self, p=None):
#        self.necessary_parameters = [('t', 1e-3), ('vi', 0.), ('vf', 0.)]
        self.set_parameters(p)

    def set_parameters(self, p):
        self.p = p
        if p is not None:
            self.continuous = lambda t: G(0, p['t'])(t)*( p['vi'] + (p['vf']-p['vi'])/p['t']*t )

    def get_points(self):
        dT = [self.p['t']]
        V = [self.p['vf']]
        return dT, V

class ExpRamp(object):
    def __init__(self, p=None):
#        self.necessary_parameters = [('t', 1e-3), ('vi', 0.), ('vf', 0.), ('tau', 1e-3), ('pts', 10)]
        self.set_parameters(p)

    def set_parameters(self, p):
        self.p = p
        if p is not None:
            self.A = (p['vf'] - p['vi'])/(np.exp(p['t']/p['tau']) - 1)
            self.C = p['vi'] - self.A
            self.continuous = lambda t: G(0, p['t'])(t)*(self.A * np.exp(t/p['tau']) + self.C)

    def get_points(self):
        num_points = int(self.p['pts'])
        T = np.linspace(0, self.p['t'], num_points+1)
        dT = [self.p['t']/float(num_points)]*num_points
        V = self.continuous(T)
        V[-1] = self.p['vf']
        return dT, V[1:]

class ParameterWidget(QtGui.QWidget):
    def __init__(self, p_info):
        """
        p_info is [(parameter_label, range, suffixes, num_decimals)]
        """
        super(ParameterWidget, self).__init__(None)
        self.p_info = p_info
        self.populate()

    def populate(self):
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.p_boxes = {}
        for i, (p, r, s, n) in enumerate(self.p_info):
            if p != 'loc':
                self.p_boxes[p] = SuperSpinBox(r, s, n)
                self.p_boxes[p].display(1)
            else:
                self.p_boxes[p] = QtGui.QLineEdit()
            label = QtGui.QLabel(p+': ')
            label.setFixedWidth(30)
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.layout.addWidget(label, i, 0)
            self.layout.addWidget(self.p_boxes[p], i, 1)
            self.p_boxes[p].setFixedWidth(80)
            self.p_boxes[p].setFixedHeight(20)
        self.layout.addWidget(QtGui.QFrame())
        self.setLayout(self.layout)

class RampColumn(QtGui.QGroupBox):
    def __init__(self):
        super(RampColumn, self).__init__(None)
        self.populate()

    def populate(self):
        self.layout = QtGui.QGridLayout()
       
        self.add = QtGui.QPushButton('+')
        self.dlt = QtGui.QPushButton('-')
        self.add.setFixedSize(15, 20) # w, h
        self.dlt.setFixedSize(15, 20) # w, h
        self.layout.addWidget(self.add, 0, 0)
        self.layout.addWidget(self.dlt, 0, 1)

        self.ramp_select = QtGui.QComboBox()
        self.ramp_select.addItems(['linear', 'exp', 'step'])
        self.ramp_select.setFixedWidth(80)
        self.ramp_select.setFixedHeight(20)
        self.layout.addWidget(self.ramp_select, 0, 2)

        self.stack = QtGui.QStackedWidget()
        available_ramps = {
                           'step': [('v', [-10, 10], [(0, 'V'), (-3, 'mV')], 3),
                                   ],
                           'linear': [('v', [-10, 10], [(0, 'V'), (-3, 'mV')], 3),
                                      ('t', [1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1), 
                                     ],
                           'exp': [('v', [-10, 10], [(0, 'V')], 3),
                                   ('t', [1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1), 
                                   ('tau', [-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')], 1),
                                   ('pts', [1, 10], [(0, 'na')], 0),
                                   ],
                           }
                                
        self.parameter_widgets = {k: ParameterWidget(p_info) for k, p_info in available_ramps.items()}
        for k, pw in self.parameter_widgets.items():
            self.stack.addWidget(pw)
        self.stack.setCurrentWidget(self.parameter_widgets['linear'])
        self.layout.addWidget(self.stack, 1, 0, 1, 3)


        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(30+80+4)

        self.ramp_select.currentIndexChanged.connect(self.select_from_stack)

    def select_from_stack(self):
        ramp_type = str(self.ramp_select.currentText())
        self.stack.setCurrentWidget(self.parameter_widgets[ramp_type])


class RampTable(QtGui.QWidget):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.populate()

    def populate(self):
        self.cols = [RampColumn() for i in range(10)]
        self.layout = QtGui.QHBoxLayout()
        for c in self.cols:
            self.layout.addWidget(c)
        self.layout.addWidget(QtGui.QFrame())
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)

        points = ([0, 1, 2, 3], [3, 2, 1, 1])

        self.fig.set_tight_layout(True)

        self.make_figure(*points)

        FigureCanvas.__init__(self, self.fig)
        self.setFixedSize(600, 300)

    def make_figure(self, times=None, voltages=None):
        self.axes.set_xlabel('time [s]')
        self.axes.set_ylabel('voltage [V]')
        self.axes.plot(times, voltages)

class LoadAndSave(QtGui.QWidget):
    def __init__(self):
        super(LoadAndSave, self).__init__(None)
        self.populate()

    def populate(self):
        self.location_box = QtGui.QLineEdit()
        self.load_button = QtGui.QPushButton('&Load')
        self.load_button.setFixedSize(80, 20)
        self.save_button = QtGui.QPushButton('&Save')
        self.save_button.setFixedSize(80, 20)
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.location_box)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setFixedHeight(40)

    
class AnalogVoltageControl(QtGui.QGroupBox):
    def __init__(self, reactor):
        self.reactor = reactor
        QtGui.QDialog.__init__(self)
        self.ramp_dict = {
                          'linear': LinearRamp,
                          'exp': ExpRamp,
                         }
        self.loading = False
        self.populate()

    def populate(self):
        self.layout = QtGui.QGridLayout()

        self.load_and_save = LoadAndSave()

        self.canvas = MplCanvas()
        self.nav = NavigationToolbar(self.canvas, self)
        
        self.ramp_table = RampTable()
        self.ramp_scroll = QtGui.QScrollArea()
        self.ramp_scroll.setWidget(self.ramp_table)
        self.ramp_scroll.setFixedHeight(self.ramp_table.height()+self.ramp_scroll.horizontalScrollBar().height()-10)
#        self.ramp_scroll.setFrameShape(0)
        self.ramp_scroll.setWidgetResizable(True)
        
        self.layout.addWidget(self.load_and_save)
        self.layout.addWidget(self.nav)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.ramp_scroll)
        
        for c in self.ramp_table.cols:
            c.ramp_select.currentIndexChanged.connect(self.replot)
            for pw in c.parameter_widgets.values():
                for pb in pw.p_boxes.values():
                    pb.returnPressed.connect(self.replot)

        for i, c in enumerate(self.ramp_table.cols):
            c.add.clicked.connect(self.add_column(i))
            c.dlt.clicked.connect(self.dlt_column(i))
        
        self.load_and_save.save_button.clicked.connect(self.save)
        self.load_and_save.load_button.clicked.connect(self.browse)

        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        width = self.canvas.width()
        height = self.nav.height() + self.canvas.height() + self.ramp_scroll.height() + self.load_and_save.height()
        self.setFixedSize(width, height)

        self.replot()

    def get_ramp_info(self):
        ramp_types = [str(c.ramp_select.currentText()) for c in self.ramp_table.cols if not c.isHidden()]
        ramp_parameters = [{k: b.value() for k, b in c.stack.currentWidget().p_boxes.items()} for c in self.ramp_table.cols if not c.isHidden()]
        return zip(ramp_types, ramp_parameters)
    
    def save(self):
        infos = [str(i) + '\n' for i in self.get_ramp_info()]
        outfile = open(self.load_and_save.location_box.text(), 'w')
        outfile.write(''.join(infos))

    def browse(self):
        #file_name = QtGui.QFileDialog(directory='/home/yertle/code/labrad/clients/').getOpenFileName()
        file_name = QtGui.QFileDialog().getOpenFileName()
        self.load_and_save.location_box.setText(file_name)
        self.load(file_name)

    def load(self, file_name):
        infile = open(file_name, 'r')
        infos = [eval(l.split('\n')[:-1][0]) for l in infile.readlines()]
        self.set_columns(infos)
    
    def set_columns(self, infos):
        self.loading = True
        for c in self.ramp_table.cols:
            c.hide()
        
        for info, c in zip(infos, self.ramp_table.cols):
            t, p =  info
            c.show()
            c.ramp_select.setCurrentIndex(c.ramp_select.findText(t))
            for k, v in p.items():
                c.parameter_widgets[t].p_boxes[k].display(v)
        self.loading = False
        self.replot()

    def add_column(self, i):
        def ac():
            infos = self.get_ramp_info()
            infos.insert(i, infos[i])
            self.set_columns(infos)
        return ac

    def dlt_column(self, i):
        def dc():
            infos = self.get_ramp_info()
            infos.pop(i)
            self.set_columns(infos)
        return dc

    def get_sequence(self):
        """should send ramp_types, parameters to server and recieve T, V"""
        ramp_types = [str(c.ramp_select.currentText()) for c in self.ramp_table.cols if not c.isHidden()]
        ramp_parameters = [{k: b.value() for k, b in c.stack.currentWidget().p_boxes.items()} for c in self.ramp_table.cols if not c.isHidden()]
        for i in range(len(ramp_parameters)):
            ramp_parameters[i]['vf'] = ramp_parameters[i]['v']
        ramp_parameters[0]['vi'] = 0
        for i in range(len(ramp_parameters)-1):
            ramp_parameters[i+1]['vi'] = ramp_parameters[i]['v']
        points = [self.ramp_dict[s](p).get_points() for p, s in zip(ramp_parameters, ramp_types)]
        dT = [t  for X in points for t in X[0]]
        T = [0] + [sum(dT[:i+1]) for i in range(len(dT))]
        V = [0] + [float(v) for X in points for v in X[1]]
        return T, V

    def replot(self):
        if not self.loading:
            T, V =  self.get_sequence()
            self.canvas.make_figure(T, V)
            self.canvas.draw()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = AnalogVoltageControl(reactor)

    widget.show()
    reactor.run()











