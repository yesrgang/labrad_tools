class ClientConfig(object):
    def __init__(self):
        self.servername = 'rf'
        self.name = '679_piezo_mod'
        self.update_id = 464022

        self.update_time = 100

        # widget sizes
        self.spinbox_width = 70

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
