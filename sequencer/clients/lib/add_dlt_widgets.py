from PyQt4 import QtGui

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
    """ row of '+'/'-' """
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

    def updateParameters(self, parameter_values):
        pass


