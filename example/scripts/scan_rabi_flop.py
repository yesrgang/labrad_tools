from experiments import *

name = 'scan_rabi_flop'

c_freq = 27.326209e6
shift_freq = 2.3667e3
clock_intensity = -5

c_freq = c_freq-shift_freq
t_start = .001
t_stop = 0.8
n_point = 20

""" should not regularly need to change stuff below here """
times = np.linspace(t_start, t_stop, n_point).tolist()
parameters = {
    'sequence': {
        '*Trabi': times,
        '*Iclk': clock_intensity,
    },
}

scan = Scan(
    name=name,
    parameters=parameters,
)

scan.queue(clear_all=True)
