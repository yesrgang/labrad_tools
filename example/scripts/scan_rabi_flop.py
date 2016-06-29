from experiments import *

name = 'scan_rabi_flop'

clock_intensity = -5

t_start = 0.0
t_stop = 0.8
n_points = 20

""" should not regularly need to change stuff below here """
times = np.linspace(t_start, t_stop, n_points).tolist()[1:]
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
