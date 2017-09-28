class ClientConfig(object):
    def __init__(self):
        self.servername = 'rf'
        self.name = 'alpha'
        self.update_id = 461013

        self.frequency_display_units = [(9, 'GHz')]
        self.frequency_digits = 6
        self.amplitude_display_units = [(0, 'dBm')]
        self.amplitude_digits = 2
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100

if __name__ == '__main__':
    from PyQt4 import QtGui
    from rf.clients.rf_client import RFClient
    a = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    
    widget = RFClient(ClientConfig(), reactor)
    widget.show()
    reactor.run()
