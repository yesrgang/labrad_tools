from PyQt4 import QtGui, QtCore, Qt
#QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np
import json
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import digital_channel_control as dcc

sbwidth = 65
sbheight = 15
pbheight = 20
acheight = 50
nlwidth = 200
ncwidth = 130
drheight = 20
pps = 1001

max_columns = 100
colors = ['#ff0000', '#ff7700', '#00ff00', '#0000ff', '#8a2be2', '#c77df3']

def merge_dicts(*dictionaries):
    merged_dictionary = {}
    for d in dictionaries:
        merged_dictionary.update(d)
    return merged_dictionary

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
        self.on_color = '#ff69b4'
        self.off_color = '#ffffff'
        if initial_state:
            self.setChecked(1)
        else:
            self.setChecked(0)
    
    def setChecked(self, state):
        if state:
            self.setFrameShadow(0x0030)
            self.setStyleSheet('QWidget {background-color: %s}' % self.on_color)
            self.is_checked = True
        else:
            self.setFrameShadow(0x0020)
            self.setStyleSheet('QWidget {background-color: %s}' % self.off_color)
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
            self.buttons[n].on_color = colors[i%len(colors)]
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
        self.columns = [DigitalColumn(self.channels) for i in range(max_columns)]
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
    clicked = QtCore.pyqtSignal()
    def __init__(self, name):
        super(NameBox, self).__init__(None)
        self.setText(name)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter  )
        self.name = name.split(': ')[1]

    def mousePressEvent(self, x):
        self.clicked.emit()

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
        self.boxes = [SuperSpinBox([500e-9, 10], units) for i in range(max_columns)]
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
        self.buttons = [AddDltButton() for i in range(max_columns)]
        self.layout = QtGui.QHBoxLayout()
        for ad in self.buttons:
            self.layout.addWidget(ad)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
    
    def display_sequence(self, sequence):
        for b in self.buttons[::-1]:
            b.hide()
        for (t, s), b in zip(sequence, self.buttons):
            b.show()

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

#    def connect_widgets(self):
#        self.vscroll.verticalScrollBar().valueChanged.connect(self.adjust_for_vscroll)
#
#    def adjust_for_vscroll(self):
#        val = self.vscroll.verticalScrollBar().value()
#        self.array.scroll_area.verticalScrollBar().setValue(val)
#        self.name_column.scroll_area.verticalScrollBar().setValue(val)
    
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

def H(x):
    return 0.5*(np.sign(x)+1)

def G(t1, t2):
    return lambda t: H(t2-t+1e-9) - H(t1-t-1e-9) 

def G2(t1, t2):
    return lambda t: H(t2-t-1e-9) - H(t1-t-1e-9) 

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

def H(x):
    return 0.5*(np.sign(x)+1)

def G(t1, t2):
    return lambda t: H(t2-t) - H(t1-t) 

class StepRamp(object):
    def __init__(self, p=None):
        self.set_parameters(p)

    def set_parameters(self, p):
        self.p = p
        if p is not None:
            self.continuous = lambda t: G(0, p['t'])(t)*p['vf']

    def get_points(self):
        dT = [0, self.p['t']]
        V = [self.p['vf'], self.p['vf']]
        return dT, V


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

class AnalogArray(FigureCanvas):
    def __init__(self, channels):
        self.channels = channels
        self.ramp_dict = {'linear': LinearRamp,
                          'exp': ExpRamp,
                          'step': StepRamp,
                          }
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
        X = self.get_points(sequence)
        self.axes.cla()
        for i, (c, n) in enumerate(sorted(self.channels.items())):
            x = np.array(X[n]) - i*20
            self.axes.plot(x)
        for i in range(len(self.channels.items())-1):
            self.axes.axhline(-10-i*20, linestyle="--", color='grey')
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
            return lambda t: G(0-1e-9, p['t']+1e-9)(t)*(p['vi']+(p['vf']-p['vi'])/p['t']*t)
        elif p['type'] == 'linear2':
            return lambda t: G2(0-1e-9, p['t']+1e-9)(t)*(p['vi']+(p['vf']-p['vi'])/p['t']*t)
        elif p['type'] == 'exp':
            A = (p['vf'] - p['vi'])/(np.exp(p['t']/p['tau']) - 1)
            C = p['vi'] - A
            continuous = lambda t: G(0-1e-9, p['t']+1e-9)(t)*(A * np.exp(t/p['tau']) + C)
            T = np.linspace(0, p['t'], p['pts'])
            V = continuous(T)
            lp2 = [{'vf': V[i+1], 'vi': V[i], 't': p['t']/float(p['pts']-1), 'type': 'linear'} for i in range(int(p['pts'])-1)]
            lp2[-1]['type'] = 'linear'
            return lambda t: sum([self.get_continuous(p2)(t-T[i]) for i, p2 in enumerate(lp2)])
        elif p['type'] == 'step':
            return lambda t: G(0-1e-9, p['t']+1e-9)(t)*p['v']


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
        self.sequence = [{name: s[name] for name in self.channels.values()} for (t, s) in sequence]
        self.array.plot_sequence(sequence)
    
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
        

""" begin analog voltage editor """
class AnalogVoltageEditor(QtGui.QDialog):
    def __init__(self, sequence, parent=None):
        super(AnalogVoltageEditor, self).__init__(parent)
        self.sequence = sequence
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
                                    ('t', [1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1), 
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
        self.cols = [RampColumn() for i in range(max_columns)]
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

    
class AnalogVoltageEditor(QtGui.QDialog):
    def __init__(self, channel, sequence, parent=None):
        super(AnalogVoltageEditor, self).__init__(parent)
        self.channel = channel
        self.sequence = sequence

        self.ramp_dict = {
                          'linear': LinearRamp,
                          'exp': ExpRamp,
                          'step': StepRamp,
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
        
#        self.layout.addWidget(self.load_and_save)
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

        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.buttons.button(QtGui.QDialogButtonBox.Ok).setDefault(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        width = self.canvas.width()
        height = self.nav.height() + self.canvas.height() + self.ramp_scroll.height() + self.load_and_save.height()
        self.setFixedSize(width, height)
        self.set_columns()
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
    
#    def set_columns(self, infos):
#        self.loading = True
#        for c in self.ramp_table.cols:
#            c.hide()
#        
#        for info, c in zip(infos, self.ramp_table.cols):
#            t, p =  info
#            c.show()
#            c.ramp_select.setCurrentIndex(c.ramp_select.findText(t))
#            for k, v in p.items():
#                c.parameter_widgets[t].p_boxes[k].display(v)
#        self.loading = False
#        self.replot()

    def set_columns(self):
        self.loading = True
        for c in self.ramp_table.cols:
            c.hide()

        for s, c in zip(self.sequence, self.ramp_table.cols):
            t, d = s
            d[self.channel].update({'t': t})
            ramp_type = d[self.channel]['type']
            c.show()
            c.ramp_select.setCurrentIndex(c.ramp_select.findText(ramp_type))
            for k, v in d[self.channel].items():
                if k not in ['length', 'type']:
                    c.parameter_widgets[ramp_type].p_boxes[k].display(v)
        self.loading = False
        self.replot()

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

    def set_sequence(self, sequence):
        self.sequence = sequence
        self.set_columns()
        

    def get_plottable_sequence(self):
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

    def get_sequence(self):
        ramp_types = [str(c.ramp_select.currentText()) for c in self.ramp_table.cols if not c.isHidden()]
        ramp_parameters = [{k: b.value() for k, b in c.stack.currentWidget().p_boxes.items()} for c in self.ramp_table.cols if not c.isHidden()]
        ramp_parameters = [merge_dicts(rp, {'type': rt}) for rp, rt in zip(ramp_parameters, ramp_types)]
        channel_sequence = [(rp['t'], {self.channel: rp }) for rp in ramp_parameters]
        self.sequence = [(cs[0], merge_dicts(s[1], cs[1])) for s, cs in zip(self.sequence, channel_sequence)]
        return self.sequence

    def replot(self):
        if not self.loading:
            T, V =  self.get_plottable_sequence()
            self.canvas.make_figure(T, V)
            self.canvas.draw()

    @staticmethod
    def getEditedSequence(channel, sequence, parent=None):
        old_sequence = sequence
        dialog = AnalogVoltageEditor(channel, sequence, parent)
        result = dialog.exec_()
        new_sequence = dialog.get_sequence()
        if result == QtGui.QDialog.Accepted:
            return new_sequence
        else:
            return old_sequence

    def keyPressEvent(self, c):
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if c.key() == QtCore.Qt.Key_Return:
                self.buttons.accepted.emit()
            if c.key() == QtCore.Qt.Key_Q:
                self.buttons.rejected.emit()
        else:
            QtGui.QWidget().keyPressEvent(c)

""" end analog voltage editor """


class Sequencer(QtGui.QWidget):
    def __init__(self, reactor=None, cxn=None):
        super(Sequencer, self).__init__(None)
        self.digital_servername = 'yesr20_digital_sequencer'
        self.analog_servername = 'yesr20_analog_sequencer'
        self.cxn = cxn
        self.reactor = reactor
        self.connect()

        self.sequence_history = []
        self.sequence_history_index = 0

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()  
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            dserver = yield self.cxn.get_server(self.digital_servername)
            dc = yield dserver.get_channels()
            self.digital_channels = eval(dc)
            aserver = yield self.cxn.get_server(self.analog_servername)
            ac = yield aserver.get_channels()
            self.analog_channels = eval(ac)
            self.populate()
            self.default_sequence = [(1, dict([(name, {'type': 'linear', 'v': 0, 'length': (1, 1)}) for name in self.analog_channels.values()] + [(name, 0) for name in self.digital_channels.values()]), )]
            self.set_sequence(self.default_sequence)
        except Exception, e:
            print e
            self.setDisabled(True)


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

        self.setWindowTitle('sequencer control')

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
        self.browse_and_save.save_button.clicked.connect(self.run_sequence)
        self.browse_and_save.browse_button.clicked.connect(self.browse)

        for i, b in enumerate(self.add_dlt_row.buttons):
            b.add.clicked.connect(self.add_column(i))
            b.dlt.clicked.connect(self.dlt_column(i))

        for l in self.digital_sequencer.name_column.labels.values():
            l.clicked.connect(self.open_digital_manual(l.name))

        for l in self.analog_sequencer.name_column.labels.values():
            l.clicked.connect(self.edit_analog_voltage(l.name))

    def open_digital_manual(self, channel_name):
        def odm():
            config = dcc.ControlConfig()
            config.name = channel_name
            widget = dcc.DigitalManualControl(config)
            dialog = QtGui.QDialog()
            dialog.ui = widget
            dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            widget.show()
            pos = QtGui.QCursor().pos()
            print pos
            pos = pos - QtCore.QPoint(100, 50)
            widget.move(pos)
        return odm


    def edit_analog_voltage(self, channel_name):
        def eav():
            sequence = AnalogVoltageEditor(channel_name, self.get_sequence()).getEditedSequence(channel_name, self.get_sequence())
            self.set_sequence(sequence)
        return eav

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
        file_name = QtGui.QFileDialog().getOpenFileName(directory='.')
        self.browse_and_save.location_box.setText(file_name)
        self.load_sequence(file_name)
    
    def save_sequence(self):
        sequence = [str(seq) + '\n' for seq in self.get_sequence()]
        outfile = open(self.browse_and_save.location_box.text(), 'w')
        outfile.write(''.join(sequence))

    @inlineCallbacks
    def run_sequence(self, c):
        #filename = str(self.browse_and_save.location_box.text())
        sequence = json.dumps(self.get_sequence())
        aserver = yield self.cxn.get_server(self.analog_servername)
        #fn = yield aserver.run_sequence_from_file(filename)
        yield aserver.run_sequence(sequence)
        dserver = yield self.cxn.get_server(self.digital_servername)
        #fn = yield dserver.run_sequence_from_file(filename)
        yield dserver.run_sequence(sequence)

    def load_sequence(self, file_name):
        infile = open(file_name, 'r')
        sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
        self.set_sequence(sequence)

    def set_sequence(self, sequence):
        self.sequence_history.insert(0, sequence)
        if len(self.sequence_history) > 20:
            self.sequence_history.pop(-1)
        for i in range(self.sequence_history_index):
            self.sequence_history.pop(i)
        self.sequence_history_index = 0

        self.display_sequence()


    def display_sequence(self):
        self.sequence_history_index = sorted([0, self.sequence_history_index, 20])[1]
        sequence = self.sequence_history[self.sequence_history_index]
        
        self.sequence_history.append(sequence)
        self.analog_sequencer.display_sequence(sequence)
        self.digital_sequencer.display_sequence(sequence)
        self.duration_row.display_sequence(sequence)
        self.add_dlt_row.display_sequence(sequence)
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

    def undo(self):
        self.sequence_history_index += 1
        self.display_sequence()

    def redo(self):
        self.sequence_history_index -= 1
        self.display_sequence()

    def keyPressEvent(self, c):
        super(Sequencer, self).keyPressEvent(c)
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if c.key() == QtCore.Qt.Key_Z:
                self.undo()
            if c.key() == QtCore.Qt.Key_R:
                self.redo()
            if c.key() == QtCore.Qt.Key_S:
                self.save_sequence()
                self.run_sequence(c)

    def closeEvent(self, x):
        self.reactor.stop()
#        
#digital_channels = {
#                    'A00': {'name': '3D MOT AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A01': {'name': '3D MOT Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A02': {'name': 'Fluores. AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A03': {'name': 'Fluores. Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A04': {'name': 'Abs. AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A05': {'name': 'Abs. Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A06': {'name': 'TC Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A07': {'name': 'Zeeman Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'A08': {'name': 'TTLA08', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A09': {'name': 'TTLA09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A10': {'name': 'TTLA10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A11': {'name': 'TTLA11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A12': {'name': 'TTLA12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A13': {'name': 'TTLA13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A14': {'name': 'TTLA14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'A15': {'name': 'TTLA15', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#
#                    'B00': {'name': 'TTLB00', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B01': {'name': 'TTLB01', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B02': {'name': 'TTLB02', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B03': {'name': 'TTLB03', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B04': {'name': 'TTLB04', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B05': {'name': 'TTLB05', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B06': {'name': 'TTLB06', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B07': {'name': 'TTLB07', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B08': {'name': 'TTLB08', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B09': {'name': 'TTLB09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B10': {'name': 'TTLB10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B11': {'name': 'TTLB11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B12': {'name': 'TTLB12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B13': {'name': 'TTLB13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B14': {'name': 'TTLB14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'B15': {'name': 'TTLB15', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#
#                    'C00': {'name': 'TTLC00', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C01': {'name': 'TTLC01', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C02': {'name': 'TTLC02', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C03': {'name': 'TTLC03', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C04': {'name': 'TTLC04', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C05': {'name': 'TTLC05', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C06': {'name': 'TTLC06', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C07': {'name': 'TTLC07', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C08': {'name': 'TTLC08', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C09': {'name': 'TTLC09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C10': {'name': 'TTLC10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C11': {'name': 'TTLC11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C12': {'name': 'TTLC12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C13': {'name': 'TTLC13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C14': {'name': 'TTLC14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'C15': {'name': 'TTLC15', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#
#                    'D00': {'name': 'Alpha AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D01': {'name': 'Alpha Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D02': {'name': 'Beta AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D03': {'name': 'Beta Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D04': {'name': 'Spin pol. AOM', 'mode': 'auto', 'manual state': 0, 'invert': 1},
#                    'D05': {'name': 'Spin pol. Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D06': {'name': '679 AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D07': {'name': '707 AOM', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D08': {'name': 'Repump Shutter', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D09': {'name': 'TTLD09', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D10': {'name': 'TTLD10', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D11': {'name': 'TTLD11', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D12': {'name': 'TTLD12', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D13': {'name': 'TTLD13', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D14': {'name': 'TTLD14', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    'D15': {'name': 'TTLD15', 'mode': 'auto', 'manual state': 0, 'invert': 0},
#                    }
#digital_channels = {k: d['name'] for k, d in digital_channels.items()}
#
#analog_channels = {
#            'A00': 'DACA00',
#            'A01': 'DACA01',
#            'A02': 'DACA02',
#            'A03': 'DACA03',
#            'A04': 'DACA04',
#            'A05': 'DACA05',
#            'A06': 'DACA06',
#            'A07': 'DACA07',
#            }
#
#
#sequence = [(1, dict([(name, {'type': 'linear', 'v': 0, 'length': (1, 1)}) for name in analog_channels.values()] + [(name, 0) for name in digital_channels.values()]), )]*19
#
#
#import labrad
#cxn = labrad.connect()
#seq = cxn.sequencer
#channels = seq.get_channels()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Sequencer(reactor)
    widget.show()
    reactor.run()
