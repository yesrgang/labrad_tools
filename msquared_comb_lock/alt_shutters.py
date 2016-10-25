import labrad
from time import sleep

cxn = labrad.connect()
s = cxn.sequencer

T = 10
SHUTTER_1 = 'SrQ Comb Shutter'
SHUTTER_2 = 'Sr1 Comb Shutter'

while 1:
    s.channel_manual_output(SHUTTER_1, 1)
    s.channel_manual_output(SHUTTER_2, 0)
    sleep(T)
    s.channel_manual_output(SHUTTER_1, 0)
    s.channel_manual_output(SHUTTER_2, 1)
    sleep(T)
