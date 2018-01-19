from datetime import datetime
import dateutil.tz
import socket
import re
#from influxdb import InfluxDBClient
import os
import numpy as np
import time
import json

# COMMUNICATE WITH INSTRUMENT


import labrad
cxn = labrad.connect()
s = cxn.yesr11_colorado_edu_socket

s.connect(('192.168.1.2', 1394))


filename = 'monitor_8_places_air_temps.txt'
tsleep = 0.1
nsample = 1

#channelToCoil = {101: 'Top AHI',
#                 102: 'Top AHM',
#                 103: 'Top AHO',
#                 104: 'Top Q1',
#                 105: 'Top Q2',
#                 106: 'Top Q3',
#                 107: 'Top Q4',
#                 108: 'Bottom AHI',
#                 109: 'Bottom AHM',
#                 110: 'Bottom AHO',
#                 111: 'Bottom Q1',
#                 112: 'Bottom Q2',Honeywell Microelectronics & Precision Sensors HMC2003
#                 113: 'Bottom Q3',
#                 114: 'Bottom Joule/KelvinQ4',
#                 115: 'Vertical ODT',
#                 116: 'Horizontal ODT',
#                 117: 'monitor',
#                 118: 'voltage_x',
#                 119: 'voltage_y',
#                 120: 'voltage_z',956-32208498
 #                }Honeywell Microelectronics & Precision Sensors HMC2003

def get_temperature(s, channelRead):
    ind = 0
    s.send('TRAC:DATA?\n')
    ans = s.recv(4096)
    #s.close()
    prog = re.compile('(?P<reading>[\w.+]+),(?P<time>[\w:.]+),(?P<date>[\w-]+),(?P<channel>[\d]+),(?P<limits>[\d]+)')
    data = []
    for m in prog.finditer(ans):
        timestamp = datetime.strptime(m.group('date') + ' ' + m.group('time')[0:-3], '%d-%b-%Y %H:%M:%S')
        # Stupid timezones. I have to shift this to match UTC
        tzlocal = dateutil.tz.tzlocal()
        timestamp = timestamp - tzlocal.utcoffset(timestamp)    
        #timestamp.tzinfo = dateutil.tz.tzoffset('MST', -7*60*60)
        mydata = {'reading': float(m.group('reading')),
                'timestamp':   timestamp.strftime('%c'),
                'date': time.strftime('%c'),
                'channel':     int(m.group('channel')),
                'limits':      m.group('limits'),
                'error':       int(m.group('limits') != '0000')}
        data.append(mydata)
#        print mydata['reading']
    for i in range(0, len(data)-1):
        if np.int(data[i]['channel']) == channelRead:
            ind = i
            #print data[i]['channel'], data[i]['temperature']
    return data[ind]



irep = 0
nsave = 0
channel_list = [101, 102, 103, 104, 105, 106, 107, 108]
try:
    while True:
#        print nsave
        current_channel = channel_list[np.mod(nsave, len(channel_list))]
        dout = get_temperature(s, current_channel)
        #print dout
        if dout['channel'] == current_channel:
            print dout['channel'], dout['date'], dout['reading']
            time.sleep(tsleep)

            # export data
            if np.mod(irep, nsample)==0:
                if os.path.isfile(filename):
                    with open(filename, 'r') as infile:
                        cdata = json.load(infile)
                else:
                    cdata = {'reading':[], 'timestamp': [], 'date': [], 'channel': [], 'limits':[], 'error': []}

                cdata['reading'].append(dout['reading'])
                cdata['timestamp'].append(dout['timestamp'])
                cdata['channel'].append(dout['channel'])
                cdata['error'].append(dout['error'])
                cdata['date'].append(dout['date'])

                print 'saving...'
                irep = 0
                nsave = nsave+1

                with open(filename, 'w+') as f:
                    json.dump(cdata,f)
            irep = irep +1

        time.sleep(0.5)
except KeyboardInterrupt:
    print 'interrupted...'
    s.close()

