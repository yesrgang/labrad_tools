class RFControlConfig(object):
    def __init__(self):
        self.servername = 'ds345'
        self.name = 'ODT Tickle'
        self.state_id = 461017
        self.frequency_id = 461018
        self.amplitude_id = 461019

        self.frequency_units = [(6, 'MHz'), (3, 'kHz'), (0, 'Hz')]
        self.frequency_digits = 1 # really digits after decimal
        self.amplitude_units = [(0, 'dBm')]
        self.amplitude_digits = 2 # again, digits after decimal
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100


if __name__ == '__main__':
    from PyQt4 import QtGui
    from rf_control2 import CWControl
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = CWControl('odt_tickle_control', reactor)
    widget.show()
    reactor.run()
