from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np


class SequencerButton(QtGui.QPushButton):
    def __init__(self, initial_state):
        super(SequencerButton, self).__init__(None)
        self.setCheckable(1)
        self.setChecked(initial_state)
        self.setFixedSize(60, 20)

#class SequencerButton(QtGui.QFrame):
#    def __init__(self, initial_state):
#        super(SequencerButton, self).__init__(None)
#        self.setFixedSize(60, 20)
#        self.setFrameShape(6)
#        self.setLineWidth(0)
#        self.setAutoFillBackground(True)
#        self.setFrameShadow(2)
#        if initial_state:
#            self.check()
#        else:
#            self.uncheck()
#    
#    def check(self):
#        self.setFrameShadow(3)
#        self.setStyleSheet('QWidget {background-color: #c9c9c9}')
#        self.is_checked = True
#
#    def uncheck(self):
#        self.setFrameShadow(2)
#        self.setStyleSheet('QWidget {background-color: #ffcccc}')
#        self.is_checked = False
#
#    def isChecked(self):
#        if self.is_checked:
#            return True
#        else:
#            return False
#
#    def mousePressEvent(self, x):
#        if self.is_checked:
#            self.uncheck()
#        else:
#            self.check()
#

class AddButton(QtGui.QPushButton):
    def __init__(self):
        super(AddButton, self).__init__(None)
        self.setText('Add')
        self.setCheckable(1)
        self.setFixedSize(60, 20)

class DelButton(QtGui.QPushButton):
    def __init__(self):
        super(AddButton, self).__init__(None)
        self.setCheckable(1)
        self.setText('Del')
        self.setFixedSize(60, 20)

class DurationBox(QtGui.QDoubleSpinBox):
    def __init__(self, initial_duration):
        super(DurationBox,  self).__init__(None)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.setDecimals(2)
        self.setValue(initial_duration)
        self.setRange(1e-5, 10000)
        self.setFixedSize(60, 20)

class LogicColumn(QtGui.QWidget):
    def __init__(self, initial_logic, initial_duration):
        super(LogicColumn, self).__init__(None)
        self.populate(initial_logic, initial_duration)

    def populate(self, logic, duration):
        self.duration_box = DurationBox(duration) 
        self.sequencer_buttons = [SequencerButton(l) for l in logic]
        self.add_button = AddButton()
        self.del_button = QtGui.QPushButton('Del')
        self.del_button.setFixedSize(60, 20)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.duration_box)
        for sb in self.sequencer_buttons:
            self.layout.addWidget(sb)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.del_button)
        self.setLayout(self.layout)

    def get_logic(self):
        return (self.duration_box.value(), [int(sb.isChecked()) for sb in self.sequencer_buttons])

class NameBox(QtGui.QLabel):
    def __init__(self, name):
        super(NameBox, self).__init__(None)
        self.setText(name)
        self.setFixedSize(80, 20)
        self.setAlignment(QtCore.Qt.AlignRight)

class NameColumn(QtGui.QWidget):
    def __init__(self, names):
        super(NameColumn, self).__init__(None)
        self.populate(names)

    def populate(self, names):
        self.name_boxes = [NameBox(n+': ') for n in names]
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        for nb in [NameBox('')] + self.name_boxes + [NameBox('')]*2:
            self.layout.addWidget(nb)
        self.setLayout(self.layout)

class BrowseAndRun(QtGui.QWidget):
    def __init__(self):
        super(BrowseAndRun, self).__init__(None)
        self.populate()

    def populate(self):
        self.sequence_location_box = QtGui.QLineEdit()
        self.browse_button = QtGui.QPushButton('&Browse')
        self.run_button = QtGui.QPushButton('&Run')
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.layout.addWidget(self.sequence_location_box)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.run_button)
        self.setLayout(self.layout)
        self.setFixedSize(10*60, 40)

class SequencerClient(QtGui.QWidget):
    def __init__(self, reactor, cxn=None):
        super(SequencerClient, self).__init__(None)    
        self.server_name = 'sequencer' 
        self.reactor =  reactor
        self.cxn = cxn
        self.layout = None
        self.sequence_location = None
        self.logic_columns = []
        #self.connect()
        self.get_configuration()
        self.populate() # not for real

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            self.get_configuration()
            self.populate()
        except Exception, e:
            print e
            self.setDisabled(True)

    @inlineCallbacks
    def get_configuration(self):
        #server = yield self.cxn.get_server(self.server_name)
        #config_str = yield server.get_configuration()
        #self.config = eval(config_str)
        self.names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.names = ['channel ' + n for n in self.names]
        yield None

    def populate(self, logic=None):
        #if logic is None:
        #    l = [[True]*len(self.names), [False]*len(self.names)]*8
        #    d = [2.0, 3.0]*8
        #    logic = zip(d, l)

        self.browse_and_run = BrowseAndRun()
        if self.layout is None:
            self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.browse_and_run, 0, 1, 1, 100000)
        self.browse_and_run.browse_button.clicked.connect(self.browse)
        self.browse_and_run.run_button.clicked.connect(self.save_sequence)

        if logic:
            self.name_column = NameColumn(self.names)
            self.logic_columns = [LogicColumn(l, t) for t, l in logic]
            self.layout.addWidget(self.name_column, 1, 0)
            for i, lc in enumerate(self.logic_columns):
                self.layout.addWidget(lc, 1, 1+i)

            self.browse_and_run.run_button.clicked.connect(self.get_logic)
            for i, lc in enumerate(self.logic_columns):
                lc.del_button.pressed.connect(self.del_row)
            for i, lc in enumerate(self.logic_columns):
                lc.add_button.pressed.connect(self.add_row)
        
        self.setLayout(self.layout)
        self.setFixedWidth(max(60*(len(self.logic_columns)+2), 640))#, 20*(len(self.names)+7))

    def browse(self):
        file_name = QtGui.QFileDialog().getOpenFileName()
        self.browse_and_run.sequence_location_box.setText(file_name)
        self.load_sequence(file_name)
        self.browse_and_run.sequence_location_box.setText(file_name)
    
    def save_sequence(self):
        logic = self.get_logic()
        array = [ str(l) +'\n'  for l in self.get_logic()]
        outfile = open(self.browse_and_run.sequence_location_box.text(), 'w')
        outfile.write(''.join(array))
        
    def load_sequence(self, file_name):
        infile = open(file_name, 'r')
        logic = [eval(l.split('\n')[:-1][0]) for l in infile.readlines()]
        self.depopulate()
        self.populate(logic)

    def get_logic(self):
        return [lc.get_logic() for lc in self.logic_columns]
    
    def add_row(self):
        logic = self.get_logic()
        for i, lc in enumerate(self.logic_columns):
            if lc.add_button.isDown():
                logic.insert(i+1, logic[i])
        self.depopulate()
        self.populate(logic)

    def del_row(self):
        logic = self.get_logic()
        for i, lc in enumerate(self.logic_columns):
            if lc.del_button.isDown():
                logic.pop(i)
        self.depopulate()
        self.populate(logic)

    def depopulate(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            self.layout.removeWidget(w)
            w.close()

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = SequencerClient(reactor)
    widget.show()
    reactor.run()
