from collections import deque

class PID:
    def __init__(self, current_value=0., setpoint=0., sampling_interval=1., overall_gain=1., prop_gain=1., int_gain=1., diff_gain=0., min_max=(float('-inf'),float('inf')), offset=0):
        self.rbuffer = deque([0., 0.], maxlen=2)

        self.current_value = current_value
        self.setpoint      = setpoint

        self.overall_gain  = overall_gain
        self.min_max       = min_max
        self.offset        = offset

        self.sampling_interval = 0.
        self.prop_gain         = 0.
        self.int_gain          = 0.
        self.diff_gain         = 0.

        self.error = 0.

        self.set_params(sampling_interval=sampling_interval,
                        prop_gain=prop_gain,
                        int_gain=int_gain,
                        diff_gain=diff_gain)

    def set_params(self, sampling_interval=False, overall_gain=False, prop_gain=False, int_gain=False, diff_gain=False):
        self.sampling_interval = sampling_interval or self.sampling_interval
        self.prop_gain         = prop_gain         or self.prop_gain
        self.int_gain          = int_gain          or self.int_gain
        self.diff_gain         = diff_gain         or self.diff_gain
        self.overall_gain      = overall_gain      or self.overall_gain

        self.update_filter_coefficients()

    def update_filter_coefficients(self):
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
            'a_2': -1.
        }

    def tick(self, current_value=None):
        if current_value != None:
            self.current_value = current_value

        self.error = self.current_value - self.setpoint

        a_1 = self.filter_coefficients['a_1']
        a_2 = self.filter_coefficients['a_2']
        b_0 = self.filter_coefficients['b_0']
        b_1 = self.filter_coefficients['b_1']
        b_2 = self.filter_coefficients['b_2']

        w = self.rbuffer
        x = self.error

        # bilinear transform of continous PID transfer function
        v = x - a_1*w[-1] - a_2*w[-2]
        y = b_0*v + b_1*w[-1] + b_2*w[-2]
        w.append(v)

        # offset
        y += self.offset

        # clamp
        if y < self.min_max[0]: y = self.min_max[0]
        if y > self.min_max[1]: y = self.min_max[1]

        self.output = y

        return y

    def reset(self):
        for i, _ in enumerate(self.rbuffer): self.rbuffer[i] = 0.

        self.current_value = 0.
        self.output        = 0.
