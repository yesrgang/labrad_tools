class ControlConfig(object):
    def __init__(self, name):
        self.name = name
        self.servername = 'rf'
        self.update_id = 461100
        
        self.frequency_display_units = [(6, 'MHz')]
        self.frequency_digits = 4
        self.amplitude_display_units = [(0, 'arb')]
        self.amplitude_digits = 2
        self.update_time = 100

        # widget sizes
        self.spinbox_width = 100


if __name__ == '__main__':
    import sys
    sys.path.append('../')
    from PyQt4 import QtGui
    a = QtGui.QApplication([])
    import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    from rf_control import MultipleRFControl
    channels = ['hodt_aom', 'vodt_aom', 'dimple_aom']
    configs = [ControlConfig(channel) for channel in channels]
    widget = MultipleRFControl(configs, reactor)
    widget.show()
    reactor.run()
