from PyQt4 import QtGui, QtCore, Qt
from sequence_parameters_control import ParameterControl

class ControlConfig(object):
    def __init__(self):
        self.servername = 'yesr20_conductor'
        self.update_id = 461028
        self.updateTime = 100 # [ms]
        self.boxWidth = 80
        self.boxHeight = 20
        self.numRows = 1
        self.device = 'Clock AOM'

if __name__ == '__main__':
    import sys
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    config = ControlConfig()
    if len(sys.argv) > 1:
        config.device = sys.argv[1]
    widget = ParameterControl(config, reactor)
    widget.show()
    reactor.run()
