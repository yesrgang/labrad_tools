import numpy as np

def H(x):
    return 0.5*(np.sign(x-1e-9)+1)

def G(t1, t2):
    return lambda t: H(t2-t) - H(t1-t) 

def lin_ramp(p):
    """
    returns continuous finction defined over ['ti', 'tf'].
    values are determined by connecting 'vi' to 'vf' with a line.
    """
    return lambda t: G(p['ti'], p['tf'])(t)*(p['vi'] + (p['vf']-p['vi'])/(p['tf']-p['ti'])*(t-p['ti']))

def exp_ramp(p):
    """
    returns continuous finction defined over ['ti', 'tf'].
    values are determined by connecting 'vi' to 'vf' with an exponential function.
    v = a*e^{-t/'tau'} + c
    """
    p['a'] = (p['vf']-p['vi'])/(np.exp(p['dt']/p['tau'])-1)
    p['c'] = p['vi'] - p['a']
    v_ideal = lambda t: G(p['ti'], p['tf'])(t)*(p['a']*np.exp((t-p['ti'])/p['tau']) + p['c'])
    t_pts = np.linspace(p['ti'], p['tf']-2e-9, p['pts']+1)
    v_pts = v_ideal(t_pts)
    sseq = [{'type': 'lin', 'ti': ti, 'tf': tf, 'vi': vi, 'vf': vf} 
            for ti, tf, vi, vf in zip(t_pts[:-1], t_pts[1:], v_pts[:-1], v_pts[1:])]
    return lambda t: sum([lin_ramp(ss)(t) for ss in sseq])

class SRamp(object):
    required_parameters = [
        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
        ]
    def __init__(self, p=None):
        self.required_parameters = [
            ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
            ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
            ]

        if p is not None:
            p['vi'] = p['vf']
            self.v = lin_ramp(p)

class LinRamp(object):
    required_parameters = [
        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
        ]
    def __init__(self, p=None):

        if p is not None:
            self.v = lin_ramp(p)

class SLinRamp(object):
    required_parameters = [
        ('vi', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
        ('vf', ([-10, 10], [(0, 'V'), (-3, 'mV')], 3)),
        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
        ]
    def __init__(self, p=None):

        if p is not None:
            self.v = lin_ramp(p)

class ExpRamp(object):
    required_parameters = [
        ('vf', ([-10, 10], [(0, 'V')], 3)),
        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
        ('tau', ([-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')], 1)),
        ('pts', ([1, 10], [(0, 'na')], 0)),
        ]
    def __init__(self, p=None):

        if p is not None:
            self.v = exp_ramp(p)

class SExpRamp(object):
    required_parameters = [
        ('vi', ([-10, 10], [(0, 'V')], 3)),
        ('vf', ([-10, 10], [(0, 'V')], 3)),
        ('dt', ([1e-6, 50], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)), 
        ('tau', ([-1e2, 1e2], [(0, 's'), (-3, 'ms'), (-6, 'us')], 1)),
        ('pts', ([1, 10], [(0, 'na')], 0)),
        ]
    def __init__(self, p=None):

        if p is not None:
            self.v = exp_ramp(p)

class RampMaker(object):
    available_ramps = {
        's': SRamp,
        'lin': LinRamp,
        'slin': SLinRamp,
        'exp': ExpRamp,
        'sexp': SExpRamp,
        }
    def __init__(self, sequence=None):

        if sequence is not None:
            j=0
            for i, s in enumerate(sequence):
                if s['type'] is 'sub':
                    seq = sequence.pop(i+j)['seq']
                    for ss in s['seq']:
                        sequence.insert(i+j, ss)
                        j += 1
    
            if not sequence[0].has_key('vi'):
                sequence[0]['vi'] = 0
            for i in range(1, len(sequence)):
                if not sequence[i].has_key('vi'):
                    sequence[i]['vi'] = sequence[i-1]['vf']
                if not sequence[i].has_key('vf'):
                    sequence[i]['vf'] = sequence[i]['vi']
    
            for i, s in enumerate(sequence):
                s['ti'] = sum([ss['dt'] for ss in sequence[:i]])
                s['tf'] = s['ti'] + s['dt']
            
            self.v = lambda t: sum([self.available_ramps[s['type']](s).v(t) for s in sequence])
            self.sequence = sequence

    def get_plottable(self, scale='real', pts=100):
        T = np.concatenate([np.linspace(s['ti'], s['tf'], pts)[:-1] for s in self.sequence])
        V = self.v(T)
        if scale=='real':
            return T, V
        elif scale=='step':
            T = range(len(self.sequence)*pts)
            return T, V

    def get_continuous(self):
        return self.v
