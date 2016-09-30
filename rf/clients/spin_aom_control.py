class ControlConfig(object):
    def __init__(self):
        self.servername = 'rf'
        self.name = 'spin_pol_aom'
        self.update_id = 461017

        self.frequency_display_units = [(6, 'MHz')]
        self.frequency_digits = 4 # really digits after decimal
        self.amplitude_display_units = [(0, 'dBm')]
        self.amplitude_digits = 2 # again, digits after decimal
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100


if __name__ == '__main__':
    import sys
    sys.path.append('../')
    from PyQt4 import QtGui
    from rf_control import RFControl
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = RFControl('spin_aom_control', reactor)
    widget.show()
    reactor.run()
