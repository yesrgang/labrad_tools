"""
### BEGIN NODE INFO
[info]
name = Red Master DDS
version = 1.0
description = 
instancename = %LABRADNODE% Red Master DDS

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from dds_server import DDSServer

config_name = 'redmasterdds_config'
__server__ = DDSServer(config_name)

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
