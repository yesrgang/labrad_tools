import numpy as np
def ftw(frequency, clk=2.4e9): 
    return hex(int(frequency*2**32/clk))[2:].zfill(8) # 32-bit dac

def check_sum(ins):
    checksum = sum(ins[1:])
    checksum_bin = bin(checksum)[2:].zfill(32)
    checksum_lowestbyte = checksum_bin[-8:]
    return int('0b'+str(checksum_lowestbyte), 0)

def instruction_set(frequency, address):
    ins = [58, address, 5, eval('0x0b')] + [int('0x'+ftw(frequency)[i:i+2], 0) for i in range(0, 8, 2)]
    ins = ins + [check_sum(ins)]
    print [bin(i) for i in ins]
    return [chr(i) for i in ins]

def set_frequency(frequency, address):
    ins = instruction_set(frequency, address)
    print len(ins)
    ser.writelines(ins) 
    #for c in ins: ser.write(c)
    print ser.readline()

import serial
import time
ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
time.sleep(1)
set_frequency(301e6, 0)
#print ser.readline()
