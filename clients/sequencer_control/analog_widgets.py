from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
import numpy as np
import json
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


#class NameBox(QtGui.QLabel):
#    clicked = QtCore.pyqtSignal()
#    def __init__(self, name):
#        super(NameBox, self).__init__(None)
#        self.setText(name)
#        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter  )
#        self.name = name
#
#    def mousePressEvent(self, x):
#        self.clicked.emit()
class NameBox(QtGui.QLabel):
    clicked = QtCore.pyqtSignal()
    def __init__(self, nameloc):
        super(NameBox, self).__init__(None)
        self.nameloc = nameloc
        name, loc = nameloc.split('@')
        self.setText(loc+': '+name)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter  )
	self.name = name

    def mousePressEvent(self, x):
        self.clicked.emit()

class AnalogNameColumn(QtGui.QWidget):
    def __init__(self, channels):
        super(AnalogNameColumn, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.labels = {nl: NameBox(nl) for nl in self.channels}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 0, 0, 0)

        for i, nl in enumerate(sorted(self.channels, key=lambda nl: nl.split('@')[1])):
            self.layout.addWidget(self.labels[nl])
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)


class AnalogArray(FigureCanvas):
    def __init__(self, channels, RampMaker):
        self.channels = channels
        self.ramp_maker = RampMaker
        self.populate()
       
    def populate(self):
        self.fig = Figure()#facecolor='white'
        FigureCanvas.__init__(self, self.fig)

        self.axes = self.fig.add_subplot(111)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.fig.subplots_adjust(left=0, bottom = 0, right=1, top=1)

    def plot_sequence(self, sequence):
        self.axes.cla()
        for i, c in enumerate(self.channels):
            channel_sequence = sequence[c]
            T, V = self.ramp_maker(channel_sequence).get_plottable(scale='step')
            V = np.array(V) - i*20
            self.axes.plot(T, V)
        for i in range(len(self.channels)-1):
            self.axes.axhline(-10-i*20, linestyle="--", color='grey')
	for i in range(len(sequence['digital@T'])-1):
            self.axes.axvline(i*99+99, color='grey')
        self.axes.set_ylim(-20*len(self.channels)+10, 10)
        self.axes.set_xlim(0, len(T))
        self.draw()

class AnalogSequencer(QtGui.QWidget):
    sequence = {}
    def __init__(self, channels, config):
        super(AnalogSequencer, self).__init__(None)
        self.channels = channels
        self.config = config
        self.populate()

    def populate(self):
        self.name_column = AnalogNameColumn(self.channels)
        self.name_column.scroll_area = QtGui.QScrollArea()
        self.name_column.scroll_area.setWidget(self.name_column)
        self.name_column.scroll_area.setWidgetResizable(True)
        self.name_column.scroll_area.setHorizontalScrollBarPolicy(1)
        self.name_column.scroll_area.setVerticalScrollBarPolicy(1)
        self.name_column.scroll_area.setFrameShape(0)
       	
        self.array = AnalogArray(self.channels, self.config.ramp_maker)
        self.array.scroll_area = QtGui.QScrollArea()
        self.array.scroll_area.setWidget(self.array)
        self.array.scroll_area.setWidgetResizable(True)
        self.array.scroll_area.setHorizontalScrollBarPolicy(1)
        self.array.scroll_area.setVerticalScrollBarPolicy(1)
        self.array.scroll_area.setFrameShape(0)

        self.vscroll = QtGui.QScrollArea()
        self.vscroll.setWidget(QtGui.QWidget())
        self.vscroll.setHorizontalScrollBarPolicy(1)
        self.vscroll.setVerticalScrollBarPolicy(2)
        self.vscroll.setFrameShape(0)
        
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.name_column.scroll_area)
        self.layout.addWidget(self.array.scroll_area)
        self.layout.addWidget(self.vscroll)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.connect_widgets()

    def set_sequence(self, sequence):
        self.sequence = sequence

    def display_sequence(self, sequence):
        self.array.plot_sequence(sequence)

#    def evaluate_sequence_parameters(self, sequence, parameters):
#        sequence = json.dumps(sequence)
#        for p, v in parameters.items():
#            sequence = sequence.replace('"{}"'.format(p), str(v))
#        sequence = json.loads(sequence)
#	print sequence['Z Comp. Coil@E04']
##        for d in sequence:
##            for v in d.values():
##                try:
##                    v = float(v)
##                except:
##                    v = 0
#        return sequence
    
    def connect_widgets(self):
        self.vscrolls = [self.name_column.scroll_area.verticalScrollBar(), self.array.scroll_area.verticalScrollBar(), self.vscroll.verticalScrollBar()]
        for vs in self.vscrolls:
            vs.valueChanged.connect(self.adjust_for_vscroll(vs))

    def adjust_for_vscroll(self, scrolled):
        def afv():
            val = scrolled.value()
            for vs in self.vscrolls:
                vs.setValue(val)
        return afv

