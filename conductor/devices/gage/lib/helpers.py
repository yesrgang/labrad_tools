import json
import numpy as np

DIRECTORY = 'Z:\\SrQ\\gage\\'
FILENAME = 'measurements.json'

def get_measurements():
    with open(DIRECTORY + FILENAME, 'r') as infile:
        measurements = json.load(infile)
    return measurements

#DIRECTORY = 'Z:\\SrQ\\gage\\'
#FILENAME = 'MulRec_CH1-{}.DAT'
#
#measurement_index = {
#    'gnd': 1,
#    'exc': 2,
#    'bac': 3,
#}
#
#def get_measurements():
#    sums = {}
#    for name, i in measurement_index.items():
#        with open(DIRECTORY + FILENAME.format(i), 'r') as infile:
#            counts = [float(v.replace('\n', '')) for v in infile.readlines()[13:]]
#            sums[name] = sum(counts[:50500])
#    bac = sums['bac']
#    gnd = sums['gnd'] - bac
#    exc = sums['exc'] - bac
#    tot = exc + gnd
#    frac = exc / tot
#    return {
#        'bac': bac,
#        'gnd': gnd,
#        'exc': exc,
#        'tot': tot,
#        'frac': frac,
#    }
    
    



