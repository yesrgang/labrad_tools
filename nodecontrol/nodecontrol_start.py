import labrad 
import numpy as np
import time
from nodecontrol_config import node_dict

errors = False
try:
    cxn = labrad.connect()
except Exception:
    print 'Please start LabRAD Manager'
else:
    for node in node_dict.keys():
    #make sure all node servers are up
        if not node in cxn.servers: 
            print '{} is not running'.format(node)
        else:
            print '\nWorking on {} \n '.format(node)
            cxn.servers[node].refresh_servers()
        #if node server is up, start all possible servers on it that are not already running
            running_servers = np.array(list(cxn.servers[node].running_servers()))
            for server in node_dict[node]:
                if server in running_servers: 
                    print server + ' is already running'
                else:
                    print 'starting ' + server
                    try:
                        cxn.servers[node].start(server)
                    except Exception as e:
                        print 'ERROR with ' + server, e
print 'DONE'
