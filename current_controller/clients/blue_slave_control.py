class ControlConfig(object):
    def __init__(self, name):
        self.name = name
        self.servername = 'current_controller'
        self.update_id = 461109
        self.update_time = 100

if __name__ == '__main__':
    import sys
    sys.path.append('../../client_tools')
    from PyQt4 import QtGui
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    from current_control import MultipleCurrentControl
    channels = ['3d', '2d', 'zs']
    configs = [ControlConfig(channel) for channel in channels]
    widget = MultipleCurrentControl(configs, reactor)
    widget.show()
    reactor.run()
