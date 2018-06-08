from devices.yesr_analog_board.yesr_analog_board import YeSrAnalogBoard
from devices.yesr_analog_board.lib.analog_channel import AnalogChannel

class BoardG(YeSrAnalogBoard):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'srq analog 3'

    autostart = True

    channels = [
        AnalogChannel(loc=0, name='DACG00', mode='auto', manual_output=0.0),
        AnalogChannel(loc=1, name='Clock AOM Phase', mode='auto', manual_output=0.0),
        AnalogChannel(loc=2, name='DACG02', mode='auto', manual_output=0.0),
        AnalogChannel(loc=3, name='813H2 pzt H', mode='auto', manual_output=0.0),
        AnalogChannel(loc=4, name='813H2 pzt V', mode='auto', manual_output=0.0),
        AnalogChannel(loc=5, name='DACG05', mode='auto', manual_output=0.0),
        AnalogChannel(loc=6, name='DACG06', mode='auto', manual_output=0.0),
        AnalogChannel(loc=7, name='DACG07', mode='auto', manual_output=0.0),
        ]

__device__ = BoardG
