import time
import labrad
import matplotlib.pyplot as plt

cxn = labrad.connect()
bus10 = cxn.yesr10_gpib_bus
addr = 'USB0::0x1AB1::0x0960::DSA8B175300897'

bus10.address(addr)
bus10.write(':SENS:FREQ:SPAN 20e6')

def meas_beta():
    bus10.write(':SENS:FREQ:CENT 100.96e6')
    time.sleep(.4)
    
    ans = bus10.query(':TRACe:DATA? TRACE1')
    pts = eval('['+ans[12:]+']')
    
    plt.plot(pts)
    plt.show()

def meas_alpha():
    bus10.write(':SENS:FREQ:CENT 1.36226e9')
    time.sleep(.4)
    
    ans = bus10.query(':TRACe:DATA? TRACE1')
    pts = eval('['+ans[12:]+']')
    
    plt.plot(pts)
    plt.show()

def meas():
    bus10.write(':SENS:FREQ:CENT 1.36226e9')
    time.sleep(.4)
    
    ans = bus10.query(':TRACe:DATA? TRACE1')
    ptsa = eval('['+ans[12:]+']')

    bus10.write(':SENS:FREQ:CENT 100.96e6')
    time.sleep(.4)
    
    ans = bus10.query(':TRACe:DATA? TRACE1')
    ptsb = eval('['+ans[12:]+']')

    plt.plot(ptsa)
    plt.plot(ptsb)
    plt.show()
