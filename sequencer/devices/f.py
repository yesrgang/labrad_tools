from devices.ad669_board.ad669_board import AD669Board
from devices.ad669_board.lib.ad669_channel import AD669Channel

class BoardF(AD669Board):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'srq analog 2'

    autostart = True

    channels = [
        AD669Channel(loc=0, name='Beta FM', mode='auto', manual_output=0.0),
        AD669Channel(loc=1, name='813 H1 Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=2, name='813 H2 Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=3, name='813 V Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=4, name='Clock Intensity', mode='auto', manual_output=0.0),
        AD669Channel(loc=5, name='813H Mixer', mode='manual', manual_output=-2.0),
        AD669Channel(loc=6, name='813V Mixer', mode='manual', manual_output=-2.0),
        AD669Channel(loc=7, name='Spin Pol. Intensity', mode='auto', manual_output=0.0),
        ]


__device__ = BoardF
