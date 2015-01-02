from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui,QtCore

class sequenceButton(QtGui.QWidget):
    def __init__(self, channel_index, time_index, initial_value, parent=None):
        #QtGui.QWidget.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        self.channel_index = channel_index
        self.time_index = time_index
        # construct layout
        button = QtGui.QPushButton()
        button.setFlat(0)

class sequencerClient(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(sequencerClient, self).__init__(parent)
        self.hwconf = {}
        self.reactor = reactor
        self.initializeLayout()
        self.connect()

    def initializeLayout(self):
        self.setWindowTitle('Sequencer')
        self.layout = QtGui.QGridLayout()
        self.manager_layout = QtGui.QHBoxLayout()
        self.grid_layout = QtGui.QGridLayout()
        self.grid_layout.setSpacing(0)
        print self.grid_layout.spacing()
        self.sequence_location_box=QtGui.QLineEdit()
        self.browse = QtGui.QPushButton('Browse')
        self.load = QtGui.QPushButton('Run')
        self.manager_layout.addWidget(self.sequence_location_box)
        self.manager_layout.addWidget(self.browse)
        self.manager_layout.addWidget(self.load)
        self.layout.addLayout(self.manager_layout, 0, 0)
        self.layout.addLayout(self.grid_layout, 1, 0)
        self.setLayout(self.layout)

    def setSequenceGrid(self, initial_states):
        #hardware configuration
        hwconf_text = open('hardware_configuration.txt').read().split('\n')
        for line in hwconf_text:
            if line != '': 
                items = line.split(',')
                self.hwconf[items[0]] = items[1:2]

        #define widgets
        self.sequence_buttons = [{k: QtGui.QPushButton() for k in self.hwconf.keys()} for i in range(len(self.times))]
        self.time_boxes = [QtGui.QLineEdit(str(self.times[i])) for i in range(len(self.times))]
        self.addrow_buttons = [QtGui.QPushButton('Add') for i in range(len(self.times))]
        self.delrow_buttons = [QtGui.QPushButton('Del') for i in range(len(self.times))]

        #add Widgets
        for i in range(len(self.times)):
            self.grid_layout.addWidget(self.time_boxes[i], 0, i+1)
            self.grid_layout.addWidget(self.addrow_buttons[i], len(self.hwconf.keys())+3, i+1)
            self.grid_layout.addWidget(self.delrow_buttons[i], len(self.hwconf.keys())+4, i+1)
            self.addrow_buttons[i].setCheckable(1)
            self.addrow_buttons[i].setMaximumWidth(55)
            self.delrow_buttons[i].setCheckable(1)
            self.delrow_buttons[i].setMaximumWidth(55)
        for i, k in enumerate(self.hwconf.keys()):
            self.grid_layout.addWidget(QtGui.QLabel(k +': ' + self.hwconf[k][0]), i+1, 0)
            for j, t in enumerate(self.times):
                self.grid_layout.addWidget(self.sequence_buttons[j][k], i+1, j+1)
                self.sequence_buttons[j][k].setCheckable(1)
                self.sequence_buttons[j][k].setChecked(int(initial_states[j][k]))
        self.spacer = QtGui.QLabel()
        self.spacer.setMaximumHeight(10)
        self.grid_layout.addWidget(self.spacer, len(self.hwconf.keys())+2, 0)
        
        #formating
        for i in range(1, self.grid_layout.columnCount()):
            self.grid_layout.setColumnMinimumWidth(i, 55)

        # connections
        for i in range(len(self.times)):
            self.addrow_buttons[i].released.connect(self.on_addRow)
        for i in range(len(self.times)):
            self.delrow_buttons[i].released.connect(self.on_delRow)
        self.grid_layout.update()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.errors import Error
        self.Error = Error
        cxn = yield connectAsync(host='128.138.107.82', name='Sequencer Client')
        self.registry = cxn.registry
        self.load.pressed.connect(self.on_load)
        self.browse.pressed.connect(self.on_browse)

    @inlineCallbacks
    def on_load(self):
        self.times = [float(t.text()) for t in self.time_boxes]
        self.sequence = [{k: self.sequence_buttons[i][k].isChecked() for k in self.hwconf.keys()} for i in range(len(self.times))]
        yield None
    
    @inlineCallbacks
    def on_browse(self): 
        try: self.saveSequence()
        except: pass
        file_name = QtGui.QFileDialog().getOpenFileName()
        self.sequence_location_box.setText(file_name)
        if self.grid_layout.count() != len(self.hwconf.keys()): yield self.removeWidgets()
        yield self.setSequence(file_name)

    def on_addRow(self):
        for i in range(len(self.times)):
            if self.addrow_buttons[i].isChecked(): row = i+1
        self.time_boxes.insert(row, QtGui.QLineEdit('1.0'))
        self.sequence_buttons.insert(row, {k: QtGui.QPushButton() for k in self.hwconf.keys()})
        for k in self.hwconf.keys():
            self.sequence_buttons[row][k].setCheckable(1)
        self.saveSequence()
        self.removeWidgets()
        self.setSequence(self.sequence_location_box.text())

    def on_delRow(self):
        for i in range(len(self.times)):
            if self.delrow_buttons[i].isChecked(): row = i
        self.time_boxes.pop(row)
        self.sequence_buttons.pop(row)
        self.saveSequence()
        self.removeWidgets()
        self.setSequence(self.sequence_location_box.text())

    @inlineCallbacks
    def removeWidgets(self):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(w)
            w.close()
        yield None

    @inlineCallbacks
    def setSequence(self, file_name):
        sequence_text = open(file_name).read().split('\n')[:-1]
        self.times = [float(t) for t in sequence_text[0].split(',')]
        initial_states = [{line.split(', ')[0]: line.split(', ')[i+1] for line in sequence_text[1:]} for i in range(len(self.times))]
        yield self.setSequenceGrid(initial_states)

    def saveSequence(self):
        f = open(self.sequence_location_box.text(), 'w')
        self.times = [float(t.text()) for t in self.time_boxes]
        write_str = str(self.times)[1:-1] + '\n'
        for k in self.hwconf.keys():
            write_str += k+', '+str([int(self.sequence_buttons[i][k].isChecked()) for i in range(len(self.times))])[1:-1]+'\n'
        f.write(write_str)

    def closeEvent(self, x):
        self.saveSequence()
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = sequencerClient(reactor)
    widget.show()
    reactor.run()
