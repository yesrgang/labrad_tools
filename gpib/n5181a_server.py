"""
### BEGIN NODE INFO
[info]
name = N5181A
version = 1.0
description = 
instancename = %LABRADNODE% N5181A

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
    configuration_name = 'n5181a_config'
    __server__ = HPSignalGeneratorServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
