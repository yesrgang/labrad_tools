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

import numpy as np
import matplotlib.pyplot as plt
# start with sequence 
seq = [{'type': 'exp', 'dt': 1.0, 'vi': 2.0, 'vf': 5, 'tau': .5, 'pts': 5}, 
       {'type': 'exp', 'dt': 1.0, 'vf': 0, 'tau': -.5, 'pts': 5},
       {'type': 'sub', 'seq': [{'type': 'exp', 'dt': 1.0, 'vf': 5, 'tau': .5, 'pts': 5}, 
                                {'type': 'exp', 'dt': 1.0, 'vf': 2, 'tau': -.5, 'pts': 5}]},
      ]

class RampMaker(object):
    def __init__(self, sequence):
        self.available_ramps = {
            'lin': LinRamp,
            'slin': LinRamp,
            's': LinRamp,
            'exp': ExpRamp,
            'sexp': ExpRamp,
            }
        j=0
        for i, s in enumerate(sequence):
            if s['type'] is 'sub':
                seq = sequence.pop(i+j)['seq']
                for ss in s['seq']:
                    sequence.insert(i+j, ss)
                    j += 1

        if not sequence[0].has_key('vi'):
            sequence[0]['vi'] = 0
        for i in range(1, len(sequence)):
            if not sequence[i].has_key('vi'):
                sequence[i]['vi'] = sequence[i-1]['vf']
            if not sequence[i].has_key('vf'):
                sequence[i]['vf'] = sequence[i]['vi']

        for i, s in enumerate(sequence):
            s['ti'] = sum([ss['dt'] for ss in sequence[:i]])
            s['tf'] = s['ti'] + s['dt']
        
        self.v = lambda t: sum([self.available_ramps[s['type']](s).v(t) for s in sequence])
        self.sequence = sequence

    def get_points(self):
        T = np.concatenate([np.linspace(s['ti'], s['tf'], 100)[:-1] for s in self.sequence])
        V = self.v(T)
        return T, V


def H(x):
    return 0.5*(np.sign(x-1e-9)+1)

def G(t1, t2):
    return lambda t: H(t2-t) - H(t1-t) 

class LinRamp(object):
    def __init__(self, p):
        self.v = lambda t: G(p['ti'], p['tf'])(t)*(p['vi'] + (p['vf']-p['vi'])/(p['tf']-p['ti'])*(t-p['ti']))

class ExpRamp(object):
    def __init__(self, p):
        p['a'] = (p['vf']-p['vi'])/(np.exp(p['dt']/p['tau'])-1)
        p['c'] = p['vi'] - p['a']
        v_ideal = lambda t: G(p['ti'], p['tf'])(t)*(p['a']*np.exp((t-p['ti'])/p['tau']) + p['c'])
        t_pts = np.linspace(p['ti'], p['tf']-2e-9, p['pts']+1)
        v_pts = v_ideal(t_pts)
        sseq = [{'type': 'lin', 'ti': ti, 'tf': tf, 'vi': vi, 'vf': vf} for ti, tf, vi, vf in zip(t_pts[:-1], t_pts[1:], v_pts[:-1], v_pts[1:])]
        self.v = lambda t: sum([LinRamp(ss).v(t) for ss in sseq])


ramp = RampMaker(seq)
plt.plot(*ramp.get_points())
plt.show()

""" 
Work on analog voltage editor
"""

class ParameterWidget(QtGui.QWidget):
    def __init__(self, ramp_type, parameters):
        """
        parameters is [(parameter_label, range, suffixes, num_decimals)]
        """
        super(ParameterWidget, self).__init__(None)
        self.ramp_type = ramp_type
        self.parameters = parameters
        self.populate()

    def populate(self):
        self.layout = QtGui.QGridLayout()
        self.pboxes = {}
        if self.ramp_type is 'sub':
            r, s, n = dict(self.parameters)['dt']
            label, self.pboxes['dt'] = self.make_pbox('dt', r, s, n)
            self.subbox = QtGui.QTextEdit()
            self.subbox.setLineWrapMode(0)
            self.subbox.setFixedWidth(80+30+2)
            self.subbox.setFixedHeight(4*20)
            self.subbox.setHorizontalScrollBarPolicy(1)
            self.subbox.setVerticalScrollBarPolicy(1)
            self.subbox.setText('')
            self.edit_button = QtGui.QPushButton('Edit')
            self.layout.addWidget(self.subbox)
            self.layout.addWidget(self.edit_button)

        else:
            for i, (p,( r, s, n)) in enumerate(self.parameters):
                label, self.pboxes[p] = self.make_pbox(*(p, r, s, n))
                self.layout.addWidget(QtGui.QLabel(label), i, 0)
                self.layout.addWidget(self.pboxes[p], i, 1)
        self.setFixedWidth(80+30+4)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(QtGui.QFrame())
        self.setLayout(self.layout)

    def make_pbox(self, p, r, s, n):
        pbox = SuperSpinBox(r, s, n)
        pbox.display(1)
        label = QtGui.QLabel(p+': ')
        label.setFixedWidth(30)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        pbox.setFixedWidth(80)
        pbox.setFixedHeight(20)
        return p, pbox


class RampColumn(QtGui.QGroupBox):
    def __init__(self):
        super(RampColumn, self).__init__(None)
        self.populate()

    def populate(self):
        available_ramps = {
                           's': [
                                ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                                ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                                ],
                           'lin': [
                                ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                                ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                                ],
                           'slin': [
                                ('vi', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                                ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                                ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                                ],
                           'exp': [
                                ('vf', ([-10, 10], [(0, 'V')], 3)),
                                ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                                ('tau', ([-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')], 1)),
                                ('pts', ([1, 10], [(0, 'na')], 0)),
                                ],
                           'sexp': [
                                ('vi', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                                ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                                ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                                ('tau', ([-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')], 1)),
                                ('pts', ([1, 10], [(0, 'na')], 0)),
                                ],
                           'sub': [
                                ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)),
                                ('seq', ([{'type': 'lin', 'vf': 0.0, 'dt': 1.0}])),
                                ]
                           }
       
        self.add = QtGui.QPushButton('+')
        self.dlt = QtGui.QPushButton('-')
        self.ramp_select = QtGui.QComboBox()
        self.ramp_select.addItems(available_ramps.keys())
        self.parameter_widgets = {k: ParameterWidget(k, parameters) for k, parameters in available_ramps.items()}
        self.stack = QtGui.QStackedWidget()
        for k, pw in self.parameter_widgets.items():
            self.stack.addWidget(pw)
        
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.add, 0, 0)
        self.layout.addWidget(self.dlt, 0, 1)
        self.layout.addWidget(self.ramp_select, 0, 2)
        self.layout.addWidget(self.stack, 1, 0, 1, 3)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.add.setFixedSize(15, 20) # w, h
        self.dlt.setFixedSize(15, 20) # w, h
        self.ramp_select.setFixedWidth(80)
        self.ramp_select.setFixedHeight(20)
        self.setFixedWidth(30+80+4)

        self.ramp_select.currentIndexChanged.connect(self.select_from_stack)
        rs_def_index = self.ramp_select.findText('lin')
        self.ramp_select.setCurrentIndex(rs_def_index)

    def select_from_stack(self):
#        prev_ramp_type = self.ramp_type
        self.ramp_type = str(self.ramp_select.currentText())
#        for p in self.parameter_widgets[prev_ramp_type].parameters:
#            try:
#                self.parameterwidgets[self.ramp_type].

        self.stack.setCurrentWidget(self.parameter_widgets[self.ramp_type])

    def get_ramp(self):
        ramp_type = str(self.ramp_select.currentText())
        ramp = {'type': str(self.ramp_select.currentText())}
        if ramp['type'] != 'sub':
            ramp.update({k: b.value() for k, b in self.stack.currentWidget().pboxes.items()})
        else:
            ramp.update({'seq': eval('['+str(self.stack.currentWidget().subbox.toPlainText())+']')})
        return ramp

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
        
available_ramps = {
                   's': [
                        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                        ],
                   'lin': [
                        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                        ],
                   'slin': [
                        ('vi', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                        ],
                   'exp': [
                        ('vf', ([-10, 10], [(0, 'V')], 3)),
                        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                        ('tau', ([-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')], 1)),
                        ('pts', ([1, 10], [(0, 'na')], 0)),
                        ],
                   'sexp': [
                        ('vi', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
                        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
                        ('tau', ([-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')], 1)),
                        ('pts', ([1, 10], [(0, 'na')], 0)),
                        ],
                   'sub': [
                        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)),
                        ('seq', ([{'type': 'lin', 'vf': 0.0, 'dt': 1.0}])),
                        ]
                   }


if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
#    widget = ParameterWidget('s', available_ramps['s'])
    widget = RampTable()
    widget.show()
    reactor.run()
