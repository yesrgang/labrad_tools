class ClientConfig(object):
    def __init__(self, name):
        self.name = name
        self.servername = 'rf'
        self.update_id = 461100
        
        self.frequency_display_units = [(6, 'MHz')]
        self.frequency_digits = 2
        self.amplitude_display_units = [(0, 'arb')]
        self.amplitude_digits = 2
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100


if __name__ == '__main__':
    from PyQt4 import QtGui
    a = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    from rf.clients.rf_client import MultipleRFClient
    channels = ['hodt_aom', 'vodt_aom', 'dimple_aom']
    configs = [ClientConfig(channel) for channel in channels]
    widget = MultipleRFClient(configs, reactor)
    widget.show()
    reactor.run()
