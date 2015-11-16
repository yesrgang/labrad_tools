"""
super simple scan
"""

def scan(list_, command):
    """
    command can be something like "lambda l: dds.frequency('name', l)"
    """
    t0 = time.time()
    for i, l in enumerate(list_):
        command(l)
        t_tar = t0 +  i*T+.5
        print t_tar - time.time()
        sleep(t_tar - time.time())

