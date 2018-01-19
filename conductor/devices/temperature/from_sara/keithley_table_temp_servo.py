import time
from time import strftime
import socket

# COMMUNICATE WITH INSTRUMENT

import labrad
cxn = labrad.connect()
s = cxn.yesr11_socket

s.connect(('192.168.1.2', 1394))

# total channel to scan
channelScan = '101:108'
# thermocoupler
channelString = '101:108'



# CLEAR AND RESET
#s.send('TRAC:CLE\n')

# CONFIGURE
s.send('*RST\n')
s.send("DISP:TEXT:DATA 'SrQ Table'\n")
s.send('DISP:TEXT:STAT ON\n')

time.sleep(1)

s.send('SYST:TIME ' + strftime('%H, %M, %S') + '\n')
s.send('SYST:DATE ' + strftime('%Y, %m, %d') + '\n')
s.send('SYST:TST:TYPE RTCL\n')



s.send('SYST:RES:TYPE1, NORM\n')

# SET CHANNEL MEASUREMENTS
# interlock
s.send('CONF:RES (@' + channelString + ')\n')
s.send("SENS1:FUNC 'RES', (@" + channelString + ")\n")




# SCAN PARAMETERS
s.send('TRAC:TST:FORM ABS\n')
s.send('TRAC:CLE:AUTO ON\n')
s.send('TRAC:POIN 20\n')
s.send('TRAC:FEED SENS\n')
s.send('TRAC:FEED:CONT ALW\n')
#s.send('FORM:ELEM READ, UNIT, CHAN, TST, LIM\n')
s.send('FORM:ELEM READ, CHAN, TST, LIM\n')


#s.send('TRAC:CLE:AUTO ON\n')
#s.send('TRAC:POIN 20\n')
s.send('INIT:CONT OFF\n')
s.send('TRIG:SOUR INT\n')
s.send('TRIG:COUN INF\n')
s.send('SAMP:COUN 45000\n')
#s.send('TRAC:FEED SENS1\n')
#s.send('TRAC:FEED:CONT NEXT')
#s.send('INIT:CONT OFF\n')

##s.send('TRIG:SOUR EXT\n')
#s.send('TRIG:SOUR TIM\n')
#s.send('TRIG:COUN 450000\n')
#s.send('SAMP:COUN 450000\n') 
s.send('ROUT:SCAN (@' + channelScan + ')\n')
s.send('ROUT:SCAN:TSO IMM\n')
s.send('ROUT:SCAN:LSEL INT\n')
#s.send('DISP:TEXT:STAT OFF\n')
#s.send('ROUT:SCAN:TSO HLIM1\n')
#s.send('HLIM1 SCAN:Y\n');

# SET DISPLAY TO NORMAL
s.send('DISP:TEXT:STAT OFF\n')



s.close()
