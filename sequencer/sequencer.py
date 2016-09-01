"""
### BEGIN NODE INFO
[info]
name = sequencer
version = 1.0
description = 
instancename = %LABRADNODE%_sequencer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import json
import numpy as np

from labrad.server import setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceServer

UPDATE_ID = 698032

class SequencerServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'sequencer'

    def id2channel(self, channel_id):
        """
        expect 3 possibilities for channel_id.
        1) name -> return channel with that name
        2) @loc -> return channel at that location
        3) name@loc -> first try name, then location
        """
        channel = None
        try:
            name, loc = channel_id.split('@')
        except:
            name = channel_id
            loc = None

        if name:
            for d in self.devices.values():
                for c in d.channels:
                    if c.name == name:
                        channel = c
        if not channel:
            for d in self.devices.values():
                for c in d.channels:
                    if c.loc == loc:
                        channel = c

        if channel is None:
            message = 'could not find channel based on ID {}.'.format(channel_id)
            raise Exception(message)
        return channel

    @setting(1)
    def get_channels(self, c):
        channels = {c.key: c 
                for d in self.devices.values() 
                for c in d.channels}
        return json.dumps(channels)
    
    @setting(2, sequence='s')
    def run_sequence(self, c, sequence):
        sequence = self._fix_sequence_keys(json.loads(sequence))
        for device in self.devices.values():
            yield device.program_sequence(sequence)
        for device in self.devices.values():
            yield device.start_sequence()
    
    @setting(3, channel_id='s', mode='s')
    def channel_mode(self, c, channel_id, mode=None):
        channel = self.id2channel(channel_id)
        if mode is not None:
            yield channel.set_mode(mode)
        yield self.send_update(c)
        return channel.mode
    
    @setting(4, channel_id='s', state='?')
    def channel_manual_state(self, c, channel_id, state=None):
        channel = self.id2channel(channel_id)
        if state is not None:
            yield channel.set_manual_state(state)
        yield self.send_update(c)
        return channel.manual_state

    @setting(5, sequence='s', returns='s')
    def fix_sequence_keys(self, c, sequence):
        sequence = json.loads(sequence)
        sequence_keyfix =  self._fix_sequence_keys(sequence)
        return json.dumps(sequence)
    
    def _fix_sequence_keys(self, sequence):
        # take sequence name@loc to configuration name@loc
        locs = [key.split('@')[1] for key in sequence.keys()]

        for key in sequence.keys():
            name, loc = key.split('@')
            for d in self.devices.values():
                for c in d.channels:
                    if c.loc == loc:
                        s = sequence.pop(key)
                        sequence.update({c.key: s})
                    elif c.loc not in locs:
                        sequence.update({c.key: [c.manual_state 
                                for dt in sequence[self.timing_channel]]})
        return sequence
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(SequencerServer())
