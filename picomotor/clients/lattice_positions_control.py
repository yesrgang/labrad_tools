class ControlConfig(object):
    def __init__(self, name):
        self.name = name
        self.servername = 'picomotor'
        self.update_id = 461315

        self.position_range = [-1e5, 1e5]
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 70


if __name__ == '__main__':
    import sys
    sys.path.append('../../client_tools')
    from PyQt4 import QtGui
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    from picomotor_control import MultiplePicoMotorControl
    channels = ['h1h', 'h1v', 'h2h', 'h2v']
    configs = [ControlConfig(channel) for channel in channels]
    widget = MultiplePicoMotorControl(configs, reactor)
    widget.show()
    reactor.run()
