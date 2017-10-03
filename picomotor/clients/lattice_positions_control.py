class ClientConfig(object):
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
    from PyQt4 import QtGui
    a = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    from picomotor.clients.picomotor_client import MultiplePicomotorClient
    mirrors = [('h1h', 'h1v'), ('h2h', 'h2v'), ('h1h_r', 'h1v_r'), ('h2h_r', 'h2v_r')]
    configs = [[ClientConfig(axis) for axis in mirror] for mirror in mirrors]
    widget = MultiplePicomotorClient(configs, reactor)
    widget.show()
    reactor.run()
