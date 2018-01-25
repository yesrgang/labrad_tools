from devices.ag335xxx.ag335xxx import AG335xxx

class BetaFM(AG335xxx):
    vxi11_address = '192.168.1.24'
    source = 2

    waveforms = [
        'INT:\\BETA.ARB',
        'INT:\\BETA_FAST.ARB',
        ]

__device__ = BetaFM
