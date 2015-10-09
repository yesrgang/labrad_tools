class RFControlConfig(object):
    def __init__(self):
        self.servername = 'yesr20_6dds'
        self.name = 'HODT AOM'
        self.update_id = 461100
        
        self.frequency_units = [(6, 'MHz')]
        self.frequency_digits = 4
        self.amplitude_units = [(0, 'arb')]
        self.amplitude_digits = 2
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100


if __name__ == '__main__':
    from PyQt4 import QtGui
    from rf_control3 import CWControl
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    widget = CWControl(RFControlConfig(), reactor)
    widget.show()
    reactor.run()
