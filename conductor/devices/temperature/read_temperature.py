import labrad
import json
from matplotlib import pyplot as plt 
import time

cxn = labrad.connect()
c = cxn.conductor

t_ = []
sch = range(101, 109)
nmax = 100
for i in range(0, nmax):
    tmp = json.loads(cxn.conductor.get_parameter_values())
    pm = tmp['temperature']['keithley_temperature']
    t_.append(pm)
    time.sleep(1)


lst = t_[0].keys()


fig = plt.figure()
[plt.plot([t_[i][x] for i in range(0, len(t_))],'-') for x in lst]
plt.show()



