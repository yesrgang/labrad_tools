from PyQt4 import QtGui, QtCore, Qt
#QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

sbwidth = 65
sbheight = 15
pbheight = 20
nlwidth = 30
acheight = 50
nlwidth = 200
ncwidth = 100
drheight = 20
pps = 1001

max_columns = 20

class Spacer(QtGui.QFrame):
    def __init__(self, height, width):
        super(Spacer, self).__init__(None)
        self.setFixedSize(width, height)
        self.setFrameShape(1)
        self.setLineWidth(0)

class BrowseAndSave(QtGui.QWidget):
    def __init__(self):
        super(BrowseAndSave, self).__init__(None)
        self.populate()

    def populate(self):
        self.location_box = QtGui.QLineEdit()
        self.browse_button = QtGui.QPushButton('Bro&wse')
        self.save_button = QtGui.QPushButton('&Save')
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.addWidget(self.location_box)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

class SequencerButton(QtGui.QFrame):
    def __init__(self, initial_state):
        super(SequencerButton, self).__init__(None)
        self.setFrameShape(2)
        self.setLineWidth(1)
        if initial_state:
            self.setChecked(1)
        else:
            self.setChecked(0)
    
    def setChecked(self, state):
        if state:
            self.setFrameShadow(0x0030)
            self.setStyleSheet('QWidget {background-color: #c9c9c9}')
            self.is_checked = True
        else:
            self.setFrameShadow(0x0020)
            self.setStyleSheet('QWidget {background-color: #ffffff}')
            self.is_checked = False

    def isChecked(self):
        if self.is_checked:
            return True
        else:
            return False

    def mousePressEvent(self, x):
        if self.is_checked:
            self.setChecked(False)
        else:
            self.setChecked(True)

class DigitalColumn(QtGui.QWidget):
    def __init__(self, channels):
        super(DigitalColumn, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.buttons = {n: SequencerButton(0) for n in self.channels.values()}

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        for i, (c, n) in enumerate(sorted(self.channels.items())):
            if not i%16 and i != 0:
                self.layout.addWidget(Spacer(sbheight/2, sbwidth))
            self.layout.addWidget(self.buttons[n])
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)
        height = 0
        for i in range(self.layout.count()):
            height += self.layout.itemAt(i).widget().height()

    def get_logic(self):
        return {n: int(self.buttons[n].isChecked()) for n in self.channels.values()}

    def set_logic(self, logic):
        for name, state in logic.items():
            if name in self.channels.values():
                self.buttons[name].setChecked(state)

class DigitalArray(QtGui.QWidget):
    def __init__(self, channels):
        super(DigitalArray, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.columns = [DigitalColumn(self.channels) for i in range(20)]
        self.layout = QtGui.QHBoxLayout()
        for lc in self.columns:
            self.layout.addWidget(lc)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        height = self.columns[0].height()
        width = self.columns[0].width()*10

    def display_sequence(self, sequence): 
        for c in self.columns[::-1]:
            c.hide()
        for (t, s), c in zip(sequence, self.columns):
            c.show()
            c.set_logic(s)

class NameBox(QtGui.QLabel):
    def __init__(self, name):
        super(NameBox, self).__init__(None)
        self.setText(name)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter  )

class DigitalNameColumn(QtGui.QWidget):
    def __init__(self, channels):
        super(DigitalNameColumn, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.labels = {n: NameBox(c+': '+n) for c, n in self.channels.items()}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 0, 0, 0)

        for i, (c, n) in enumerate(sorted(self.channels.items())):
            if not i%16 and i != 0:
                self.layout.addWidget(Spacer(sbheight/2, nlwidth))
            self.layout.addWidget(self.labels[n])
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)

class DurationRow(QtGui.QWidget):
    def __init__(self):
        super(DurationRow, self).__init__(None)
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.boxes = [SuperSpinBox([500e-9, 10], units) for i in range(20)]
        self.layout = QtGui.QHBoxLayout()
        for db in self.boxes:
            self.layout.addWidget(db)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def display_sequence(self, sequence):
        for b in self.boxes[::-1]:
            b.hide()
        for (t, s), b in zip(sequence, self.boxes):
            b.show()
            b.display(t)


class AddDltButton(QtGui.QWidget):
    def __init__(self):
        super(AddDltButton, self).__init__(None)
        self.add = QtGui.QPushButton('+')
        self.dlt = QtGui.QPushButton('-')
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.add)
        self.layout.addWidget(self.dlt)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

class AddDltRow(QtGui.QWidget):
    def __init__(self):
        super(AddDltRow, self).__init__(None)
        self.populate()

    def populate(self):
        self.buttons = [AddDltButton() for i in range(20)]
        self.layout = QtGui.QHBoxLayout()
        for ad in self.buttons:
            self.layout.addWidget(ad)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

class DigitalSequencer(QtGui.QWidget):
    def __init__(self, channels):
        super(DigitalSequencer, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.name_column = DigitalNameColumn(self.channels)
        self.name_column.scroll_area = QtGui.QScrollArea()
        self.name_column.scroll_area.setWidget(self.name_column)
        self.name_column.scroll_area.setWidgetResizable(True)
        self.name_column.scroll_area.setHorizontalScrollBarPolicy(1)
        self.name_column.scroll_area.setVerticalScrollBarPolicy(1)
        self.name_column.scroll_area.setFrameShape(0)

        self.array = DigitalArray(self.channels)
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

    def display_sequence(self, sequence):
        self.array.display_sequence(sequence)

    def connect_widgets(self):
        self.vscroll.verticalScrollBar().valueChanged.connect(self.adjust_for_vscroll)

    def adjust_for_vscroll(self):
        val = self.vscroll.verticalScrollBar().value()
        self.array.scroll_area.verticalScrollBar().setValue(val)
        self.name_column.scroll_area.verticalScrollBar().setValue(val)

def H(x):
    return 0.5*(np.sign(x)+1)

def G(t1, t2):
    return lambda t: H(t2-t+1e-9) - H(t1-t-1e-9) 

def G2(t1, t2):
    return lambda t: H(t2-t-1e-9) - H(t1-t-1e-9) 

#class AnalogCanvas(FigureCanvas):
#    def __init__(self):
#        self.populate()
#       
#    def populate(self):
#        self.fig = Figure()#facecolor='white'
#        FigureCanvas.__init__(self, self.fig)
#
#        self.axes = self.fig.add_subplot(111)
#        self.axes.spines['top'].set_visible(False)
#        self.axes.spines['bottom'].set_visible(False)
#        self.axes.spines['left'].set_visible(False)
#        self.axes.spines['right'].set_visible(False)
#        self.axes.get_xaxis().set_visible(False)
#        self.axes.get_yaxis().set_visible(False)
#        self.setContentsMargins(0, 0, 0, 0)
#        self.fig.subplots_adjust(left=0, bottom = 0, right=1, top=1)
#        #self.plot_sequence()
#
#    def plot_sequence(self, sequence):
#        S = sum([t for t, r in sequence])
#        X = self.get_points(sequence)
#        self.axes.cla()
#        for i, (c, n) in enumerate(sorted(self.channels.items())):
#            x = np.array(X[n]) - i*20
#            self.axes.plot(x)
#        self.axes.set_ylim(-20*len(self.channels.items())+10, 10)
#        self.axes.set_xlim(0, len(sequence)*pps)
#        self.draw()
#    
#    def get_points(self, sequence):
#        ramp_parameters = [{name: dict(d[name].items() + [('t', t)]) for name in self.channels.values()} for t, d in sequence] # throw t into dict
#        for name in self.channels.values():
#            ramp_parameters[0][name]['vi'] = 0
#            for i in range(1, len(sequence)):
#                ramp_parameters[i][name]['vi'] = ramp_parameters[i-1][name]['v']
#            for rp in ramp_parameters:
#                rp[name]['vf'] = rp[name]['v']
#        T = [np.linspace(0, t, pps) for t, r in sequence]
#        return {name: [v for vv in [self.get_continuous(rp[name])(t) for t, rp in zip(T, ramp_parameters)] for v in vv] for name in self.channels.values()}
#
#    def get_continuous(self, p):
#        if p['type'] == 'linear':
#            return lambda t: G(0, p['t'])(t)*(p['vi']+(p['vf']-p['vi'])/p['t']*t)
#        elif p['type'] == 'linear2':
#            return lambda t: G2(0, p['t'])(t)*(p['vi']+(p['vf']-p['vi'])/p['t']*t)
#        elif p['type'] == 'exp':
#            A = (p['vf'] - p['vi'])/(np.exp(p['t']/p['tau']) - 1)
#            C = p['vi'] - A
#            continuous = lambda t: G(0, p['t'])(t)*(A * np.exp(t/p['tau']) + C)
#            T = np.linspace(0, p['t'], p['pts'])
#            V = continuous(T)
#            lp2 = [{'vf': V[i+1], 'vi': V[i], 't': p['t']/float(p['pts']-1), 'type': 'linear2'} for i in range(p['pts']-1)]
#            lp2[-1]['type'] = 'linear'
#            return lambda t: sum([self.get_continuous(p2)(t-T[i]) for i, p2 in enumerate(lp2)])
#        elif p['type'] == 'step':
#            return lambda t: G(0, p['t'])(t)*p['v']

class AnalogNameColumn(QtGui.QWidget):
    def __init__(self, channels):
        super(AnalogNameColumn, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.labels = {n: NameBox(c+': '+n) for c, n in self.channels.items()}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 0, 0, 0)

        for i, (c, n) in enumerate(sorted(self.channels.items())):
            self.layout.addWidget(self.labels[n])
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)

class AnalogArray(FigureCanvas):
    def __init__(self, channels):
        self.channels = channels
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
        #self.plot_sequence()

    def plot_sequence(self, sequence):
        S = sum([t for t, r in sequence])
        X = self.get_points(sequence)
        self.axes.cla()
        for i, (c, n) in enumerate(sorted(self.channels.items())):
            x = np.array(X[n]) - i*20
            self.axes.plot(x)
        self.axes.set_ylim(-20*len(self.channels.items())+10, 10)
        self.axes.set_xlim(0, len(sequence)*pps)
        self.draw()
    
    def get_points(self, sequence):
        ramp_parameters = [{name: dict(d[name].items() + [('t', t)]) for name in self.channels.values()} for t, d in sequence] # throw t into dict
        for name in self.channels.values():
            ramp_parameters[0][name]['vi'] = 0
            for i in range(1, len(sequence)):
                ramp_parameters[i][name]['vi'] = ramp_parameters[i-1][name]['v']
            for rp in ramp_parameters:
                rp[name]['vf'] = rp[name]['v']
        T = [np.linspace(0, t, pps) for t, r in sequence]
        return {name: [v for vv in [self.get_continuous(rp[name])(t) for t, rp in zip(T, ramp_parameters)] for v in vv] for name in self.channels.values()}

    def get_continuous(self, p):
        if p['type'] == 'linear':
            return lambda t: G(0, p['t'])(t)*(p['vi']+(p['vf']-p['vi'])/p['t']*t)
        elif p['type'] == 'linear2':
            return lambda t: G2(0, p['t'])(t)*(p['vi']+(p['vf']-p['vi'])/p['t']*t)
        elif p['type'] == 'exp':
            A = (p['vf'] - p['vi'])/(np.exp(p['t']/p['tau']) - 1)
            C = p['vi'] - A
            continuous = lambda t: G(0, p['t'])(t)*(A * np.exp(t/p['tau']) + C)
            T = np.linspace(0, p['t'], p['pts'])
            V = continuous(T)
            lp2 = [{'vf': V[i+1], 'vi': V[i], 't': p['t']/float(p['pts']-1), 'type': 'linear2'} for i in range(p['pts']-1)]
            lp2[-1]['type'] = 'linear'
            return lambda t: sum([self.get_continuous(p2)(t-T[i]) for i, p2 in enumerate(lp2)])
        elif p['type'] == 'step':
            return lambda t: G(0, p['t'])(t)*p['v']


class AnalogSequencer(QtGui.QWidget):
    def __init__(self, channels):
        super(AnalogSequencer, self).__init__(None)
        self.channels = channels
        self.sequence = []
        self.populate()

    def populate(self):
        self.name_column = AnalogNameColumn(self.channels)
        self.name_column.scroll_area = QtGui.QScrollArea()
        self.name_column.scroll_area.setWidget(self.name_column)
        self.name_column.scroll_area.setWidgetResizable(True)
        self.name_column.scroll_area.setHorizontalScrollBarPolicy(1)
        self.name_column.scroll_area.setVerticalScrollBarPolicy(1)
        self.name_column.scroll_area.setFrameShape(0)
        
        self.array = AnalogArray(self.channels)
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

    def display_sequence(self, sequence):
        self.sequence = [{name: s[name] for name in self.channels.values()} for t, s in sequence]
        self.array.plot_sequence(sequence)
    
    def connect_widgets(self):
        self.vscroll.verticalScrollBar().valueChanged.connect(self.adjust_for_vscroll)

    def adjust_for_vscroll(self):
        val = self.vscroll.verticalScrollBar().value()
        self.array.scroll_area.verticalScrollBar().setValue(val)
        self.name_column.scroll_area.verticalScrollBar().setValue(val)

class Sequencer(QtGui.QWidget):
    def __init__(self, digital_channels, analog_channels):
        super(Sequencer, self).__init__(None)
        self.digital_channels = digital_channels
        self.analog_channels = analog_channels
        self.populate()

    def populate(self):
        self.browse_and_save = BrowseAndSave()

        self.add_dlt_row = AddDltRow()
        self.add_dlt_row.scroll_area = QtGui.QScrollArea()
        self.add_dlt_row.scroll_area.setWidget(self.add_dlt_row)
        self.add_dlt_row.scroll_area.setWidgetResizable(True)
        self.add_dlt_row.scroll_area.setHorizontalScrollBarPolicy(1)
        self.add_dlt_row.scroll_area.setVerticalScrollBarPolicy(1)
        self.add_dlt_row.scroll_area.setFrameShape(0)

        self.duration_row = DurationRow()
        self.duration_row.scroll_area = QtGui.QScrollArea()
        self.duration_row.scroll_area.setWidget(self.duration_row)
        self.duration_row.scroll_area.setWidgetResizable(True)
        self.duration_row.scroll_area.setHorizontalScrollBarPolicy(1)
        self.duration_row.scroll_area.setVerticalScrollBarPolicy(1)
        self.duration_row.scroll_area.setFrameShape(0)
        
        self.digital_sequencer = DigitalSequencer(self.digital_channels)
        self.analog_sequencer = AnalogSequencer(self.analog_channels)

        self.hscroll_array = QtGui.QScrollArea()
        self.hscroll_array.setWidget(QtGui.QWidget())
        self.hscroll_array.setHorizontalScrollBarPolicy(2)
        self.hscroll_array.setVerticalScrollBarPolicy(1)
        self.hscroll_array.setWidgetResizable(True)
        self.hscroll_array.setFrameShape(0)
        
        self.hscroll_name = QtGui.QScrollArea()
        self.hscroll_name.setWidget(QtGui.QWidget())
        self.hscroll_name.setHorizontalScrollBarPolicy(2)
        self.hscroll_name.setVerticalScrollBarPolicy(1)
        self.hscroll_name.setWidgetResizable(True)
        self.hscroll_name.setFrameShape(0)
        
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.digital_sequencer)
        self.splitter.addWidget(self.analog_sequencer)

        """spacer widgets"""
        self.northwest = QtGui.QWidget()
        self.northeast = QtGui.QWidget()
        self.southwest = QtGui.QWidget()
        self.southeast = QtGui.QWidget()

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.northwest, 0, 0, 2, 1)
        self.layout.addWidget(self.browse_and_save, 0, 1)
        self.layout.addWidget(self.northeast, 0, 2, 2, 1)
        self.layout.addWidget(self.duration_row.scroll_area, 1, 1)
        self.layout.addWidget(self.splitter, 2, 0, 1, 3)
        self.layout.addWidget(self.southwest, 3, 0, 1, 1)
        self.layout.addWidget(self.add_dlt_row.scroll_area, 3, 1)
        self.layout.addWidget(self.hscroll_name, 4, 0)
        self.layout.addWidget(self.hscroll_array, 4, 1)
        self.layout.addWidget(self.southeast, 3, 2, 2, 1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.set_sizes()
        self.connect_widgets()

    def set_sizes(self):
        self.northwest.setFixedSize(ncwidth, drheight)
        self.browse_and_save.setFixedWidth(10*sbwidth)
        self.northeast.setFixedSize(20, drheight)
        
        for c in self.digital_sequencer.array.columns:
            for b in c.buttons.values():
                b.setFixedSize(sbwidth, sbheight)
            height = sum([c.layout.itemAt(i).widget().height() for i in range(c.layout.count()-1)]) # -1 because there is a generic widget in the last spot
            c.setFixedSize(sbwidth, height)
        da_width = sum([c.width() for c in self.digital_sequencer.array.columns if not c.isHidden()])
        da_height = self.digital_sequencer.array.columns[0].height()
        self.digital_sequencer.array.setFixedSize(da_width, da_height)

        for nl in self.digital_sequencer.name_column.labels.values():
            nl.setFixedHeight(sbheight)
#            nb.setFixedSize(nlwidth, sbheight)
        nc_width = nlwidth
        nc_height = self.digital_sequencer.array.height()
        self.digital_sequencer.name_column.setFixedSize(nc_width, nc_height)
        self.digital_sequencer.name_column.scroll_area.setFixedWidth(ncwidth)
        
        self.digital_sequencer.vscroll.widget().setFixedSize(0, self.digital_sequencer.array.height())
        self.digital_sequencer.vscroll.setFixedWidth(20)

        self.analog_sequencer.array.setFixedSize(self.digital_sequencer.array.width(), acheight*len(self.analog_channels))
        self.analog_sequencer.vscroll.widget().setFixedSize(0, self.analog_sequencer.array.height())
        self.analog_sequencer.vscroll.setFixedWidth(20)
        
        for nl in self.analog_sequencer.name_column.labels.values():
#            nl.setFixedHeight(acheight)
            nl.setFixedSize(nlwidth, acheight)
        nc_width = nlwidth
        nc_height = self.analog_sequencer.array.height()
        self.analog_sequencer.name_column.setFixedSize(nc_width, nc_height)
        self.analog_sequencer.name_column.scroll_area.setFixedWidth(ncwidth)
        
        for b in self.duration_row.boxes:
            b.setFixedSize(sbwidth, drheight)
        dr_width = sum([db.width() for db in self.duration_row.boxes if not db.isHidden()])
        self.duration_row.setFixedSize(dr_width, drheight)
        self.duration_row.scroll_area.setFixedHeight(drheight)
       
        self.southwest.setFixedSize(ncwidth, drheight)
        self.southeast.setFixedWidth(20)
        
        for b in self.add_dlt_row.buttons:
            b.setFixedSize(sbwidth, 15)
        self.add_dlt_row.setFixedSize(dr_width, drheight)
        self.add_dlt_row.scroll_area.setFixedHeight(drheight)
        
        self.hscroll_array.widget().setFixedSize(self.digital_sequencer.array.width(), 0)
        self.hscroll_array.setFixedHeight(20)
        self.hscroll_name.widget().setFixedSize(nlwidth, 0)
        self.hscroll_name.setFixedSize(ncwidth, 20)

    def connect_widgets(self):
        self.hscroll_array.horizontalScrollBar().valueChanged.connect(self.adjust_for_hscroll_array)
        self.hscroll_name.horizontalScrollBar().valueChanged.connect(self.adjust_for_hscroll_name)

        self.browse_and_save.save_button.clicked.connect(self.save_sequence)
        self.browse_and_save.browse_button.clicked.connect(self.browse)

        for i, b in enumerate(self.add_dlt_row.buttons):
            b.add.clicked.connect(self.add_column(i))
            b.dlt.clicked.connect(self.dlt_column(i))

    def adjust_for_dvscroll(self):
        val = self.digital_vscroll.verticalScrollBar().value()
        self.digital_name_scroll.verticalScrollBar().setValue(val)
        self.digital_scroll.verticalScrollBar().setValue(val)
    
    def adjust_for_avscroll(self):
        val = self.analog_vscroll.verticalScrollBar().value()
        self.analog_name_scroll.verticalScrollBar().setValue(val)
        self.analog_array_scroll.verticalScrollBar().setValue(val)

    def adjust_for_hscroll_array(self):
        val = self.hscroll_array.horizontalScrollBar().value()
        self.duration_row.scroll_area.horizontalScrollBar().setValue(val)
        self.digital_sequencer.array.scroll_area.horizontalScrollBar().setValue(val)
        self.analog_sequencer.array.scroll_area.horizontalScrollBar().setValue(val)
        self.add_dlt_row.scroll_area.horizontalScrollBar().setValue(val)
    
    def adjust_for_hscroll_name(self):
        val = self.hscroll_name.horizontalScrollBar().value()
        self.digital_sequencer.name_column.scroll_area.horizontalScrollBar().setValue(val)
        self.analog_sequencer.name_column.scroll_area.horizontalScrollBar().setValue(val)
    
    def browse(self):
        file_name = QtGui.QFileDialog().getOpenFileName()
        self.browse_and_save.location_box.setText(file_name)
        self.load_sequence(file_name)

    def save_sequence(self):
        sequence = [str(seq) + '\n' for seq in self.get_sequence()]
        print sequence
        outfile = open(self.browse_and_save.location_box.text(), 'w')
        outfile.write(''.join(sequence))

    def load_sequence(self, file_name):
        infile = open(file_name, 'r')
        sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
        self.set_sequence(sequence)

    def set_sequence(self, sequence):
        self.analog_sequencer.display_sequence(sequence)
        self.digital_sequencer.display_sequence(sequence)
        self.duration_row.display_sequence(sequence)
        self.set_sizes()

    def get_sequence(self):
        durations = [b.value() for b in self.duration_row.boxes if not b.isHidden()]
        digital_logic = [c.get_logic() for c in self.digital_sequencer.array.columns if not c.isHidden()]
        analog_logic = self.analog_sequencer.sequence
        sequence = [(t, dict(d.items() + a.items())) for t, d, a in zip(durations, digital_logic, analog_logic)]
        return sequence
    
    def add_column(self, i):
        def ac():
            sequence = self.get_sequence()
            sequence.insert(i, sequence[i])
            self.set_sequence(sequence)
        return ac

    def dlt_column(self, i):
        def dc():
            sequence = self.get_sequence()
            sequence.pop(i)
            self.set_sequence(sequence)
        return dc



digital_channels = {
            'A00': 'TTLA00',
            'A01': 'TTLA01',
            'A02': 'TTLA02',
            'A03': 'TTLA03',
            'A04': 'TTLA04',
            'A05': 'TTLA05',
            'A06': 'TTLA06',
            'A07': 'TTLA07',
            'A08': 'TTLA08',
            'A09': 'TTLA09',
            'A10': 'TTLA10',
            'A11': 'TTLA11',
            'A12': 'TTLA12',
            'A13': 'TTLA13',
            'A14': 'TTLA14',
            'A15': 'TTLA15',

            'B00': 'TTLB00',
            'B01': 'TTLB01',
            'B03': 'TTLB02',
            'B03': 'TTLB03',
            'B04': 'TTLB04',
            'B05': 'TTLB05',
            'B06': 'TTLB06',
            'B07': 'TTLB07',
            'B08': 'TTLB08',
            'B09': 'TTLB09',
            'B10': 'TTLB10',
            'B11': 'TTLB11',
            'B12': 'TTLB12',
            'B13': 'TTLB13',
            'B14': 'TTLB14',
            'B15': 'TTLB15',

            'C00': 'TTLC00',
            'C01': 'TTLC01',
            'C02': 'TTLC02',
            'C03': 'TTLC03',
            'C04': 'TTLC04',
            'C05': 'TTLC05',
            'C06': 'TTLC06',
            'C07': 'TTLC07',
            'C08': 'TTLC08',
            'C09': 'TTLC09',
            'C10': 'TTLC10',
            'C11': 'TTLC11',
            'C12': 'TTLC12',
            'C13': 'TTLC13',
            'C14': 'TTLC14',
            'C15': 'TTLC15',
            
            'D00': 'TTLD00',
            'D01': 'TTLD01',
            'D02': 'TTLD02',
            'D03': 'TTLD03',
            'D04': 'TTLD04',
            'D05': 'TTLD05',
            'D06': 'TTLD06',
            'D07': 'TTLD07',
            'D08': 'TTLD08',
            'D09': 'TTLD09',
            'D10': 'TTLD10',
            'D11': 'TTLD11',
            'D12': 'TTLD12',
            'D13': 'TTLD13',
            'D14': 'TTLD14',
            'D15': 'TTLD15',
            }

analog_channels = {
            'A00': 'DACA00asdfafds',
            'A01': 'DACA01',
            'A02': 'DACA02',
            'A03': 'DACA03',
            'A04': 'DACA04',
            'A05': 'DACA05',
            'A06': 'DACA06',
            'A07': 'DACA07',
            }

test_ramp = [(1, {name: {'type': 'exp', 'v': 10, 'tau': .5, 'pts': 10} for name in analog_channels.values()})] + [(1, {name: {'type': 'step', 'v': 0, 'length': (1, 1)} for name in analog_channels.values()})] + [(1, {name: {'type': 'linear', 'v': 10, 'length': (1, 1)} for name in analog_channels.values()})]*3 + [(.1, {name: {'type': 'linear', 'v': 0, 'length': (1, 1)} for name in analog_channels.values()})]*3

sequence = [(1, dict([(name, {'type': 'linear', 'v': 0, 'length': (1, 1)}) for name in analog_channels.values()] + [(name, 0) for name in digital_channels.values()]), )]*19

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Sequencer(digital_channels, analog_channels)
    widget.show()
    reactor.run()
