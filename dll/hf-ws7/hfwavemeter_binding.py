from ctypes import WinDLL
from ctypes import byref
from ctypes import c_long, c_double, POINTER

class HFWavemeterBinding:
    def __init__(self, dll_path='C:\\\\Windows\\System32\\wlmdata.dll'):
        self.dll = self.configure_dll(dll_path)

    @staticmethod
    def configure_dll(path):
        dll = WinDLL(path)

        dll.GetChannelsCount.restype   = c_long
        dll.GetChannelsCount.argtypes  = [c_long]

        dll.GetSwitcherChannel.restype  = c_long
        dll.GetSwitcherChannel.argtypes = [c_long]

        dll.SetSwitcherChannel.restype  = c_long
        dll.SetSwitcherChannel.argtypes = [c_long]

        dll.GetSwitcherMode.restype  = c_long
        dll.GetSwitcherMode.argtypes = [c_long]

        dll.SetSwitcherMode.restype  = c_long
        dll.SetSwitcherMode.argtypes = [c_long]

        dll.GetSwitcherSignalStates.restype = c_long
        dll.GetSwitcherSignalStates.argtypes = [c_long, POINTER(c_long), POINTER(c_long)]

        dll.SetSwitcherSignalStates.restype = c_long
        dll.SetSwitcherSignalStates.argtypes = [c_long, c_long, c_long]

        dll.GetFrequencyNum.restype  = c_double
        dll.GetFrequencyNum.argtypes = [c_long, c_double]

        dll.GetWavelengthNum.restype  = c_double
        dll.GetWavelengthNum.argtypes = [c_long, c_double]

        return dll

    def get_channels_count(self):
        return self.dll.GetChannelsCount(0)

    def get_switcher_channel(self):
        return self.dll.GetSwitcherChannel(0)

    def set_switcher_channel(self, num):
        self.assert_channel_num(num)

        self.dll.SetSwitcherChannel(num)
        return True

    def get_switcher_mode(self):
        return self.dll.GetSwitcherMode(0)

    def set_switcher_mode(self, mode):
        if mode > 1: mode = 1
        if mode < 0: mode = 0
        return self.dll.SetSwitcherMode(mode)
        return True

    def get_switcher_signal_states(self, num):
        self.assert_channel_num(num)

        show = c_long(0)
        use = c_long(0)
        self.dll.GetSwitcherSignalStates(num, byref(use), byref(show))

        return {
                 'use':  use.value == 1,
                 'show': show.value == 1
               }

    def set_switcher_signal_states(self, num, states):
        self.assert_channel_num(num)

        use = 1 if states['use'] else 0
        show = 1 if states['show'] else 0
        self.dll.SetSwitcherSignalStates(num, use, show)
        return True

    def get_frequency_num(self, num):
        self.assert_channel_num(num)

        value = self.dll.GetFrequencyNum(num, 0)
        return self.return_or_raise(value)

    def get_wavelength_num(self, num):
        self.assert_channel_num(num)

        value = self.dll.GetWavelengthNum(num, 0)
        return self.return_or_raise(value)

    def assert_channel_num(self, num):
        channel_count = self.get_channels_count()
        if (num < 1 or num > channel_count):
            raise Exception('Wavemeter channel %i does not exist (1-%i).' % (num, channel_count))

    @staticmethod
    def return_or_raise(value):
        if value <= 0:
            if value == 0.0:
                raise Exception('Wavemeter has no signal')
            if value == -3.0:
                raise Exception('Wavemeter is underexposured')
            if value == -4.0:
                raise Exception('Wavemeter is overexposured')
            if value == -5.0:
                raise Exception('Wavemeter application not running')

            raise Exception('Unknown wavemeter error')
        else:
            return value
