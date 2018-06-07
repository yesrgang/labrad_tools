from devices.yesr_digital_board.yesr_digital_board import YeSrDigitalBoard
from devices.yesr_digital_board.lib.digital_channel import DigitalChannel

class BoardABCD(YeSrDigitalBoard):
    okfpga_server_name = 'yesr20_okfpga'
    okfpga_device_id = 'Sr2 dev.'

    autostart = True

    channels = [
        DigitalChannel(loc=['A', 0], name='3D MOT AOM', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['A', 1], name='3D MOT Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 2], name='HR Abs. AOM', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['A', 3], name='HR Abs. Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 4], name='LR Abs. AOM', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['A', 5], name='LR H Abs. Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 6], name='LR V Abs. Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 7], name='2D MOT Shutter', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['A', 8], name='Zeeman Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 9], name='AH Enable', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 10], name='AH Bottom Enable', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 11], name='V Camera Trig.', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 12], name='H Camera Trig.', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 13], name='LR V Camera Trig.', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 14], name='TTLA14', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['A', 15], name='Gage Trig.', mode='auto', manual_output=False, invert=True),
        
        DigitalChannel(loc=['B', 0], name='Clock Detune', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 1], name='Clock Center/Sweep', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 2], name='Beta Phase', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 3], name='Spin Pol. LC Wave', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 4], name='HODT AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 5], name='VODT AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 6], name='HODT Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 7], name='VODT Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 8], name='MOT V Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 9], name='813 H1 AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 10], name='813 H2 AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 11], name='813 V AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 12], name='M2 Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 13], name='813 H1 Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 14], name='813 H2 Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['B', 15], name='813 V Shutter', mode='auto', manual_output=False, invert=False),
        
        DigitalChannel(loc=['C', 0], name='Broken!C00', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 1], name='RM Gain Switch', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 2], name='STIRAP P Switch', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['C', 3], name='STIRAP P Trigger', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 4], name='STIRAP S Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 5], name='STIRAP S Switch', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 6], name='STIRAP S Trigger', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 7], name='V Clock Switch', mode='manual', manual_output=True, invert=True),
        DigitalChannel(loc=['C', 8], name='Clock Servo Enable', mode='manual', manual_output=True, invert=False),
        DigitalChannel(loc=['C', 9], name='TTLC09', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 10], name='TTLC10', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 11], name='TTLC11', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 12], name='Troubleshoot', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 13], name='SrQ Comb Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 14], name='Sr1 Comb Shutter', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['C', 15], name='ODT Servo Enable', mode='manual', manual_output=True, invert=False),
        
        DigitalChannel(loc=['D', 0], name='Alpha AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 1], name='Alpha Shutter', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['D', 2], name='Beta AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 3], name='Beta Shutter', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['D', 4], name='Spin Pol. AOM', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['D', 5], name='Spin Pol. Shutter', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['D', 6], name='679 AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 7], name='707 AOM', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 8], name='Repump Shutter', mode='auto', manual_output=False, invert=True),
        DigitalChannel(loc=['D', 9], name='RM FM Trigger', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 10], name='TTLD10', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 11], name='TTLD11', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 12], name='TTLD12', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 13], name='TTLD13', mode='auto', manual_output=False, invert=False),
        DigitalChannel(loc=['D', 14], name='AOSense Heater Enable', mode='manual', manual_output=True, invert=False),
        DigitalChannel(loc=['D', 15], name='Trigger', mode='auto', manual_output=False, invert=True),
        ]
        
__device__ = BoardABCD
