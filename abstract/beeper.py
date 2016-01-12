import winsound
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock

class BeeperServer(LabradServer):
    name = '%LABRADNODE% Beeper'
    
    @setting(2, 'beep', frequency='i: [Hz]', duration='i: [ms]')
    def beep(self, c, frequency=1000, duration=200):
        winsound.Beep(frequency, duration)
    
if __name__ == "__main__":
    __server__ = BeeperServer()
    from labrad import util
    util.runServer(__server__)
