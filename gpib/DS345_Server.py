"""
### BEGIN NODE INFO
[info]
name = DS345
version = 1.0
description = 
instancename = %LABRADNODE% DS345

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import types
from srs_signal_generator import SRSSignalGeneratorServer

if __name__ == '__main__':
    configuration_name = 'ds345_config'
    __server__ = SRSSignalGeneratorServer(configuration_name)

    from labrad import util
    util.runServer(__server__)
