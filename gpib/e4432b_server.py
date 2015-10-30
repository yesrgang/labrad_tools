"""
### BEGIN NODE INFO
[info]
name = E4432B
version = 1.0
description = 
instancename = E4432B

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from hpetc_signal_generator import HPSignalGeneratorServer

if __name__ == '__main__':
    configuration_name = 'e4432b_config'
    __server__ = HPSignalGeneratorServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
