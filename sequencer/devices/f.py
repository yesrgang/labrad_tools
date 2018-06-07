from devices.yesr_analog_board.yesr_analog_board import YeSrAnalogBoard
from devices.yesr_analog_board.lib.analog_channel import AnalogChannel

class BoardF(YeSrAnalogBoard):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'srq analog 2'

    autostart = True

    channels = [
        AnalogChannel(loc=0, name='Beta FM', mode='auto', manual_output=0.0),
        AnalogChannel(loc=1, name='813 H1 Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=2, name='813 H2 Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=3, name='813 V Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=4, name='Clock Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=5, name='813H Mixer', mode='manual', manual_output=-2.0),
        AnalogChannel(loc=6, name='813V Mixer', mode='manual', manual_output=-2.0),
        AnalogChannel(loc=7, name='Spin Pol. Intensity', mode='auto', manual_output=0.0),
        ]


__device__ = BoardF
