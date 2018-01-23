from devices.ad669_board.ad669_board import AD669Board
from devices.ad669_board.lib.ad669_channel import AD669Channel

class BoardG(AD669Board):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'srq analog 3'

    autostart = True

    channels = [
        AD669Channel(loc=0, name='DACG00', mode='auto', manual_output=0.0),
        AD669Channel(loc=1, name='Clock AOM Phase', mode='auto', manual_output=0.0),
        AD669Channel(loc=2, name='DACG02', mode='auto', manual_output=0.0),
        AD669Channel(loc=3, name='813H2 pzt H', mode='auto', manual_output=0.0),
        AD669Channel(loc=4, name='813H2 pzt V', mode='auto', manual_output=0.0),
        AD669Channel(loc=5, name='DACG05', mode='auto', manual_output=0.0),
        AD669Channel(loc=6, name='DACG06', mode='auto', manual_output=0.0),
        AD669Channel(loc=7, name='DACG07', mode='auto', manual_output=0.0),
        ]

__device__ = BoardG
