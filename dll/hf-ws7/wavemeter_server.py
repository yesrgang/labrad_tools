# LabRAD server for the HighFiness wavemeter WS-7 (and other models)

from labrad.server import LabradServer, setting
from labrad.units import nm, THz
from hfwavemeter_binding import HFWavemeterBinding

class WavemeterServer(LabradServer):
    """
    HighFinesse wavemeter LabRAD server
    """
    name = 'Wavemeter'

    def initServer(self):
        binding = HFWavemeterBinding()
        self.binding = binding

    @setting(1, 'get_channel', returns='i')
    def get_channel(self, c):
        """
        Gets the currently active channel of the multiplexer
        """
        channel = self.binding.get_switcher_channel()
        return int(channel);

    @setting(2, 'set_channel', channel='i', returns='b')
    def set_channel(self, c, channel):
        """
        Sets the channel (1-8) of the multiplexer
        """
        try:
            self.binding.set_switcher_channel(channel)
        except Exception, e:
            self.handle_wavemeter_error(e)
            return False

        return True

    @setting(3, 'get_multiplex_mode', returns='b')
    def get_multiplex_mode(self, c):
        """
        Gets whether wavemeter is multiplexed
        """
        multiplexed = (self.binding.get_switcher_mode() == 1)
        return multiplexed

    @setting(4, 'set_multiplex_mode', on='b', returns='b')
    def set_multiplex_mode(self, c, on):
        """
        Sets whether wavemeter is multiplexed
        """
        self.binding.set_switcher_mode(on)
        return True

    @setting(5, 'get_multiplex_used', channel='i', returns='?')
    def get_multiplex_used(self, c, channel):
        """
        Gets whether channel is used by multiplexer

        This setting only has a meaning if in multiplex mode
        """
        try:
            states = self.binding.get_switcher_signal_states(channel)
            return states['use'] == True
        except Exception, e:
            return self.handle_wavemeter_error(e)

    @setting(6, 'set_multiplex_used', channel='i', on='b', returns='b')
    def set_multiplex_used(self, c, channel, on):
        """
        Sets whether channel is used by multiplexer

        This setting only has a meaning if in multiplex mode
        """
        try:
            states = self.binding.get_switcher_signal_states(channel)
            states['use'] = on
            self.binding.set_switcher_signal_states(channel, states)
            return True
        except Exception, e:
            self.handle_wavemeter_error(e)
            return False

    @setting(7, 'get_multiplex_shown', channel='i', returns='?')
    def get_multiplex_shown(self, c, channel):
        """
        Gets whether channel is shown in multiplex mode

        This setting only has a meaning if in multiplex mode
        """
        try:
            states = self.binding.get_switcher_signal_states(channel)
            return states['show'] == True
        except Exception, e:
            return self.handle_wavemeter_error(e)

    @setting(8, 'set_multiplex_shown', channel='i', on='b', returns='b')
    def set_multiplex_shown(self, c, channel, on):
        """
        Sets whether channel is used by multiplexer

        This setting only has a meaning if in multiplex mode
        """
        try:
            states = self.binding.get_switcher_signal_states(channel)
            states['show'] = on
            self.binding.set_switcher_signal_states(channel, states)
            return True
        except Exception, e:
            self.handle_wavemeter_error(e)
            return False

    @setting(9, 'get_frequency', channel='i', returns='?')
    def get_frequency(self, c, channel=-1):
        """
        Gets the frequency of a channel

        This setting tries to guess the active channel unless in multiplex mode
        """
        if (channel == -1):
            channel = self.guess_channel()

        try:
            frequency = self.binding.get_frequency_num(channel)
            return frequency * THz;
        except Exception, e:
            return self.handle_wavemeter_error(e)

    @setting(10, 'get_wavelength', channel='i', returns='?')
    def get_wavelength(self, c, channel=-1):
        """
        Gets the wavelength (vacuum) of a channel

        This setting tries to guess the active channel unless in multiplex mode
        """
        if (channel == -1):
            channel = self.guess_channel()

        try:
            wavelength = self.binding.get_wavelength_num(channel)
            return wavelength * nm;
        except Exception, e:
            return self.handle_wavemeter_error(e)

    def guess_channel(self):
        if (self.get_multiplex_mode({})):
            return 1;
        else:
            return self.get_channel({})

    @staticmethod
    def handle_wavemeter_error(e):
        print '(wavemeter) error: %s' % e
        return None

if __name__ == '__main__':
    from labrad import util

    server = WavemeterServer()
    util.runServer(server)
