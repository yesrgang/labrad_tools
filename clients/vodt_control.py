

class ControlConfig(object):
    def __init__(self):
        self.name = 'DACE08'
        self.servername = 'yesr20_analog_sequencer_2'
        self.servername_alt = 'yesr20 Analog Sequencer 2'
        self.update_id = 461023
        self.update_time = 100 # [ms]

        self.voltage_units = [(0, 'V')]
        self.voltage_digits = 3
        self.spinbox_width = 80


if __name__ == '__main__':
    from PyQt4 import QtGui, QtCore, Qt
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from analog_voltage_manual_control import AnalogVoltageManualControl
    widget = AnalogVoltageManualControl(ControlConfig(), reactor)
#    widget = ManyChannels(reactor)
    widget.show()
    reactor.run()
