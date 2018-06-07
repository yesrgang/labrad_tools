import devices.yesr_analog_board.yesr_analog_board
reload(devices.yesr_analog_board.yesr_analog_board)
from devices.yesr_analog_board.yesr_analog_board import YeSrAnalogBoard
from devices.yesr_analog_board.lib.analog_channel import AnalogChannel

class BoardE(YeSrAnalogBoard):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'sr2 dac1'

#    bitfile = 'analog_sequencer-v2b.bit'
    bitfile = 'analog_sequencer.bit'

    autostart = True

    channels = [
        AnalogChannel(loc=0, name='Alpha Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=1, name='Beta Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=2, name='X Comp. Coil', mode='auto', manual_output=0.0),
        AnalogChannel(loc=3, name='Y Comp. Coil', mode='auto', manual_output=0.0),
        AnalogChannel(loc=4, name='Z Comp. Coil', mode='auto', manual_output=0.0),
        AnalogChannel(loc=5, name='MOT Coil', mode='auto', manual_output=0.0),
        AnalogChannel(loc=6, name='HODT Intensity', mode='auto', manual_output=0.0),
        AnalogChannel(loc=7, name='VODT Intensity', mode='auto', manual_output=0.0),
        ]


__device__ = BoardE
