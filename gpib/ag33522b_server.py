"""
### BEGIN NODE INFO
[info]
name = 33500
version = 1.0
description = 
instancename = 33500

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from generic_signal_generator import GenericSignalGeneratorServer

if __name__ == '__main__':
    configuration_name = 'ag33522b_config'
    __server__ = GenericSignalGeneratorServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
