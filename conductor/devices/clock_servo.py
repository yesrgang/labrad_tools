import json
from twisted.internet.defer import inlineCallbacks

center_freq = 27e6
linewidth = 1.
modulation_depth = linewidth/2.

sampling_period = (13. + .8/lock_linewidth)*2.

# 3.5 Hz settings
peak_height = .5
overall_gain =  -1./peak_height
prop_gain = 0
int_gain = 5./sampling_period
intint_gain = .1/sampling_period**2
diff_gain = .0 * sampling_period

def error(DP):
    def rabi(delta):
        T = .8/lock_linewidth
        O0 = 1. / T
        O = np.sqrt(O0**2 + (np.pi * delta)**2)
        return O0**2/O**2 * np.sin(np.pi * O*T/2.)**2
    HWHM = lock_linewidth/2.
    delta_ = np.linspace(-HWHM, HWHM, 1000)
    DP_ = np.array([rabi(delta-HWHM) - rabi(delta+HWHM) for delta in delta_])
    return delta_[np.argmin(abs(DP_ - DP))]

pid_config = {
    "+9/2": {
        "parameters": {
            'output': center_freq,
            'output_offset': center_freq,
            'overall_gain': overall_gain,
            'prop_gain': prop_gain,
            'int_gain': int_gain,
            'intint_gain': intint_gain,
            'diff_gain': diff_gain,
            'sampling_period': sampling_period,
            'data_path': ('gage', 'frac'),
        },
        "update": "lambda self=self: self.client.yesr20_conductor.get_received_data()",
   },
}

dither_config = {
    "+9/2": {
        "parameters": {
            'modulation_depth': modulation_depth,
        },
        "initialize": "lambda self=self: self.client.rf.select_device('clock_steer')",
        "update": "lambda value, self=self: self.client.rf.frequency(value)",
    },
}

pid_config['+9/2']['parameters']['error_function'] = clouddumps(error)

@inlineCallbacks
def initialize_pid(self):
    yield self.cxn.clock_servo.initialize_pid(json.dumps(pid_config, encoding='ISO-8859-1'))

@inlineCallbacks
def update_pid(self, value):
    lock, side = eval(value)
    yield self.cxn.clock_servo.update(json.dumps({lock: side}))

@inlineCallbacks
def initialize_dither(self):
    yield self.cxn.clock_servo.initialize_dither(json.dumps(dither_config))

@inlineCallbacks
def update_dither(self, value):
    lock, side = eval(value)
    yield self.cxn.clock_servo.advance(json.dumps({lock: side}))


config = {
    'clock_servo': {
        'pid': {
            'initialize': initialize_pid,
            'update': update_pid,
            'value': "(None, None)"
        },
        'dither': {
            'initialize': initialize_dither,
            'update': update_dither,
            'value': "(None, None)"
        },
    },
}

s = cxn.clock_servo
s.initialize_pid(json.dumps(pid_config, encoding='ISO-8859-1'))
s.initialize_dither(json.dumps(dither_config))
