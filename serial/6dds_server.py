"""
### BEGIN NODE INFO
[info]
name = 6DDS
version = 1.0
description = 
instancename = %LABRADNODE% 6DDS

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from dds_server import DDSServer


config_name = '6dds_config'
if __name__ == "__main__":
    from labrad import util
    util.runServer(DDSServer(config_name))

