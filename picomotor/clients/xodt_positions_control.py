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
    mirrors = [('hodt_x', 'hodt_y'), ('vodt_x', 'vodt_y'), ('trans_x', 'trans_y'), ('image_x', 'image_y')]
    configs = [[ClientConfig(axis) for axis in mirror] for mirror in mirrors]
    widget = MultiplePicomotorClient(configs, reactor)
    widget.show()
    reactor.run()
