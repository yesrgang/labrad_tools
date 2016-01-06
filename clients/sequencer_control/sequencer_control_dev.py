import json
import numpy as np

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks

import digital_channel_control as dcc
from connection import connection
from client_tools2 import SuperSpinBox
from digital_widgets import DigitalSequencer
from analog_widgets import AnalogSequencer
from analog_editor import AnalogVoltageEditor

from okfpga.sequencer.analog_ramps import RampMaker

def merge_dicts(*dictionaries):
    merged_dictionary = {}
    for d in dictionaries:
        merged_dictionary.update(d)
    return merged_dictionary

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

class DurationRow(QtGui.QWidget):
    def __init__(self, config):
        super(DurationRow, self).__init__(None)
        self.config = config
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.boxes = [SuperSpinBox([500e-9, 10], units) for i in range(self.config.max_columns)]
        self.layout = QtGui.QHBoxLayout()
        for db in self.boxes:
            self.layout.addWidget(db)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def display_sequence(self, sequence):
        for b in self.boxes[::-1]:
            b.hide()
        for dt, b in zip(sequence[self.config.timing_channel], self.boxes):
            b.show()
            b.display(dt)


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
    def __init__(self, config):
        super(AddDltRow, self).__init__(None)
        self.config = config
        self.populate()

    def populate(self):
        self.buttons = [AddDltButton() for i in range(self.config.max_columns)]
        self.layout = QtGui.QHBoxLayout()
        for ad in self.buttons:
            self.layout.addWidget(ad)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
    
    def display_sequence(self, sequence):
        for b in self.buttons[::-1]:
            b.hide()
        for t, b in zip(sequence[self.config.timing_channel], self.buttons):
            b.show()

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


class Sequencer(QtGui.QWidget):
    sequence_parameters = {}
    def __init__(self, config, reactor=None, cxn=None):
        super(Sequencer, self).__init__(None)
        self.config = config
        for key, value in config.__dict__.items():
            setattr(self, key, value)
        self.digital_servername = config.digital_servername #'yesr20_digital_sequencer'
        self.analog_servername = config.analog_servername #'yesr20_analog_sequencer'
        self.config = config
        self.cxn = cxn
        self.reactor = reactor
        self.connect()


    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()  
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            dserver = yield self.cxn.get_server(self.digital_servername)
            dc = yield dserver.get_channels()
            self.digital_channels = json.loads(dc)
	    tc = yield dserver.get_timing_channel()
	    self.timing_channel = json.loads(tc)
	    self.config.timing_channel = json.loads(tc)
            aserver = yield self.cxn.get_server(self.analog_servername)
            ac = yield aserver.get_channels()
            self.analog_channels = json.loads(ac)
	    self.channels = self.digital_channels + self.analog_channels + [self.timing_channel]
	    conductor = yield self.cxn.get_server(self.conductor_servername)
	    yield conductor.signal__update_sp(self.config.conductor_update_id)
	    yield conductor.addListener(listener=self.update_parameters, source=None, ID=self.conductor_update_id)
            self.populate()
            self.default_sequence = dict([(nameloc, [{'type': 'lin', 'vf': 0, 'dt': 1}]) for nameloc in self.analog_channels] + [(nameloc, [0]) for nameloc in self.digital_channels] + [(self.timing_channel, [1])])
            self.set_sequence(self.default_sequence)
        except Exception, e:
            print 'Error', e
            self.setDisabled(True)

    def populate(self):
        self.browse_and_save = BrowseAndSave()

        self.add_dlt_row = AddDltRow(self.config)
        self.add_dlt_row.scroll_area = QtGui.QScrollArea()
        self.add_dlt_row.scroll_area.setWidget(self.add_dlt_row)
        self.add_dlt_row.scroll_area.setWidgetResizable(True)
        self.add_dlt_row.scroll_area.setHorizontalScrollBarPolicy(1)
        self.add_dlt_row.scroll_area.setVerticalScrollBarPolicy(1)
        self.add_dlt_row.scroll_area.setFrameShape(0)

        self.duration_row = DurationRow(self.config)
        self.duration_row.scroll_area = QtGui.QScrollArea()
        self.duration_row.scroll_area.setWidget(self.duration_row)
        self.duration_row.scroll_area.setWidgetResizable(True)
        self.duration_row.scroll_area.setHorizontalScrollBarPolicy(1)
        self.duration_row.scroll_area.setVerticalScrollBarPolicy(1)
        self.duration_row.scroll_area.setFrameShape(0)

        self.digital_sequencer = DigitalSequencer(self.digital_channels, self.config)
        self.analog_sequencer = AnalogSequencer(self.analog_channels, self.config)

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
#        self.setStyleSheet('QWidget {background-color: yellow}')


    def set_sizes(self):
        self.northwest.setFixedSize(self.namecolumn_width, self.durationrow_height)
        self.browse_and_save.setFixedWidth(10*self.spacer_width)
        self.northeast.setFixedSize(20, self.durationrow_height)
        
        for c in self.digital_sequencer.array.columns:
            for b in c.buttons.values():
                b.setFixedSize(self.spacer_width, self.spacer_height)
            height = sum([c.layout.itemAt(i).widget().height() for i in range(c.layout.count()-1)]) # -1 because there is a generic widget in the last spot
            c.setFixedSize(self.spacer_width, height)
        da_width = sum([c.width() for c in self.digital_sequencer.array.columns if not c.isHidden()])
        da_height = self.digital_sequencer.array.columns[0].height()
        self.digital_sequencer.array.setFixedSize(da_width, da_height)

        for nl in self.digital_sequencer.name_column.labels.values():
            nl.setFixedHeight(self.spacer_height)
        nc_width = self.namelabel_width
        nc_height = self.digital_sequencer.array.height()
        self.digital_sequencer.name_column.setFixedSize(nc_width, nc_height)
        self.digital_sequencer.name_column.scroll_area.setFixedWidth(self.namecolumn_width)
        
        self.digital_sequencer.vscroll.widget().setFixedSize(0, self.digital_sequencer.array.height())
        self.digital_sequencer.vscroll.setFixedWidth(20)

        self.analog_sequencer.array.setFixedSize(self.digital_sequencer.array.width(), self.analog_height*len(self.analog_channels))
        self.analog_sequencer.vscroll.widget().setFixedSize(0, self.analog_sequencer.array.height())
        self.analog_sequencer.vscroll.setFixedWidth(20)
        
        for nl in self.analog_sequencer.name_column.labels.values():
            nl.setFixedSize(self.namelabel_width, self.analog_height)
        nc_width = self.namelabel_width
        nc_height = self.analog_sequencer.array.height()
        self.analog_sequencer.name_column.setFixedSize(nc_width, nc_height)
        self.analog_sequencer.name_column.scroll_area.setFixedWidth(self.namecolumn_width)
        
        for b in self.duration_row.boxes:
            b.setFixedSize(self.spacer_width, self.durationrow_height)
        dr_width = sum([db.width() for db in self.duration_row.boxes if not db.isHidden()])
        self.duration_row.setFixedSize(dr_width, self.durationrow_height)
        self.duration_row.scroll_area.setFixedHeight(self.durationrow_height)
       
        self.southwest.setFixedSize(self.namecolumn_width, self.durationrow_height)
        self.southeast.setFixedWidth(20)
        
        for b in self.add_dlt_row.buttons:
            b.setFixedSize(self.spacer_width, 15)
        self.add_dlt_row.setFixedSize(dr_width, self.durationrow_height)
        self.add_dlt_row.scroll_area.setFixedHeight(self.durationrow_height)
        
        self.hscroll_array.widget().setFixedSize(self.digital_sequencer.array.width(), 0)
        self.hscroll_array.setFixedHeight(20)
        self.hscroll_name.widget().setFixedSize(self.namelabel_width, 0)
        self.hscroll_name.setFixedSize(self.namecolumn_width, 20)

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
            l.clicked.connect(self.open_digital_manual(l.nameloc))

        for l in self.analog_sequencer.name_column.labels.values():
            l.clicked.connect(self.edit_analog_voltage(l.nameloc))

    def open_digital_manual(self, channel_name):
        def odm():
            config = dcc.ControlConfig()
            config.name = str(channel_name.split('@')[0])
            widget = dcc.DigitalManualControl(config)
            dialog = QtGui.QDialog()
            dialog.ui = widget
            dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            widget.show()
            pos = QtGui.QCursor().pos()
            pos = pos - QtCore.QPoint(100, 50)
            widget.move(pos)
        return odm


    def edit_analog_voltage(self, channel_name):
        def eav():
            ave_args = (channel_name, self.get_sequence(), self.ramp_maker, self.config, self.reactor, self.cxn)
            sequence = AnalogVoltageEditor(*ave_args).getEditedSequence(*ave_args)
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
        file_name = self.browse_and_save.location_box.text()
	with open(file_name, 'w') as outfile:
            sequence = self.get_sequence()
            json.dump(sequence, outfile)

    @inlineCallbacks
    def run_sequence(self, c):
        sequence = json.dumps(self.get_sequence())
#        aserver = yield self.cxn.get_server(self.analog_servername)
#        yield aserver.run_sequence(sequence)
#        dserver = yield self.cxn.get_server(self.digital_servername)
#        yield dserver.run_sequence(sequence)
        conductor = yield self.cxn.get_server(self.conductor_servername)
	yield conductor.load_sequence(sequence)

    def load_sequence(self, file_name):
	with open(file_name, 'r') as infile:
	    sequence = json.load(infile)
	    self.set_sequence(sequence)

    def set_sequence(self, sequence):
        self.display_sequence(sequence)

    @inlineCallbacks
    def get_sequence_paramaters(self):
        conductor = yield self.cxn.get_server(self.conductor_servername)
	sp = yield conductor.set_sequence_parameters()
	self.sequence_parameters = json.loads(sp)

    @inlineCallbacks
    def update_parameters(self, c, signal):
        conductor = yield self.cxn.get_server(self.conductor_servername)
        plottable_sequence = yield conductor.evaluate_sequence_parameters(json.dumps(self.get_sequence()))
	self.analog_sequencer.display_sequence(json.loads(plottable_sequence)) 

    @inlineCallbacks
    def display_sequence(self, sequence):
        conductor = yield self.cxn.get_server(self.conductor_servername)
        plottable_sequence = yield conductor.evaluate_sequence_parameters(json.dumps(sequence))
	self.analog_sequencer.set_sequence(sequence)
        self.analog_sequencer.display_sequence(json.loads(plottable_sequence))
        self.digital_sequencer.display_sequence(sequence)
        self.duration_row.display_sequence(sequence)
        self.add_dlt_row.display_sequence(sequence)
        self.set_sizes()

    def get_sequence(self):
        durations = [b.value() for b in self.duration_row.boxes if not b.isHidden()]
	timing_sequence = {self.timing_channel: durations}
        digital_logic = [c.get_logic() for c in self.digital_sequencer.array.columns if not c.isHidden()]
        digital_sequence = {key: [dl[key] for dl in digital_logic] for key in self.digital_channels}
        analog_sequence = {key: [dict(s.items() + {'dt': dt}.items()) for s, dt in zip(self.analog_sequencer.sequence[key], durations)] for key in self.analog_channels}
        sequence = dict(digital_sequence.items() + analog_sequence.items() + timing_sequence.items())
        return sequence
    
    def add_column(self, i):
        def ac():
            sequence = self.get_sequence()
	    for c in self.channels:
                sequence[c].insert(i, sequence[c][i])
            self.set_sequence(sequence)
        return ac

    def dlt_column(self, i):
        def dc():
            sequence = self.get_sequence()
	    for c in self.channels:
                sequence[c].pop(i)
            self.set_sequence(sequence)
        return dc

    def undo(self):
        self.display_sequence()

    def redo(self):
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

class SequencerConfig(object):
    def __init__(self):
        self.digital_servername = 'yesr20_digital_sequencer'
        self.analog_servername = 'yesr20_analog_sequencer'
	self.conductor_servername = 'yesr20_conductor'
	self.conductor_update_id = 689222
        self.spacer_width = 65
        self.spacer_height = 15
	self.namecolumn_width = 130
	self.namelabel_width = 200
	self.durationrow_height = 20
	self.analog_height = 50
        self.max_columns = 100
        self.digital_colors = ['#ff0000', '#ff7700', '#ffff00', '#00ff00', '#0000ff', '#8a2be2']
	self.ramp_maker = RampMaker

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Sequencer(SequencerConfig(), reactor)
    widget.show()
    reactor.run()
