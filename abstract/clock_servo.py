"""
### BEGIN NODE INFO
[info]
name = clock_servo
version = 1.0
description = 
instancename = %LABRADNODE%_clock_servo

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock

from pid import Dither, DitherPID

class ClockServoServer(LabradServer):
    def __init__(self, config_name):
        self.dither = {}
        self.pid = {}
        self.command = {}

        self.config_name = config_name
        self.load_configuration()
        LabradServer.__init__(self)

    def load_configuration(self):
        config = __import__(self.config_name).ClockServoConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
    
    @setting(1, 'init servo', parameters='s')
    def init_servo(self, c, parameters=None):
        """ define servo

        parameters = {
            lock_name: {
                "pid_parameters": **parameters
                "dither_parameters": **parameters
                "write_command": command
        }
        """
        for lock_name, lock_parameters in json.loads(parameters).items():
            dither_parameters = lock_parameters['dither_parameters']
            pid_parameters = lock_parameters['pid_parameters']
            command = lock_parameters['command']
            self.dither[lock_name] = Dither(**dither_parameters)
            self.pid[lock_name] = DitherPID(**pid_parameters)
            self.command[lock_name] = command

    @setting(2, 'update', signal='s')
    def update(self, c, signal):
        signal = json.loads(signal)
        returns = {}
        for k, v in signal.items():
            center = self.pid[k].tick(v)
            next_write = self.dither[k].tick(center)
            yield eval(self.command[k])(next_write)
#            print  eval(self.command[k])(next_write)
            yield self.record({k: center})

    def record(self, data):
        print data
#        yield self.client.conductor.send_data(json.dumps(data))

if __name__ == "__main__":
    from labrad import util
    config_name = 'clock_servo_config'
    server = ClockServoServer(config_name)
    util.runServer(server)
