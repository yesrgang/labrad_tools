from devices.ag335xxx.ag335xxx import AG335xxx

class AlphaFM(AG335xxx):
    vxi11_address = '192.168.1.24'
    source = 1

    waveforms = [
        'INT:\\ALPHA.ARB',
        'INT:\\ALPHA_FAST.ARB',
        ]

__device__ = AlphaFM
