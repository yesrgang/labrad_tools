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

class BrowseAndSave(QtGui.QWidget):
    def __init__(self):
        super(BrowseAndSave, self).__init__(None)
        self.populate()

    def populate(self):
        self.location_box = QtGui.QLineEdit()
        self.browse_button = QtGui.QPushButton('Bro&wse')
        self.save_button = QtGui.QPushButton('&Save')
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
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
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)
        height = 0
        for i in range(self.layout.count()):
            height += self.layout.itemAt(i).widget().height()

    def get_logic(self):
        return {n: int(self.sequencer_buttons[n].isChecked()) for n in self.channels.values()}

    def set_logic(self, logic):
        for name, state in logic.items():
            self.sequencer_buttons[name].setChecked(state)

class LogicArray(QtGui.QWidget):
    def __init__(self, channels):
        super(LogicArray, self).__init__(None)
        self.populate()

    def populate(self):
        self.logic_columns = [LogicColumn(channels) for i in range(20)]
        self.layout = QtGui.QHBoxLayout()
        for lc in self.logic_columns:
            self.layout.addWidget(lc)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        height = self.logic_columns[0].height()
        width = self.logic_columns[0].width()*10

class NameBox(QtGui.QLabel):
    def __init__(self, name):
        super(NameBox, self).__init__(None)
        self.setText(name)
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
        self.layout.addWidget(QtGui.QWidget())
        self.setLayout(self.layout)

class DurationRow(QtGui.QWidget):
    def __init__(self):
        super(DurationRow, self).__init__(None)
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.duration_boxes = [SuperSpinBox([500e-9, 10], units) for i in range(20)]
        self.layout = QtGui.QHBoxLayout()
        for db in self.duration_boxes:
            self.layout.addWidget(db)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

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
        self.add_dlt_buttons = [AddDltButton() for i in range(20)]
        self.layout = QtGui.QHBoxLayout()
        for ad in self.add_dlt_buttons:
            self.layout.addWidget(ad)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)


class NameAndLogic(QtGui.QWidget):
    def __init__(self, channels):
        super(NameAndLogic, self).__init__(None)
        self.channels = channels
        self.populate()
        self.connect_widgets()

    def populate(self):
        self.browse_and_save = BrowseAndSave()
        self.duration_row = DurationRow()
        self.name_column = NameColumn(channels)
        self.logic_array = LogicArray(channels)
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
        self.vscroll.setWidget(QtGui.QWidget())
        self.vscroll.setWidgetResizable(True)
        
        self.hscroll = QtGui.QScrollArea()
        self.hscroll.setWidget(QtGui.QWidget())
        self.hscroll.setWidgetResizable(True)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.browse_and_save, 0, 1)
        self.layout.addWidget(self.duration_scroll, 1, 1)
        self.layout.addWidget(self.name_scroll, 2, 0)
        self.layout.addWidget(self.logic_scroll, 2, 1)
        self.layout.addWidget(self.add_dlt_scroll, 3, 1)
        self.layout.addWidget(self.vscroll, 2, 2)
        self.layout.addWidget(self.hscroll, 4, 1)
        self.setLayout(self.layout)
        
        self.duration_scroll.setHorizontalScrollBarPolicy(1)
        self.duration_scroll.setVerticalScrollBarPolicy(1)
        self.duration_scroll.setFrameShape(0)

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
        
        self.vscroll.setHorizontalScrollBarPolicy(1)
        self.vscroll.setVerticalScrollBarPolicy(2)
        self.vscroll.setFrameShape(0)
        
        self.hscroll.setHorizontalScrollBarPolicy(2)
        self.hscroll.setVerticalScrollBarPolicy(1)
        self.hscroll.setFrameShape(0)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.set_sizes()

    def set_sizes(self):
        self.browse_and_save.setFixedSize(10*sbwidth, 40)

        for db in self.duration_row.duration_boxes:
            db.setFixedSize(sbwidth, 20)
        dr_width = sum([db.width() for db in self.duration_row.duration_boxes if not db.isHidden()])
        self.duration_row.setFixedSize(dr_width, 20)
        
        for lc in self.logic_array.logic_columns:
            for b in lc.sequencer_buttons.values():
                b.setFixedSize(sbwidth, sbheight)
            height = sum([lc.layout.itemAt(i).widget().height() for i in range(lc.layout.count()-1)]) # -1 because there is a generic widget in the last spot
            lc.setFixedSize(sbwidth, height)
        la_width = sum([lc.width() for lc in self.logic_array.logic_columns if not lc.isHidden()])
        la_height = self.logic_array.logic_columns[0].height()
        self.logic_array.setFixedSize(la_width, la_height)

        for nb in self.name_column.name_boxes.values():
            nb.setFixedSize(nbwidth, sbheight)
        nc_width = nbwidth
        nc_height = self.logic_array.height()

        for adb in self.add_dlt_row.add_dlt_buttons:
            adb.setFixedSize(sbwidth, 15)
        ad_width = sum([adb.width() for adb in self.add_dlt_row.add_dlt_buttons if not adb.isHidden()])
        self.add_dlt_row.setFixedSize(ad_width, 15)
        
        self.vscroll.widget().setFixedHeight(self.logic_array.height())
        self.vscroll.setFixedWidth(20)
        self.hscroll.widget().setFixedWidth(self.logic_array.width())
        self.hscroll.setFixedHeight(20)
        
        self.duration_scroll.setFixedHeight(25)
        self.add_dlt_scroll.setFixedHeight(15)
        
        self.name_column.setFixedHeight(self.logic_array.height())
        self.name_scroll.setFixedWidth(100)
        
        height = self.duration_scroll.height() + self.logic_array.height() + self.add_dlt_scroll.height() + self.hscroll.height()
        self.setMaximumHeight(1000)

    def connect_widgets(self):
        self.vscroll.verticalScrollBar().valueChanged.connect(self.adjust_for_vscroll)
        self.hscroll.horizontalScrollBar().valueChanged.connect(self.adjust_for_hscroll)

        self.browse_and_save.save_button.clicked.connect(self.save_sequence)
        self.browse_and_save.browse_button.clicked.connect(self.browse)

        for i, adb in enumerate(self.add_dlt_row.add_dlt_buttons):
            adb.add.clicked.connect(self.add_column(i))
            adb.dlt.clicked.connect(self.dlt_column(i))

    def adjust_for_vscroll(self):
        val = self.vscroll.verticalScrollBar().value()
        self.name_scroll.verticalScrollBar().setValue(val)
        self.logic_scroll.verticalScrollBar().setValue(val)

    def adjust_for_hscroll(self):
        val = self.hscroll.horizontalScrollBar().value()
        self.duration_scroll.horizontalScrollBar().setValue(val)
        self.logic_scroll.horizontalScrollBar().setValue(val)
        self.add_dlt_scroll.horizontalScrollBar().setValue(val)

    def get_sequence_info(self):
        infos = [(db.value(), lc.get_logic()) for db, lc in zip(self.duration_row.duration_boxes, self.logic_array.logic_columns) if not lc.isHidden()]
        return infos

    def save_sequence(self):
        infos = [str(info) + '\n' for info in self.get_sequence_info()]
        outfile = open(self.browse_and_save.location_box.text(), 'w')
        outfile.write(''.join(infos))

    def browse(self):
        file_name = QtGui.QFileDialog().getOpenFileName()
        self.browse_and_save.location_box.setText(file_name)
        self.load_sequence(file_name)

    def load_sequence(self, file_name):
        infile = open(file_name, 'r')
        infos = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
        self.set_sequence_info(infos)

    def set_sequence_info(self, infos):
        for db, lc, ad in zip(self.duration_row.duration_boxes, self.logic_array.logic_columns, self.add_dlt_row.add_dlt_buttons)[::-1]:
            db.hide()
            lc.hide()
            ad.hide()
        for info, db, lc, ad in zip(infos, self.duration_row.duration_boxes, self.logic_array.logic_columns, self.add_dlt_row.add_dlt_buttons):
            t, l = info
            db.show()
            lc.show()
            ad.show()
            db.display(t)
            lc.set_logic(l)

        self.set_sizes()

    def add_column(self, i):
        def ar():
            infos = self.get_sequence_info()
            infos.insert(i, infos[i])
            self.set_sequence_info(infos)
        return ar

    def dlt_column(self, i):
        def dr():
            infos = self.get_sequence_info()
            infos.pop(i)
            self.set_sequence_info(infos)
        return dr

channels = {
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
            'B02': 'TTLB02',
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

if __name__ == '__main__':
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = NameAndLogic(channels)
    widget.show()
    reactor.run()
