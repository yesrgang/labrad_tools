"""
### BEGIN NODE INFO
[info]
name = clock_servo
version = 1.1
description = 
instancename = clock_servo

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

from lib.pid import Dither, DitherPID

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

    @setting(5, 'update pid', config='s')
    def update_pid(self, c, config='{}'):
        config = json.loads(config)
        if config:
            for lock_name, lock_config in config.items():
                self.pid[lock_name].set_parameters(**lock_config)
#        return json.dumps({k: v.__dict__ for k, v in self.pid.items()})


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
            yield eval(parameters['init command'])()
            self.dither[lock_name] = Dither(**parameters['parameters'])
            self.dither_command[lock_name] = parameters['update command']

    @setting(6, 'update dither', config='s')
    def update_dither(self, c, config='{}'):
        config = json.loads(config)
        if config:
            for lock_name, lock_config in config.items():
                self.dither[lock_name].set_parameters(**lock_config)
#        return json.dumps({k: v.__dict__ for k, v in self.dither.items()})

    @setting(3, 'update', signal='s')
    def update(self, c, signal):
        reactor.callLater(5, self.do_update, signal)
    
    @inlineCallbacks
    def do_update(self, signal):
        for lock, side in json.loads(signal).items():
            print 'PID: ', lock, side
            if self.pid.has_key(lock):
                data_dev, data_param = self.pid[lock].data_path
                data = yield eval(self.pid_command[lock])()
                try:
                    value = json.loads(data)[data_dev][data_param]
                    if type(value).__name__ == 'list':
                        value = value[-1]
                    center = self.pid[lock].tick(side, value)
                except KeyError, e:
                    print "waiting for valid data on {}".format(e)
                    center = self.pid[lock].output_offset
                data = {lock: {'frequency': center}}
                yield self.record(data)

    @setting(7, lock='s')
    def get_center(self, c, lock):
        return self.pid[lock].output

    @setting(4, 'advance', signal='s')
    def advance(self, c, signal):
        for lock, side in json.loads(signal).items():
            print 'dither: ', lock, side
            if self.dither.has_key(lock):
                center = self.pid[lock].output
                next_write = self.dither[lock].tick(side, center)
                x = yield eval(self.dither_command[lock])(next_write)

    @inlineCallbacks
    def record(self, data):
        yield self.client.yesr20_conductor.send_data(json.dumps(data))

if __name__ == "__main__":
    from labrad import util
    config_name = 'config'
    server = ClockServoServer(config_name)
    util.runServer(server)
