from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from client_tools import SuperSpinBox
import numpy as np
import json
import matplotlib
matplotlib.use('Qt4Agg')
import digital_channel_control as dcc

class Spacer(QtGui.QFrame):
    def __init__(self, config):
        super(Spacer, self).__init__(None)
        self.setFixedSize(config.spacer_width, config.spacer_height)
        self.setFrameShape(1)
        self.setLineWidth(0)

class SequencerButton(QtGui.QFrame):
    def __init__(self):
        super(SequencerButton, self).__init__(None)
        self.setFrameShape(2)
        self.setLineWidth(1)
        self.on_color = '#ff69b4'
        self.off_color = '#ffffff'
    
    def setChecked(self, state):
        if state:
            self.setFrameShadow(0x0030)
            self.setStyleSheet('QWidget {background-color: %s}' % self.on_color)
            self.is_checked = True
        else:
            self.setFrameShadow(0x0020)
            self.setStyleSheet('QWidget {background-color: %s}' % self.off_color)
            self.is_checked = False

    def mousePressEvent(self, x):
        if self.is_checked:
            self.setChecked(False)
        else:
            self.setChecked(True)

class DigitalColumn(QtGui.QWidget):
    def __init__(self, channels, config, position):
        super(DigitalColumn, self).__init__(None)
        self.channels = channels
        self.config = config
	self.position = position
        self.populate()

    def populate(self):
        self.buttons = {nl: SequencerButton() for nl in self.channels}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        for i, nl in enumerate(sorted(self.channels, key=lambda nl: nl.split('@')[1])):
            if not i%16 and i != 0:
                self.layout.addWidget(Spacer(self.config))
            self.layout.addWidget(self.buttons[nl])
            self.buttons[nl].on_color = self.config.digital_colors[i%len(self.config.digital_colors)]
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)

    def get_logic(self):
        return {nl: int(self.buttons[nl].is_checked) for nl in self.channels}

    def set_logic(self, sequence):
        print self.position
        for nameloc in self.channels:
            self.buttons[nameloc].setChecked(sequence[nameloc][self.position]['state'])

class DigitalArray(QtGui.QWidget):
    def __init__(self, channels, config):
        super(DigitalArray, self).__init__(None)
        self.channels = channels
        self.config = config
        self.populate()

    def populate(self):
        self.columns = [DigitalColumn(self.channels, self.config, i) for i in range(self.config.max_columns)]
        self.layout = QtGui.QHBoxLayout()
        for lc in self.columns:
            self.layout.addWidget(lc)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def display_sequence(self, sequence): 
        for c in self.columns[::-1]:
            c.hide()
	print len(sequence[self.channels[0]])
	for c in self.columns[:len(sequence[self.channels[0]])]:
            c.show()
            c.set_logic(sequence)

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

class DigitalNameColumn(QtGui.QWidget):
    def __init__(self, channels, config):
        super(DigitalNameColumn, self).__init__(None)
        self.channels = channels
        self.config = config
        self.populate()

    def populate(self):
        self.labels = {nl: NameBox(nl) for nl in self.channels}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 0, 0, 0)
        for i, nl in enumerate(sorted(self.channels, key=lambda nl: nl.split('@')[1])):
            if not i%16 and i != 0:
                self.layout.addWidget(Spacer(self.config))
            self.layout.addWidget(self.labels[nl])
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)

class DigitalSequencer(QtGui.QWidget):
    def __init__(self, channels, config):
        super(DigitalSequencer, self).__init__(None)
        self.channels = channels
        self.config = config
        self.populate()

    def populate(self):
        self.name_column = DigitalNameColumn(self.channels, self.config)
        self.name_column.scroll_area = QtGui.QScrollArea()
        self.name_column.scroll_area.setWidget(self.name_column)
        self.name_column.scroll_area.setWidgetResizable(True)
        self.name_column.scroll_area.setHorizontalScrollBarPolicy(1)
        self.name_column.scroll_area.setVerticalScrollBarPolicy(1)
        self.name_column.scroll_area.setFrameShape(0)

        self.array = DigitalArray(self.channels, self.config)
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
        self.vscrolls = [self.name_column.scroll_area.verticalScrollBar(), self.array.scroll_area.verticalScrollBar(), self.vscroll.verticalScrollBar()]
        for vs in self.vscrolls:
            vs.valueChanged.connect(self.adjust_for_vscroll(vs))

    def adjust_for_vscroll(self, scrolled):
        def afv():
            val = scrolled.value()
            for vs in self.vscrolls:
                vs.setValue(val)
        return afv
