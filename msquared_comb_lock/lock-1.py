from msquared_comb_lock import MSquaredCombLockServer

if __name__ == '__main__':
    from labrad import util
    server = MSquaredCombLockServer('./config-1.json')
    util.runServer(server)
