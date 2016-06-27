import json
import time
import numpy as np
import os

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

class LoadSaveRun(QtGui.QWidget):
    def __init__(self):
        super(LoadSaveRun, self).__init__(None)
        self.populate()

    def populate(self):
        self.locationBox = QtGui.QLineEdit()
        self.loadButton = QtGui.QPushButton('Load')
        self.saveButton = QtGui.QPushButton('Save')
        self.runButton = QtGui.QPushButton('Run')
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.addWidget(self.locationBox)
        self.layout.addWidget(self.loadButton)
        self.layout.addWidget(self.saveButton)
        self.layout.addWidget(self.runButton)
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

    def displaySequence(self, sequence):
        shown = sum([1 for b in self.boxes if not b.isHidden()])
        num_to_show = len(sequence[self.config.timing_channel])
        if shown > num_to_show:
            for b in self.boxes[num_to_show:shown][::-1]:
                b.hide()
        elif shown < num_to_show:
            for b in self.boxes[shown:num_to_show]:
                b.show()
        for b, dt in zip(self.boxes[:num_to_show], sequence[self.config.timing_channel]):
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
    
    def displaySequence(self, sequence):
        shown = sum([1 for b in self.buttons if not b.isHidden()])
        num_to_show = len(sequence[self.config.timing_channel])
        if shown > num_to_show:
            for b in self.buttons[num_to_show: shown][::-1]:
                b.hide()
        elif shown < num_to_show:
            for b in self.buttons[shown:num_to_show]:
                b.show()


class Sequencer(QtGui.QWidget):
    def __init__(self, config, reactor=None, cxn=None):
        super(Sequencer, self).__init__(None)
        self.sequence_parameters = {}
        self.config = config
        for key, value in config.__dict__.items():
            setattr(self, key, value)
        self.digital_servername = config.digital_servername
        self.analog_servername = config.analog_servername
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
        dserver = yield self.cxn.get_server(self.digital_servername)
        dc = yield dserver.get_channels()
        self.digital_channels = json.loads(dc)
        yield dserver.signal__update(self.config.digital_update_id)
        yield dserver.addListener(listener=self.update_digital,
            source=None, ID=self.digital_update_id)
        tc = yield dserver.get_timing_channel()
        self.timing_channel = json.loads(tc)
        self.config.timing_channel = json.loads(tc)
        aserver = yield self.cxn.get_server(self.analog_servername)
        ac = yield aserver.get_channels()
        self.analog_channels = json.loads(ac)
        self.channels = self.digital_channels + self.analog_channels + [self.timing_channel]
        conductor = yield self.cxn.get_server(self.conductor_servername)
        yield conductor.signal__parameters_updated(self.config.conductor_update_id)
        yield conductor.addListener(listener=self.update_parameters, 
            source=None, ID=self.conductor_update_id)
        self.populate()
        self.default_sequence = dict(
            [(nameloc, [{'type': 'lin', 'vf': 0, 'dt': 1}]) 
                for nameloc in self.analog_channels]
            + [(nameloc, [0]) for nameloc in self.digital_channels] 
            + [(self.timing_channel, [1])])
        self.setSequence(self.default_sequence)
        yield dserver.notify_listeners()

    def populate(self):
        self.loadSaveRun = LoadSaveRun()

        self.addDltRow = AddDltRow(self.config)
        self.addDltRow.scrollArea = QtGui.QScrollArea()
        self.addDltRow.scrollArea.setWidget(self.addDltRow)
        self.addDltRow.scrollArea.setWidgetResizable(True)
        self.addDltRow.scrollArea.setHorizontalScrollBarPolicy(1)
        self.addDltRow.scrollArea.setVerticalScrollBarPolicy(1)
        self.addDltRow.scrollArea.setFrameShape(0)

        self.durationRow = DurationRow(self.config)
        self.durationRow.scrollArea = QtGui.QScrollArea()
        self.durationRow.scrollArea.setWidget(self.durationRow)
        self.durationRow.scrollArea.setWidgetResizable(True)
        self.durationRow.scrollArea.setHorizontalScrollBarPolicy(1)
        self.durationRow.scrollArea.setVerticalScrollBarPolicy(1)
        self.durationRow.scrollArea.setFrameShape(0)

        self.digitalSequencer = DigitalSequencer(self.digital_channels, self.config)
        self.analogSequencer = AnalogSequencer(self.analog_channels, self.config)

        self.hscrollArray = QtGui.QScrollArea()
        self.hscrollArray.setWidget(QtGui.QWidget())
        self.hscrollArray.setHorizontalScrollBarPolicy(2)
        self.hscrollArray.setVerticalScrollBarPolicy(1)
        self.hscrollArray.setWidgetResizable(True)
        self.hscrollArray.setFrameShape(0)
        
        self.hscrollName = QtGui.QScrollArea()
        self.hscrollName.setWidget(QtGui.QWidget())
        self.hscrollName.setHorizontalScrollBarPolicy(2)
        self.hscrollName.setVerticalScrollBarPolicy(1)
        self.hscrollName.setWidgetResizable(True)
        self.hscrollName.setFrameShape(0)
        
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.digitalSequencer)
        self.splitter.addWidget(self.analogSequencer)

        #spacer widgets
        self.northwest = QtGui.QWidget()
        self.northeast = QtGui.QWidget()
        self.southwest = QtGui.QWidget()
        self.southeast = QtGui.QWidget()

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.northwest, 0, 0, 2, 1)
        self.layout.addWidget(self.loadSaveRun, 0, 1)
        self.layout.addWidget(self.northeast, 0, 2, 2, 1)
        self.layout.addWidget(self.durationRow.scrollArea, 1, 1)
        self.layout.addWidget(self.splitter, 2, 0, 1, 3)
        self.layout.addWidget(self.southwest, 3, 0, 1, 1)
        self.layout.addWidget(self.addDltRow.scrollArea, 3, 1)
        self.layout.addWidget(self.hscrollName, 4, 0)
        self.layout.addWidget(self.hscrollArray, 4, 1)
        self.layout.addWidget(self.southeast, 3, 2, 2, 1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setWindowTitle('sequencer control')

        self.setLayout(self.layout)
        self.setSizes()
        self.connectWidgets()

    def setSizes(self):
        self.northwest.setFixedSize(self.namecolumn_width, self.durationrow_height)
        self.loadSaveRun.setFixedWidth(10*self.spacer_width)
        self.northeast.setFixedSize(20, self.durationrow_height)
        
        for c in self.digitalSequencer.array.columns:
            for b in c.buttons.values():
                b.setFixedSize(self.spacer_width, self.spacer_height)
            # -1 because there is a generic widget in the last spot
            height = sum([c.layout.itemAt(i).widget().height() for i in range(c.layout.count()-1)]) 
            c.setFixedSize(self.spacer_width, height)
        da_width = sum([c.width() for c in self.digitalSequencer.array.columns if not c.isHidden()])
        da_height = self.digitalSequencer.array.columns[0].height()
        self.digitalSequencer.array.setFixedSize(da_width, da_height)

        for nl in self.digitalSequencer.nameColumn.labels.values():
            nl.setFixedHeight(self.spacer_height)
        nc_width = self.namelabel_width
        nc_height = self.digitalSequencer.array.height()
        self.digitalSequencer.nameColumn.setFixedSize(nc_width, nc_height)
        self.digitalSequencer.nameColumn.scrollArea.setFixedWidth(self.namecolumn_width)
        
        self.digitalSequencer.vscroll.widget().setFixedSize(0, self.digitalSequencer.array.height())
        self.digitalSequencer.vscroll.setFixedWidth(20)
        
        width = self.digitalSequencer.array.width()
        height = self.analog_height*len(self.analog_channels)
        self.analogSequencer.array.setFixedSize(width, height)
        self.analogSequencer.vscroll.widget().setFixedSize(0, self.analogSequencer.array.height())
        self.analogSequencer.vscroll.setFixedWidth(20)
        
        for nl in self.analogSequencer.nameColumn.labels.values():
            nl.setFixedSize(self.namelabel_width, self.analog_height)
        nc_width = self.namelabel_width
        nc_height = self.analogSequencer.array.height()
        self.analogSequencer.nameColumn.setFixedSize(nc_width, nc_height)
        self.analogSequencer.nameColumn.scrollArea.setFixedWidth(self.namecolumn_width)
        
        for b in self.durationRow.boxes:
            b.setFixedSize(self.spacer_width, self.durationrow_height)
        dr_width = sum([db.width() for db in self.durationRow.boxes if not db.isHidden()])
        self.durationRow.setFixedSize(dr_width, self.durationrow_height)
        self.durationRow.scrollArea.setFixedHeight(self.durationrow_height)
       
        self.southwest.setFixedSize(self.namecolumn_width, self.durationrow_height)
        self.southeast.setFixedWidth(20)
        
        for b in self.addDltRow.buttons:
            b.setFixedSize(self.spacer_width, 15)
        self.addDltRow.setFixedSize(dr_width, self.durationrow_height)
        self.addDltRow.scrollArea.setFixedHeight(self.durationrow_height)
        
        self.hscrollArray.widget().setFixedSize(self.digitalSequencer.array.width(), 0)
        self.hscrollArray.setFixedHeight(20)
        self.hscrollName.widget().setFixedSize(self.namelabel_width, 0)
        self.hscrollName.setFixedSize(self.namecolumn_width, 20)

    def connectWidgets(self):
        self.hscrollArray.horizontalScrollBar().valueChanged.connect(self.adjustForHScrollArray)
        self.hscrollName.horizontalScrollBar().valueChanged.connect(self.adjustForHScrollName)

        self.loadSaveRun.saveButton.clicked.connect(self.saveSequence)
        self.loadSaveRun.runButton.clicked.connect(self.runSequence)
        self.loadSaveRun.loadButton.clicked.connect(self.browse)

        for i, b in enumerate(self.addDltRow.buttons):
            b.add.clicked.connect(self.addColumn(i))
            b.dlt.clicked.connect(self.dltColumn(i))

        for l in self.digitalSequencer.nameColumn.labels.values():
            #l.clicked.connect(self.openDigitalManual(l.nameloc))
            l.clicked.connect(self.onDigitalNameClick(l.nameloc))

        for l in self.analogSequencer.nameColumn.labels.values():
            l.clicked.connect(self.editAnalogVoltage(l.nameloc))

    def openDigitalManual(self, channel_name):
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

    def onDigitalNameClick(self, channel_name):
        channel_name = str(channel_name)
        @inlineCallbacks
        def odnc():
            if QtGui.qApp.mouseButtons() & QtCore.Qt.RightButton:
                server = yield self.cxn.get_server(self.digital_servername)
                mode = yield server.channel_mode(channel_name)
                if mode == 'manual':
                    yield server.channel_mode(channel_name, 'auto')
                else:
                    yield server.channel_mode(channel_name, 'manual')
            elif QtGui.qApp.mouseButtons() & QtCore.Qt.LeftButton:
                server = yield self.cxn.get_server(self.digital_servername)
                state = yield server.channel_manual_state(channel_name)
                yield server.channel_manual_state(channel_name, not state)
        return odnc

    def editAnalogVoltage(self, channel_name):
        @inlineCallbacks
        def eav():
            ave_args = (channel_name, self.getSequence(), self.rampMaker, self.config, self.reactor, self.cxn)
            ave = AnalogVoltageEditor(*ave_args)
            if ave.exec_():
                sequence = ave.getEditedSequence().copy()
                self.setSequence(sequence)
            conductor = yield self.cxn.get_server(self.conductor_servername)
            yield conductor.removeListener(listener=ave.receive_parameters, ID=ave.config.conductor_update_id)
        return eav

    def adjustForDVScroll(self):
        val = self.digitalVScroll.verticalScrollBar().value()
        self.digitalNameScroll.verticalScrollBar().setValue(val)
        self.digitalScroll.verticalScrollBar().setValue(val)
    
    def adjustForAVScroll(self):
        val = self.analogVScroll.verticalScrollBar().value()
        self.analogNameScroll.verticalScrollBar().setValue(val)
        self.analogArrayScroll.verticalScrollBar().setValue(val)

    def adjustForHScrollArray(self):
        val = self.hscrollArray.horizontalScrollBar().value()
        self.durationRow.scrollArea.horizontalScrollBar().setValue(val)
        self.digitalSequencer.array.scrollArea.horizontalScrollBar().setValue(val)
        self.analogSequencer.array.scrollArea.horizontalScrollBar().setValue(val)
        self.addDltRow.scrollArea.horizontalScrollBar().setValue(val)
    
    def adjustForHScrollName(self):
        val = self.hscrollName.horizontalScrollBar().value()
        self.digitalSequencer.nameColumn.scrollArea.horizontalScrollBar().setValue(val)
        self.analogSequencer.nameColumn.scrollArea.horizontalScrollBar().setValue(val)
    
    def browse(self):
        if os.path.exists(self.sequence_directory()):
            directory = self.sequence_directory()
        else:
            directory = self.base_directory
        filepath = QtGui.QFileDialog().getOpenFileName(directory=directory)
        if filepath:
            self.loadSaveRun.locationBox.setText(filepath)
            self.loadSequence(filepath)
    
    def saveSequence(self):
        filename = self.loadSaveRun.locationBox.text().split('/')[-1]
        filepath = self.sequence_directory() + filename
        if not os.path.exists(self.sequence_directory()):
            os.makedirs(self.sequence_directory())
        with open(filepath, 'w+') as outfile:
            sequence = self.getSequence()
            json.dump(sequence, outfile)

    @inlineCallbacks
    def runSequence(self, c):
        self.saveSequence()
        sequence = json.dumps(self.getSequence())
        conductor = yield self.cxn.get_server(self.conductor_servername)
        yield conductor.set_sequence(sequence)
    
    @inlineCallbacks
    def loadSequence(self, filepath):
        with open(filepath, 'r') as infile:
            sequence = json.load(infile)
        if sequence.has_key('sequence'):
            sequence = sequence['sequence']
            filepath = self.sequence_directory() + filepath.split('/')[-1].split('#')[0]
        conductor = yield self.cxn.get_server(self.conductor_servername)
        sequence = yield conductor.fix_sequence_keys(json.dumps(sequence))
        self.setSequence(json.loads(sequence))
        self.loadSaveRun.locationBox.setText(filepath)

    def setSequence(self, sequence):
        self.analogSequencer.setSequence(sequence)
        self.displaySequence(sequence)

    @inlineCallbacks
    def get_sequence_paramaters(self):
        conductor = yield self.cxn.get_server(self.conductor_servername)
        sp = yield conductor.set_sequence_parameters()
        self.sequence_parameters = json.loads(sp)

    @inlineCallbacks
    def update_parameters(self, c, signal):
        conductor = yield self.cxn.get_server(self.conductor_servername)
        plottable_sequence = yield conductor.evaluate_sequence_parameters(json.dumps(self.getSequence()))
        self.analogSequencer.displaySequence(json.loads(plottable_sequence)) 
    
    def update_digital(self, c, signal):
        signal = json.loads(signal)
        for l in self.digitalSequencer.nameColumn.labels.values():
            l.displayModeState(signal[l.nameloc])

    @inlineCallbacks
    def displaySequence(self, sequence):
        conductor = yield self.cxn.get_server(self.conductor_servername)
        plottable_sequence = yield conductor.evaluate_sequence_parameters(json.dumps(sequence))
        self.analogSequencer.displaySequence(json.loads(plottable_sequence))
        self.digitalSequencer.displaySequence(sequence)
        self.durationRow.displaySequence(sequence)
        self.addDltRow.displaySequence(sequence)
        self.setSizes()

    def getSequence(self):
        durations = [b.value() for b in self.durationRow.boxes 
                if not b.isHidden()]
        timing_sequence = {self.timing_channel: durations}
        digital_logic = [c.getLogic() 
                for c in self.digitalSequencer.array.columns 
                if not c.isHidden()]
        digital_sequence = {key: [dl[key] 
                for dl in digital_logic] 
                for key in self.digital_channels}
        analog_sequence = {key: [dict(s.items() + {'dt': dt}.items()) 
                for s, dt in zip(self.analogSequencer.sequence[key], durations)]
                for key in self.analog_channels}
        sequence = dict(digital_sequence.items() 
                        + analog_sequence.items() 
                        + timing_sequence.items())
        return sequence
    
    def addColumn(self, i):
        def ac():
            sequence = self.getSequence()
	    for c in self.channels:
                sequence[c].insert(i, sequence[c][i])
            self.setSequence(sequence)
        return ac

    def dltColumn(self, i):
        def dc():
            sequence = self.getSequence()
	    for c in self.channels:
                sequence[c].pop(i)
            self.setSequence(sequence)
        return dc

    def undo(self):
        self.displaySequence()

    def redo(self):
        self.displaySequence()

    def keyPressEvent(self, c):
        super(Sequencer, self).keyPressEvent(c)
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if c.key() == QtCore.Qt.Key_Z:
                self.undo()
            if c.key() == QtCore.Qt.Key_R:
                self.redo()
            if c.key() == QtCore.Qt.Key_S:
                self.saveSequence()
            if c.key() == QtCore.Qt.Key_Return:
                self.runSequence(c)
            if c.key() in [QtCore.Qt.Key_Q, QtCore.Qt.Key_W]:
                self.reactor.stop()
            if c.key() == QtCore.Qt.Key_B:
                self.browse()

    def closeEvent(self, x):
        self.reactor.stop()

class SequencerConfig(object):
    def __init__(self):
        self.digital_servername = 'yesr20_digital_sequencer'
        self.analog_servername = 'yesr20_analog_sequencer'
        self.conductor_servername = 'yesr20_conductor'
        self.base_directory = 'Z:\\SrQ\\data\\'
        self.sequence_directory = lambda: self.base_directory + '{}\\sequences\\'.format(time.strftime('%Y%m%d'))
        self.conductor_update_id = 689222
        self.digital_update_id = 689223
        self.spacer_width = 65
        self.spacer_height = 15
        self.namecolumn_width = 130
        self.namelabel_width = 200
        self.durationrow_height = 20
        self.analog_height = 50
        self.max_columns = 100
        self.digital_colors = ['#ff0000', '#ff7700', '#ffff00', '#00ff00', '#0000ff', '#8a2be2']
        self.rampMaker = RampMaker

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Sequencer(SequencerConfig(), reactor)
    widget.show()
    reactor.run()
