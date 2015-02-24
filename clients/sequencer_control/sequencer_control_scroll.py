from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

sbwidth = 60
sbheight = 15
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
    def __init__(self):
        super(SequencerButton, self).__init__(None)
        self.setFixedSize(sbwidth, sbheight)
        self.setFrameShape(2)
        self.setLineWidth(1)
        #self.setAutoFillBackground(True)
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
        self.setFixedSize(sbwidth, sbheight)

class DelButton(QtGui.QPushButton):
    def __init__(self):
        super(DelButton, self).__init__(None)
        #self.setCheckable(1)
        self.setText('Del')
        self.setFixedSize(sbwidth, sbheight)

class TimingBox(QtGui.QDoubleSpinBox):
    def __init__(self):
        super(TimingBox,  self).__init__(None)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.setDecimals(2)
        self.setValue(1)
        self.setRange(1e-5, 10000)
#        self.setStyleSheet('QWidget {background-color: #eeeeee}') # set widget background
        self.setFixedSize(sbwidth, sbheight)

class TimingRow(QtGui.QWidget):
    def __init__(self, num_columns):
        super(TimingRow, self).__init__(None)
        self.populate(num_columns)
        #self.set_timing(initial_times)

    def populate(self, num_columns):
        self.timing_boxes = [TimingBox() for i in range(num_columns)]
        self.layout = QtGui.QHBoxLayout()
        for tb in self.timing_boxes:
            self.layout.addWidget(tb)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def get_timing(self):
        return [tb.value() for tb in self.timing_boxes]

    def set_timings(self, times):
        for tb, t in zip(self.timing_boxes, times):
            tb.setValue(t)

class LogicColumn(QtGui.QWidget):
    def __init__(self, num_rows):
        super(LogicColumn, self).__init__(None)
        self.populate(num_rows)

    def populate(self, num_rows):
        self.sequencer_buttons = [SequencerButton() for i in range(num_rows)]
        self.add_button = AddButton()
        self.del_button = DelButton()

        self.layout = QtGui.QVBoxLayout()
        
        for i, sb in enumerate(self.sequencer_buttons):
            if not i%15:
                self.layout.addWidget(Spacer(sbheight/2, sbwidth))
            self.layout.addWidget(sb)
        self.layout.addWidget(Spacer(sbheight/2, sbwidth))
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.del_button)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def get_logic(self):
        return [int(sb.isChecked()) for sb in self.sequencer_buttons]

    def set_logic(self, logic):
        for sb, l in zip(self.sequencer_buttons, logic):
            sb.setChecked(l)

class LogicArray(QtGui.QWidget):
    def __init__(self, num_rows, num_columns):
        super(LogicArray, self).__init__(None)
        self.logic_columns = [LogicColumn(num_rows) for i in range(num_columns)]
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
        self.layout.setContentsMargins(0, 0, 10, 0)
        for i, nb in enumerate(self.name_boxes):
            if not i%15:
                self.layout.addWidget(Spacer(sbheight/2, nbwidth))
            self.layout.addWidget(nb)
        self.layout.addWidget(Spacer(sbheight/2, nbwidth))
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
        from sequencerconfig import SequencerConfig
        conf = SequencerConfig()
        self.names = [k + ': ' + conf.channels[k] for k in sorted(conf.channels.keys())]
        yield None

    def initialize(self):
        self.browse_and_run = BrowseAndRun()
        self.name_column = NameColumn(self.names)
        self.logic_array = LogicArray(len(self.names), maxcols)
        self.timing_row = TimingRow(maxcols)
 
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.browse_and_run, 0, 1, 1, 100000)

#        self.layout.addWidget(self.scroll_area, 1, 1)

        self.layout.addWidget(self.timing_row, 1, 1)
        self.layout.addWidget(self.name_column, 2, 0)
        self.layout.addWidget(self.logic_array, 2, 1)

        self.browse_and_run.run_button.clicked.connect(self.save_sequence)
        self.browse_and_run.run_button.clicked.connect(self.program_sequence)
        self.browse_and_run.browse_button.clicked.connect(self.browse)
        for i, lc in enumerate(self.logic_array.logic_columns):
            lc.del_button.clicked.connect(self.del_row(i))
        for i, lc in enumerate(self.logic_array.logic_columns):
            lc.add_button.clicked.connect(self.add_row(i))
        
#        self.setStyleSheet('QWidget {background-color: #f4a460}') # set widget background
        for tb in reversed(self.timing_row.timing_boxes):
            tb.hide()
        for lc in reversed(self.logic_array.logic_columns):
            lc.hide()
        self.name_column.hide()
        
#        meta_widget = QtGui.QWidget()
#        meta_layout = QtGui.QVBoxLayout()
#        meta_layout.setContentsMargins(0, 0, 0, 0)
#        meta_layout.setSpacing(0)
#        scroll_area = QtGui.QScrollArea()
#        meta_widget.setLayout(self.layout)
#        scroll_area.setWidget(meta_widget)
#        meta_layout.addWidget(scroll_area)
        


        self.setLayout(self.layout)


    def resize(self, sequence):
        self.setFixedWidth(nbwidth+36+sbwidth*max(10,len(sequence)))

    def browse(self):
        file_name = QtGui.QFileDialog().getOpenFileName()
        try:
            self.browse_and_run.sequence_location_box.setText(file_name)
            sequence = self.load_sequence(file_name)
            self.display_sequence(sequence)
            self.browse_and_run.sequence_location_box.setText(file_name)
        except Exception, e:
            print e
            print 'could not load file: ', file_name
 
    def save_sequence(self):
        outfile = open(self.browse_and_run.sequence_location_box.text(), 'w')
        array = [str(l) +'\n'  for l in self.get_sequence()]
        outfile.write(''.join(array))

    def program_sequence(self):
        print self.get_sequence()

  
    def load_sequence(self, file_name):
        infile = open(file_name, 'r')
        return [eval(l.split('\n')[:-1][0]) for l in infile.readlines()]

    def display_sequence(self, sequence):
        self.name_column.show()
        for tb, lc, seq in zip(self.timing_row.timing_boxes, self.logic_array.logic_columns, sequence):
            timing, logic = seq
            tb.show()
            tb.setValue(timing)
            lc.show()
            lc.set_logic(logic)

    def get_sequence(self):
        return [(tb.value(), lc.get_logic()) for tb, lc in zip(self.timing_row.timing_boxes, self.logic_array.logic_columns) if not lc.isHidden()]
    
    def add_row(self, i):
        def ar():
            sequence = self.get_sequence()
            sequence.insert(i+1, sequence[i])
            self.display_sequence(sequence)
            self.resize(sequence)
        return ar

    def del_row(self, i):
        def dr():
            sequence = self.get_sequence()
            sequence.pop(i)
            self.display_sequence(sequence)
            self.timing_row.timing_boxes[len(sequence)].hide()
            self.logic_array.logic_columns[len(sequence)].hide()
            self.resize(sequence)
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
