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
import numpy as np

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock

from pid import Dither, DitherPID

class ClockServoServer(LabradServer):
    def __init__(self, config_name):
        self.pid = {}
        self.pid_command = {}
        self.dither = {}
        self.dither_command = {}

        self.config_name = config_name
        self.load_configuration()
        LabradServer.__init__(self)

    def load_configuration(self):
        config = __import__(self.config_name).ClockServoConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
    
    @setting(1, 'init pid', config='s')
    def init_pid(self, c, config=None):
        """ define pid

        config = {
            lock_name: {
                "parameters": **parameters
            }
        }
        """
        for lock_name, parameters in json.loads(config).items():
            self.pid[lock_name] = DitherPID(**parameters['parameters'])
            self.pid_command[lock_name] = parameters['command']

    @setting(2, 'init dither', config='s')
    def init_dither(self, c, config=None):
        """ define dither

        config = {
            lock_name: {
                "parameters": **parameters
                "command": command
            }
        }
        """
        for lock_name, parameters in json.loads(config).items():
            self.dither[lock_name] = Dither(**parameters['parameters'])
            self.dither_command[lock_name] = parameters['command']

    @setting(3, 'update', signal='s')
    def update(self, c, signal):
        for lock, side in json.loads(signal).items():
            if self.pid.has_key(lock):
                data_dev, data_param = self.pid[lock].data_path
                data = eval(self.pid_command[lock])()
                try:
                    value = data[data_dev][data_param]
                    center = self.pid[lock].tick(side, value)
                    yield self.record({lock: center})
                except:
                    print "waiting for valid data"

    @setting(4, 'advance', signal='s')
    def advance(self, c, signal):
        signal = json.loads(signal)
        for lock, side in signal.items():
            if self.dither.has_key(lock):
                center = self.pid[lock].output
                next_write = self.dither[lock].tick(side, center)
#                print eval(self.dither_command[lock])(next_write)

    def record(self, data):
        print 'center', data
#        yield self.client.conductor.send_data(json.dumps(data))

if __name__ == "__main__":
    from labrad import util
    config_name = 'clock_servo_config'
    server = ClockServoServer(config_name)
    util.runServer(server)
