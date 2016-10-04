class ControlConfig(object):
    def __init__(self):
        self.servername = 'ecdl'
        self.name = 'blue_master'
        self.update_id = 461014

        self.piezo_voltage_display_units = [(0, 'V')]
        self.piezo_voltage_digits = 2
        self.diode_current_display_units = [(0, 'mA')]
        self.diode_current_digits = 1
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 80

if __name__ == '__main__':
    import sys
    sys.path.append('../../client_tools')
    from PyQt4 import QtGui
    from ecdl_control import ECDLControl
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = ECDLControl('blue_master_control', reactor)
    widget.show()
    reactor.run()
