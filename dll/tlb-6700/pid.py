from collections import deque

class PID(object):
    def __init__(self, **kwargs):
        """ 
        """
        self.current_value = 0. 
        self.setpoint = 0. 
        self.sampling_interval = 1. 
        self.overall_gain = 1. 
        self.prop_gain = 1. 
        self.int_gain = 1. 
        self.diff_gain = 0.
        self.out_range = [float('-inf'), float('inf')]
        self.offset = 0
        self.xbuffer = deque([0., 0., 0.], maxlen=3)
        self.ybuffer = deque([0., 0., 0.], maxlen=3)
        self.error = 0.

        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
        
        G = self.overall_gain
        T = self.sampling_interval
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

    def tick(self, current_value=False):
        if not type(current_value).__name__ == 'bool': 
            self.current_value = current_value
        self.error = self.current_value - self.setpoint

        b_0 = self.filter_coefficients['b_0']
        b_1 = self.filter_coefficients['b_1']
        b_2 = self.filter_coefficients['b_2']
        a_1 = self.filter_coefficients['a_1']
        a_2 = self.filter_coefficients['a_2']

        x = self.error
        x_ = self.xbuffer
        y_ = self.ybuffer
        y  = b_0*x + b_1*x_[-1] + b_2*x_[-2] + a_2*y_[-2]

        # offset
        y += self.offset

        # clamp
        y = sorted([self.out_range[0], y, self.out_range[1]])[1]

        self.output = y

        x_.append(x)
        y_.append(y)
        return y

    def reset(self):
        for x in self.xbuffer:
            x = 0
        for y in self.ybuffer:
            y = 0

        self.current_value = 0.
