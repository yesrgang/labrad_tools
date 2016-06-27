from collections import deque
import numpy as np

class DitherPID(object):
    def __init__(self, **kwargs):
        self.sampling_period = 1. 
        self.overall_gain = 1. 
        self.prop_gain = 1. 
        self.int_gain = 1 
        self.diff_gain = 0.
        self.input_offset = 0.
        self.output_offset = 0.
        self.output = None
        self.output_range = [float('-inf'), float('inf')]

        self.input_buffer = {
            'left': deque([], maxlen=1),
            'right': deque([], maxlen=1),
        }
        self.xbuffer = deque([0., 0., 0.], maxlen=3)
        self.ybuffer = deque([0., 0., 0.], maxlen=3)
        self.error = None

        self.set_parameters(**kwargs)

    def set_parameters(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        G = self.overall_gain
        T = self.sampling_period
        p = G*self.prop_gain
        i = G*self.int_gain
        d = G*self.diff_gain

        self.filter_coefficients = {
            'b_0': p + i*T/2. + d*2./T,
            'b_1': i*T - d*4./T,
            'b_2': i*T/2. - p + d*2./T,
            'a_1': 0.,
            'a_2': 1.
        }

    def tick(self, side, value):
        self.input_buffer[side].append(value)
        if np.product([bool(v) for v in self.input_buffer.values()]):
            self.update_output()
        return self.output

    def update_output(self):
        in_l = self.input_buffer['left'].pop()
        in_r = self.input_buffer['right'].pop()
        print 'in: ', in_l, in_r

        self.error = in_l - in_r - self.input_offset
        print 'err', self.error

        b_0 = self.filter_coefficients['b_0']
        b_1 = self.filter_coefficients['b_1']
        b_2 = self.filter_coefficients['b_2']
        a_1 = self.filter_coefficients['a_1']
        a_2 = self.filter_coefficients['a_2']

        x = self.error
        x_ = self.xbuffer
        y_ = self.ybuffer
        y  = b_0*x + b_1*x_[-1] + b_2*x_[-2] + a_2*y_[-2]
        print 'y', y
        x_.append(x)
        y_.append(y)

        # offset
        y += self.output_offset

        # clamp
        y = sorted([self.output_range[0], y, self.output_range[1]])[1]

        self.output = y

        return y

    def reset(self):
        for x in self.xbuffer:
            x = 0
        for y in self.ybuffer:
            y = 0

        self.input_buffer = {
            'left': deque([], maxlen=1),
            'right': deque([], maxlen=1),
        }

class Dither(object):
    def __init__(self, **kwargs):
        # defaults
        self.modulation_depth = 1.
        self.modulation_sign = {
            'left': -1.,
            'right': 1,
        }

        # non-defaults 
        self.set_parameters(**kwargs)

    def set_parameters(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def tick(self, side, center):
        offset = self.modulation_depth * self.modulation_sign[side]
        self.output = center + offset
        return center + offset
