"""
### BEGIN NODE INFO
[info]
name = sequencer
version = 1.0
description = 
instancename = sequencer

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
import sys

from labrad.server import setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceServer

UPDATE_ID = 698032
TRIGGER_CHANNEL = 'Trigger@D15'

class SequencerServer(DeviceServer):
    #update = Signal(UPDATE_ID, 'signal: update', 's')
    update = Signal(UPDATE_ID, 'signal: update', 'b')
    name = 'sequencer'
    
    def id2channel(self, channel_id):
        """
        expect 3 possibilities for channel_id.
        1) name -> return channel with that name
        2) @loc -> return channel at that location
        3) name@loc -> first try name, then location
        """
        channel = None
        nameloc = channel_id.split('@') + ['']
        name = nameloc[0]
        loc = nameloc[1]
#        try:
#            name, loc = channel_id.split('@')
#        except:
#            name = channel_id
#            loc = None

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

    @setting(10)
    def get_channels(self, c, channel_id=None):
        channels = {}
        try:
            channel = self.id2channel(channel_id)
            return json.dumps(channel.channel_info(), default=lambda x: None)
        except:
            channels = {ch.key: ch.channel_info()
                    for d in self.devices.values() 
                    for ch in d.channels}
            return json.dumps(channels, default=lambda x: None)
    
    @setting(11, sequence='s')
    def run_sequence(self, c, sequence):
        fixed_sequence = self._fix_sequence_keys(json.loads(sequence))
        for device in self.devices.values():
            yield device.program_sequence(fixed_sequence)
        for device in self.devices.values():
            if device.sequencer_type == 'analog':
                yield device.start_sequence()
        for device in self.devices.values():
            if device.sequencer_type == 'digital':
                yield device.start_sequence()

    @setting(12, channel_id='s', mode='s')
    def channel_mode(self, c, channel_id, mode=None):
        channel = self.id2channel(channel_id)
        if mode is not None:
            yield channel.set_mode(mode)
        yield self.send_update(c)
        returnValue(channel.mode)
    
    @setting(13, channel_id='s', output='?')
    def channel_manual_output(self, c, channel_id, output=None):
        channel = self.id2channel(channel_id)
        if output is not None:
            yield channel.set_manual_output(output)
        yield self.send_update(c)
        returnValue(channel.manual_output)

    @setting(14, sequence='s', returns='s')
    def fix_sequence_keys(self, c, sequence):
        sequence = json.loads(sequence)
        sequence_keyfix = self._fix_sequence_keys(sequence)
        return json.dumps(sequence_keyfix)
    
    @setting(15, sequencer='s', returns='s')
    def sequencer_mode(self, c, sequencer):
        return self.devices[sequencer].mode
    
    def _fix_sequence_keys(self, sequence):
        """ patch sequence after channel name change 
        
        After adding channels, or changing the name of existing channels in the sequencer's configuration,
        the channels in a previously made sequence might not match up with the newly configured channels.
        If a configured channel (name@board_loc) does not have an entry in sequence,
        we insert a new sequence according to 
        1) if name matches any name@board_loc in sequence, use this sequence.
        2) if not (1) but board_loc matches any name@board_loc in sequence, use this sequence.
        3) if neither (1) or (2), sequence is constant, defined by configured channel's manual_output variable.

        should save fixed sequences from sequencer.
        save and load sequences from local directory as remote yedata is slow.
        """
        # sequence might be specified by just names or just board_locs. map to name@board_loc
        sequence = {self.id2channel(key).key: value for key, value in sequence.items()}
        sequence_by_name = {key.split('@')[0]: value for key, value in sequence.items()}
        sequence_by_loc = {key.split('@')[1]: value for key, value in sequence.items()}

        patched_sequence = {}
        for board_name, board in self.devices.items():
            for channel in board.channels:
                if channel.name in sequence_by_name:
                    patched_sequence[channel.key] = sequence_by_name[channel.name]
                elif channel.board_loc in sequence_by_loc:
                    patched_sequence[channel.key] = sequence_by_loc[channel.board_loc]
                else:
                    if channel.channel_type == 'digital':
                        default_sequence = [{'dt': s['dt'], 'out': channel.manual_output}
                            for s in sequence[TRIGGER_CHANNEL]]
                    elif channel.channel_type == 'analog':
                        default_sequence = [{'dt': s['dt'], 'type': 's', 'vf': channel.manual_output}
                            for s in sequence[TRIGGER_CHANNEL]]
                    patched_sequence[channel.key] = default_sequence

        return patched_sequence
    
    @setting(2)
    def send_update(self, c):
        yield self.update(True)
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(SequencerServer())
