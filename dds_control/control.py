import numpy as np
def ftw(frequency, clk=200e6): 
    return hex(int(frequency*2**48/clk))[2:].zfill(12) # 48-bit dac

def check_sum(ins):
    checksum = sum(ins[1:])
    checksum_bin = bin(checksum)[2:].zfill(48)
    checksum_lowestbyte = checksum_bin[40:]
    return int('0b'+str(checksum_lowestbyte), 0)
    

def instruction_set(frequency, address):
    ins = [58, address, 7, 2] + [int('0x'+ftw(frequency)[i:i+2], 0) for i in range(0, 12, 2)]
    ins = ins + [check_sum(ins)]
    return [chr(i) for i in ins]

def set_frequency(frequency, address):
    ins = instruction_set(frequency, address)
    #ser.writelines(ins) 
    for c in ins: ser.write(c)

import serial
import time
ser = serial.Serial('/dev/ttyACM0')
time.sleep(.1)
set_frequency(40e6, 0)
