
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
import ok

class SequencerServer(LabradServer):
    name = 'sequencer'
    mode='idle'

    def __init__(self, config_name):
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()

    def load_configuration(self):
        config = __import__(self.config_name).SequencerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    def initServer(self):
#        self.channels = SequencerConfiguration.channels
        self.initialize_board()

    def initialize_board(self):
        connected = self.connect_board()
        if not connected:
            raise Exception("sequencer board not found")
        self.program_board()

    def connect_board(self):
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "Found {} unused modules".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            iden = tmp.GetDeviceID()
            if iden == self.okDeviceID:
                self.xem = tmp
                print 'Connected to {}'.format(iden)
                self.program_board()
                return True
        return False

    def program_board(self):
        self.xem.LoadDefaultPLLConfiguration() 
        prog = self.xem.ConfigureFPGA(self.bit_file)
        if prog:
            raise "unable to program sequencer"

    def _time_to_ticks(self, time):
        return int(time*self.clk_frequency)
    
    def _program_sequence(self, sequence):
        """ sequence is list of tuples [(duration, {name: logic}), ...] """
        ba = []
        for t, l in sequence:
            #l is a dict
            l2 = [l[d['name']] for k, d in sorted(self.channels.items())]
            ba += list([sum([2**j for j, b in enumerate(l2[i:i+8]) if b]) for i in range(0, 64, 8)])
            ba += list([int(eval(hex(self._time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)])
        ba += [0]*96
        self.set_sequencer_mode('idle')
        self.set_sequencer_mode('load')
        self.xem.WriteToPipeIn(0x80, bytearray(ba))
        self.set_sequencer_mode('idle')

    def set_sequencer_mode(self, mode):
        self.xem.SetWireInValue(0x00, self.sequencer_mode_num[mode])
        self.xem.UpdateWireIns()
        self.seuqencer_mode = mode

    @setting(01, 'get channels', returns='s')
    def get_channels(self, c):
        returnValue(str(self.channels))

    @setting(02, 'run sequence', file_name='s')
    def run_sequence(self, c, file_name):
        infile = open(file_name, 'r')
        sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
        self._program_sequence(sequence)
        self.set_sequencer_mode('run')

    @setting(03, 'sequencer mode', mode='s')
    def _sequencer_mode(self, c, mode=None):
        if mode is not None:
            self.set_sequencer_mode(mode)
        return self.sequencer_mode

    def write_channel_modes(self): 
        cm_list = [d['mode'] for k, d in sorted(self.channels.items())]
        bas = [sum([2**j for j, m in enumerate(cm_list[i:i+16]) if m == 'manual']) for i in range(0, 64, 16)]
        for ba, wire in zip(bas, self.channel_mode_wires):
            self.xem.SetWireInValue(wire, ba)
        self.xem.UpdateWireIns()

    @setting(04, 'channel mode', channel='s', mode='s')
    def channel_mode(self, c, channel, mode=None):
        if mode is not None:
            self.channels[self.name_to_key[channel]]['mode'] = mode
            self.write_channel_modes()
            self.write_channel_stateinvs()
        return self.channels[self.name_to_key[channel]]['mode']
    
    def write_channel_stateinvs(self): 
        cm_list = [d['mode'] for k, d in sorted(self.channels.items())]
        cs_list = [d['manual state'] for k, d in sorted(self.channels.items())]
        ci_list = [d['invert'] for k, d in sorted(self.channels.items())]
        bas = [sum([2**j for j, (m, s, i) in enumerate(zip(cm_list[i:i+16], cs_list[i:i+16], ci_list[i:i+16])) if (m=='manual' and s!=i) or (m=='auto' and i==True)]) for i in range(0, 64, 16)]
        for ba, wire in zip(bas, self.channel_stateinv_wires):
            self.xem.SetWireInValue(wire, ba)
        self.xem.UpdateWireIns()

    @setting(05, 'channel manual state', channel='s', state='i')
    def channel_manual_state(self, c, channel, state):
        if state is not None:
            self.channels[self.name_to_key[channel]]['manual state'] = state
            self.write_channel_stateinvs()
        return self.channels[self.name_to_key[channel]]['manual state']

    @setting(06, 'channel invert', channel='s', invert='i')
    def channel_invert(self, c, channel, invert=None):
        if invert is not None:
            self.channels[self.name_to_key[channel]]['invert'] = invert
            self.write_channel_stateinvs()
        return self.channels[self.name_to_key[channel]]['invert']

if __name__ == "__main__":
    config_name = 'sequencer_config'
    __server__ = SequencerServer(config_name)
    from labrad import util
    util.runServer(__server__)
