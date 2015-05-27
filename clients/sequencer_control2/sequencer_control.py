from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
from connection import connection
from twisted.internet.defer import inlineCallbacks
import numpy as np

sbwidth = 65
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

class LogicColumn(QtGui.QWidget):
    def __init__(self, channels):
        super(LogicColumn, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.sequencer_buttons = {n: SequencerButton(0) for n in self.channels.values()}

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        for i, (c, n) in enumerate(sorted(self.channels.items())):
            if not i%16 and i != 0:
                self.layout.addWidget(Spacer(sbheight/2, sbwidth))
            self.layout.addWidget(self.sequencer_buttons[n])
        self.setLayout(self.layout)
        height = 0
        for i in range(self.layout.count()):
            height += self.layout.itemAt(i).widget().height()
        self.setFixedSize(sbwidth, height)

    def get_logic(self):
        return {n: int(self.sequencer_buttons[n].isChecked()) for n in self.channels.values()}

    def set_logic(self, logic):
        for i, s in enumerate(logic):
            self.sequencer_buttons[i].setChecked(s)

class LogicArray(QtGui.QWidget):
    def __init__(self, channels):
        super(LogicArray, self).__init__(None)
        self.populate()

    def populate(self):
        self.logic_columns = [LogicColumn(channels) for i in range(10)]
        self.layout = QtGui.QHBoxLayout()
        for lc in self.logic_columns:
            self.layout.addWidget(lc)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        height = self.logic_columns[0].height()
        width = self.logic_columns[0].width()*10
        self.setFixedSize(width, height)

class NameBox(QtGui.QLabel):
    def __init__(self, name):
        super(NameBox, self).__init__(None)
        self.setText(name)
        self.setFixedSize(nbwidth, sbheight)
        self.setAlignment(QtCore.Qt.AlignRight)

class NameColumn(QtGui.QWidget):
    def __init__(self, channels):
        super(NameColumn, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.name_boxes = {n: NameBox(c+': '+n) for c, n in self.channels.items()}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 5, 0)

        for i, (c, n) in enumerate(sorted(self.channels.items())):
            if not i%16 and i != 0:
                self.layout.addWidget(Spacer(sbheight/2, nbwidth))
            self.layout.addWidget(self.name_boxes[n])
        self.setLayout(self.layout)

class DurationRow(QtGui.QWidget):
    def __init__(self):
        super(DurationRow, self).__init__(None)
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.duration_boxes = [SuperSpinBox([500e-9, 10], units) for i in range(10)]
        self.layout = QtGui.QHBoxLayout()
        for db in self.duration_boxes:
            db.setFixedSize(sbwidth, 20)
            self.layout.addWidget(db)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(sbwidth*10)

class AddDltButton(QtGui.QWidget):
    def __init__(self):
        super(AddDltButton, self).__init__(None)
        self.add = QtGui.QPushButton('+')
        self.add.setFixedSize(sbwidth/2, 15)
        self.dlt = QtGui.QPushButton('-')
        self.dlt.setFixedSize(sbwidth/2, 15)
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.add)
        self.layout.addWidget(self.dlt)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(sbwidth, 15)

class AddDltRow(QtGui.QWidget):
    def __init__(self):
        super(AddDltRow, self).__init__(None)
        self.populate()

    def populate(self):
        self.add_dlt = [AddDltButton() for i in range(10)]
        self.layout = QtGui.QHBoxLayout()
        for ad in self.add_dlt:
            self.layout.addWidget(ad)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(sbwidth*10)

class NameAndLogic(QtGui.QWidget):
    def __init__(self, channels):
        super(NameAndLogic, self).__init__(None)
        self.channels = channels
        self.populate()

    def populate(self):
        self.name_column = NameColumn(channels)
        self.logic_array = LogicArray(channels)
        self.duration_row = DurationRow()
        self.add_dlt_row = AddDltRow()

        self.name_scroll = QtGui.QScrollArea()
        self.name_scroll.setWidget(self.name_column)
        self.name_scroll.setWidgetResizable(True)
        self.logic_scroll = QtGui.QScrollArea()
        self.logic_scroll.setWidget(self.logic_array)
        self.logic_scroll.setWidgetResizable(True)
        self.duration_scroll = QtGui.QScrollArea()
        self.duration_scroll.setWidget(self.duration_row)
        self.duration_scroll.setWidgetResizable(True)
        self.add_dlt_scroll = QtGui.QScrollArea()
        self.add_dlt_scroll.setWidget(self.add_dlt_row)
        self.add_dlt_scroll.setWidgetResizable(True)

        self.vscroll = QtGui.QScrollArea()
        self.vscroll.setWidget(Spacer(self.logic_array.height(), 0))
        self.vscroll.setWidgetResizable(True)
        
        self.hscroll = QtGui.QScrollArea()
        self.hscroll.setWidget(Spacer(0, self.logic_array.width()))
        self.hscroll.setWidgetResizable(True)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.duration_scroll, 0, 1)
        self.layout.addWidget(self.name_scroll, 1, 0)
        self.layout.addWidget(self.logic_scroll, 1, 1)
        self.layout.addWidget(self.add_dlt_scroll, 2, 1)
        self.layout.addWidget(self.vscroll, 1, 2)
        self.layout.addWidget(self.hscroll, 3, 1)
        self.setLayout(self.layout)
        
        self.duration_scroll.setHorizontalScrollBarPolicy(1)
        self.duration_scroll.setVerticalScrollBarPolicy(1)
        self.duration_scroll.setFrameShape(0)
        self.duration_scroll.setFixedHeight(25)

        self.name_scroll.setHorizontalScrollBarPolicy(1)
        self.name_scroll.setVerticalScrollBarPolicy(1)
        self.name_scroll.setMaximumWidth(100)
        self.name_scroll.setFrameShape(0)
        
        self.logic_scroll.setHorizontalScrollBarPolicy(1)
        self.logic_scroll.setVerticalScrollBarPolicy(1)
        self.logic_scroll.setFrameShape(0)
        
        self.add_dlt_scroll.setHorizontalScrollBarPolicy(1)
        self.add_dlt_scroll.setVerticalScrollBarPolicy(1)
        self.add_dlt_scroll.setFrameShape(0)
        self.add_dlt_scroll.setFixedHeight(15)
        
        self.vscroll.setHorizontalScrollBarPolicy(1)
        self.vscroll.setVerticalScrollBarPolicy(2)
        self.vscroll.setFixedWidth(20)
        self.vscroll.setFrameShape(0)
        
        self.hscroll.setHorizontalScrollBarPolicy(2)
        self.hscroll.setVerticalScrollBarPolicy(1)
        self.hscroll.setFixedHeight(20)
        self.hscroll.setFrameShape(0)

        self.name_column.setFixedHeight(self.logic_array.height())
        self.vscroll.verticalScrollBar().valueChanged.connect(self.adjust_for_vscroll)
        self.hscroll.horizontalScrollBar().valueChanged.connect(self.adjust_for_hscroll)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 10, 10, 10)
        height = self.duration_scroll.height() + self.logic_array.height() + self.add_dlt_scroll.height() + self.hscroll.height()
        print self.add_dlt_row.height()

        self.setMaximumHeight(height+25)

    def adjust_for_vscroll(self):
        val = self.vscroll.verticalScrollBar().value()
        self.name_scroll.verticalScrollBar().setValue(val)
        self.logic_scroll.verticalScrollBar().setValue(val)

    def adjust_for_hscroll(self):
        val = self.hscroll.horizontalScrollBar().value()
        self.duration_scroll.horizontalScrollBar().setValue(val)
        self.logic_scroll.horizontalScrollBar().setValue(val)
        self.add_dlt_scroll.horizontalScrollBar().setValue(val)



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
        self.scrollarea.setFixedHeight(self.logic_array.height()+18)
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

channels = {
            'A00': 'TTL00',
            'A01': 'TTL01',
            'A02': 'TTL02',
            'A03': 'TTL03',
            'A04': 'TTL04',
            'A05': 'TTL05',
            'A06': 'TTL06',
            'A07': 'TTL07',
            'A08': 'TTL08',
            'A09': 'TTL09',
            'A10': 'TTL10',
            'A11': 'TTL11',
            'A12': 'TTL12',
            'A13': 'TTL13',
            'A14': 'TTL14',
            'A15': 'TTL15',
            'A16': 'TTL16',
            'A17': 'TTL17',
            }

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
#    widget = SequencerClient(reactor)
    widget = LogicArray(channels)
    widget = NameAndLogic(channels)

    widget.show()
    reactor.run()
