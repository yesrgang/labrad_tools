from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

sbwidth = 60
sbheight = 15
pbheight = 20
nbwidth = 90
maxcols = 100

class Spacer(QtGui.QFrame):
    def __init__(self, height, width):
        super(Spacer, self).__init__(None)
        self.setFixedSize(width, height)
        self.setFrameShape(1)
        self.setLineWidth(0)

class SequencerButton(QtGui.QPushButton):
    def __init__(self, initial_state):
        super(SequencerButton, self).__init__(None)
        self.setCheckable(1)
        self.setChecked(initial_state)
        self.setFixedSize(sbwidth, sbheight)

class SequencerButton(QtGui.QFrame):
    def __init__(self, initial_state):
        super(SequencerButton, self).__init__(None)
        self.setFixedSize(sbwidth, sbheight)
        self.setFrameShape(2)
        self.setLineWidth(1)
        #self.setAutoFillBackground(True)
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


class AddButton(QtGui.QPushButton):
    def __init__(self):
        super(AddButton, self).__init__(None)
        self.setText('Add')
        #self.setCheckable(1)
        self.setFixedSize(sbwidth, pbheight)

class DelButton(QtGui.QPushButton):
    def __init__(self):
        super(DelButton, self).__init__(None)
        #self.setCheckable(1)
        self.setText('Del')
        self.setFixedSize(sbwidth, pbheight)

class DurationBox(QtGui.QDoubleSpinBox):
    def __init__(self, initial_duration):
        super(DurationBox,  self).__init__(None)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.setDecimals(2)
        self.setValue(initial_duration)
        self.setRange(1e-5, 10000)
#        self.setStyleSheet('QWidget {background-color: #eeeeee}') # set widget background
        self.setFixedSize(sbwidth, sbheight)

class LogicColumn(QtGui.QWidget):
    def __init__(self, initial_logic, initial_duration):
        super(LogicColumn, self).__init__(None)
        self.populate(initial_logic, initial_duration)

    def populate(self, logic, duration):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        #self.duration_box = DurationBox(duration)
        self.duration_box = SuperSpinBox([500e-9, 1000], units)
        self.duration_box.display(duration)
        self.sequencer_buttons = [SequencerButton(l) for l in logic]
        self.add_button = AddButton()
        self.del_button = DelButton()

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.duration_box)
        for i, sb in enumerate(self.sequencer_buttons):
            if not i%15:
                self.layout.addWidget(Spacer(sbheight/2, sbwidth))
            self.layout.addWidget(sb)
        self.layout.addWidget(Spacer(sbheight/2, sbwidth))
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.del_button)
        self.setLayout(self.layout)

    def get_logic(self):
        return (self.duration_box.value(), [int(sb.isChecked()) for sb in self.sequencer_buttons])

    def set_logic(self, logic):
        duration, states = logic
        self.duration_box.display(duration)
        #self.duration_box.setValue(duration)
        for i, s in enumerate(states):
            self.sequencer_buttons[i].setChecked(s)

class LogicArray(QtGui.QWidget):
    def __init__(self, num_rows, num_columns):
        super(LogicArray, self).__init__(None)
        self.logic_columns = [LogicColumn(num_rows*[False], 1) for i in range(num_columns)]
        self.layout = QtGui.QHBoxLayout()
        for lc in self.logic_columns:
            self.layout.addWidget(lc)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

class NameBox(QtGui.QLabel):
    def __init__(self, name):
        super(NameBox, self).__init__(None)
        self.setText(name)
        self.setFixedSize(nbwidth, sbheight)
        self.setAlignment(QtCore.Qt.AlignRight)

class NameColumn(QtGui.QGroupBox):
    def __init__(self, names):
        super(NameColumn, self).__init__(None)
        self.populate(names)

    def populate(self, names):
        self.name_boxes = [NameBox(n) for n in names]
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 5, 0)
        self.layout.addWidget(NameBox('')) # blank. browse and run
        for i, nb in enumerate(self.name_boxes):
            if not i%15:
                self.layout.addWidget(Spacer(sbheight/2, nbwidth))
            self.layout.addWidget(nb)
        self.layout.addWidget(Spacer(sbheight/2, nbwidth))
        self.layout.addWidget(NameBox('')) #blank. add button
        self.layout.addWidget(NameBox('')) #blank. del button
        self.setLayout(self.layout)

class BrowseAndRun(QtGui.QWidget):
    def __init__(self):
        super(BrowseAndRun, self).__init__(None)
        self.populate()

    def populate(self):
        self.sequence_location_box = QtGui.QLineEdit()
        self.browse_button = QtGui.QPushButton('Bro&wse')
        self.run_button = QtGui.QPushButton('&Run')
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.sequence_location_box)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.run_button)
        self.setLayout(self.layout)
#        self.setStyleSheet('QWidget {background-color: #eeeeee}') # set widget background
        self.setFixedSize(10*sbwidth, 40)

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
        self.initialize() # not for real

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        self.get_configuration()
        self.populate()

    @inlineCallbacks
    def get_configuration(self):
        #server = yield self.cxn.get_server(self.server_name)
        #config_str = yield server.get_configuration()
        #self.config = eval(config_str)
        from sequencerconfig import SequencerConfig
        conf = SequencerConfig()
        self.names = [k + ': ' + conf.channels[k] for k in sorted(conf.channels.keys())]
        yield None

    def initialize(self):
        self.browse_and_run = BrowseAndRun()
        self.browse_and_run.browse_button.clicked.connect(self.browse)
        self.browse_and_run.run_button.clicked.connect(self.save_sequence)
        self.name_column = NameColumn(self.names)
        self.logic_array = LogicArray(len(self.names), maxcols)
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.browse_and_run, 0, 1, 1, 100000)

        self.scrollarea = QtGui.QScrollArea()
        self.scrollarea.setWidget(self.logic_array)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setFixedHeight(self.logic_array.height()+16)
        self.scrollarea.setFrameShape(0)

        self.layout.addWidget(self.name_column, 1, 0)
#        self.layout.addWidget(self.logic_array, 1, 1)
#        self.layout.addWidget(self.scrollarea, 1, 1)

        self.browse_and_run.run_button.clicked.connect(self.get_logic)
        for i, lc in enumerate(self.logic_array.logic_columns):
            lc.del_button.clicked.connect(self.del_row(i))
        for i, lc in enumerate(self.logic_array.logic_columns):
            lc.add_button.clicked.connect(self.add_row(i))
        
        self.setLayout(self.layout)
#        self.setStyleSheet('QWidget {background-color: #f4a460}') # set widget background
        for lc in reversed(self.logic_array.logic_columns):
            lc.hide()
        self.name_column.hide()

    def resize(self, logic):
        self.scrollarea.setFixedWidth(min(sbwidth*len(logic)+2, 20*sbwidth))
        self.setFixedWidth(min(nbwidth+36+sbwidth*max(10,len(logic)), nbwidth+36+sbwidth*20))

    def browse(self):
        file_name = QtGui.QFileDialog().getOpenFileName()
        self.browse_and_run.sequence_location_box.setText(file_name)
        self.load_sequence(file_name)
        self.browse_and_run.sequence_location_box.setText(file_name)
    
    def save_sequence(self):
        logic = self.get_logic()
        array = [str(l) +'\n'  for l in self.get_logic()]
        outfile = open(self.browse_and_run.sequence_location_box.text(), 'w')
        outfile.write(''.join(array))
        
    def load_sequence(self, file_name):
        if not self.layout.itemAtPosition(1, 1):
            self.layout.addWidget(self.scrollarea, 1, 1)
        infile = open(file_name, 'r')
        logic = [eval(l.split('\n')[:-1][0]) for l in infile.readlines()]
        self.name_column.show()
        self.set_logic(logic)
        self.resize(logic)

    def get_logic(self):
        return [lc.get_logic() for lc in self.logic_array.logic_columns if not lc.isHidden()] # only keep relavent 

    def set_logic(self, logic):
        for col, log in zip(self.logic_array.logic_columns, logic):
            col.show()
            col.set_logic(log)
    
    def add_row(self, i):
        def ar():
            logic = self.get_logic()
            logic.insert(i+1, logic[i])
            self.set_logic(logic)
            self.resize(logic)
        return ar

    def del_row(self, i):
        def dr():
            logic = self.get_logic()
            logic.pop(i)
            self.set_logic(logic)
            self.logic_array.logic_columns[len(logic)].hide()
            self.resize(logic)
        return dr
    
    def closeEvent(self, x):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            self.layout.removeWidget(w)
            w.close()
        self.reactor.stop()

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = SequencerClient(reactor)
    widget.show()
    reactor.run()
