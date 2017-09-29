class ClientConfig(object):
    def __init__(self):
        self.servername = 'picomotor'
        self.name = 'h2v_r'
        self.update_id = 461015

        self.position_range = [-1e5, 1e5]
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 70

if __name__ == '__main__':
    import sys
    sys.path.append('../../client_tools')
    from PyQt4 import QtGui
    from picomotor_control import PicoMotorControl
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = PicoMotorControl(ClientConfig(), reactor)
    widget.show()
    reactor.run()
