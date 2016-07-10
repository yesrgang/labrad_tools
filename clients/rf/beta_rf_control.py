class ControlConfig(object):
    def __init__(self):
        self.servername = 'gpib_signal_generator'
        self.name = 'beta'
        self.update_id = 461014

        self.frequency_display_units = [(6, 'MHz')]
        self.frequency_digits = 3
        self.amplitude_display_units = [(0, 'dBm')]
        self.amplitude_digits = 2
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100

if __name__ == '__main__':
    from PyQt4 import QtGui
    from rf_control import RFControl
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = RFControl('beta_rf_control', reactor)
    widget.show()
    reactor.run()
