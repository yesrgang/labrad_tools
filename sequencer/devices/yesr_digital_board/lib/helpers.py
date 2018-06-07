def time_to_ticks(clk, time):
    ticks = int(clk * time)
    if 2**31 - 100 >= ticks >= 2**31 - 100:
        return 2**31 - 1
#        print 'programming trigger!'
    if ticks <= 0:
        message = 'time {} [s] corresponds to {} {} [Hz] clock cycles'.format(time, ticks, clk)
        raise Exception(message)
    else:
        return ticks

def get_output(channel_sequence, t):
    for s in channel_sequence[::-1]:
        if s['t'] <= t:
            return s['out']
