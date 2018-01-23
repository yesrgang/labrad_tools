from devices.ad669_board.ad669_board import AD669Board
from devices.ad669_board.lib.ad669_channel import AD669Channel

class BoardE(AD669Board):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'sr2 dac1'

    autostart = True

    channels = [
        AD669Channel(loc=0, name='Alpha Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=1, name='Beta Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=2, name='X Comp. Coil', mode='auto', manual_output=0.0),
        AD669Channel(loc=3, name='Y Comp. Coil', mode='auto', manual_output=0.0),
        AD669Channel(loc=4, name='Z Comp. Coil', mode='auto', manual_output=0.0),
        AD669Channel(loc=5, name='MOT Coil', mode='auto', manual_output=0.0),
        AD669Channel(loc=6, name='HODT Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=7, name='VODT Intensity', mode='auto', manual_output=0.0),
        ]


__device__ = BoardE
