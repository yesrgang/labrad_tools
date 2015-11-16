"""
super simple scan
"""
import numpy as np
import labrad
import time

def T_from_sequence(sequence_filename):
    infile = open(sequence_filename, 'r')
    sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
    return sum([T for (T, seq) in sequence])

def scan(T, list_, command):
    """
    command can be something like "lambda l: dds.frequency('name', l)"
    """
    t0 = time.time()
    for i, l in enumerate(list_):
        command(float(l))
        t_tar = t0 +  i*T+.5
        print t_tar - time.time()
        time.sleep(t_tar - time.time())

cxn = labrad.connect()
dds = cxn.DS345
dds.select_device_by_name('ODT Tickle')
sequence_filename = 'C:\Users\Ye Lab\Desktop\labrad\clients\sequencer_control\\20151116\loatodt_abs-swgain'
T = T_from_sequence(sequence_filename)
list_ = np.arange(50, 400, 5)
command = lambda l: dds.frequency(l)

scan(T, list_, command)


