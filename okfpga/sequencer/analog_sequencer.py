from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

import time
import numpy as np
import ok

class SequencerServer(LabradServer):
    name = 'analog sequencer'
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


    def time_to_ticks(self, time):
        return int(time*self.clk_frequency)
    
#    def _voltages_to_ramp_rates(self, times, voltages):
#    vi = np.array([0] + voltages)
#    vf = np.array(voltages + [voltages[-1]])
#    voltage_diffs = vf[:-1] - vi[:-1]
#    ramp_rates = [int(voltage_to_unsigned(v)*2.**int(np.log2(time_to_ticks(t)))/(time_to_ticks(t))) for v, t in zip(voltage_diffs, times)]
#    for i,r in enumerate(ramp_rates):
#        if r > 0:
#            ramp_rates[i] = r +1
#        else:
#            ramp_rates[i] = 2**16 + r 
#    return ramp_rates

    def voltage_to_signed(self, voltage):
        voltage = sorted([-20, voltage, 20])[1]
        return int(voltage/20.*(2**16-1))

    def ramp_rate(self, voltage_diff, time):
        t = self.time_to_ticks(time)
        v = self.voltage_to_signed(voltage_diff)
        signed_ramp_rate = int(v*2.**int(np.log2(t)-1)/t)
        if signed_ramp_rate > 0:
            return signed_ramp_rate
        else:
            return signed_ramp_rate + 2**16

    def _make_sequence(self, sequence):
        """ sequence is list of tuples [(duration, {name: logic}), ...] """
        # remove unnecessary ramps -> get all the ramp rates. if consequtive ramprates are same, combine!!!
        # write necessary ramps in correct order. Q
        ba = []
        for k, d in sorted(self.channels.items()):
            dv = sequence[0][1][d['name']]['v'] 
            if dv == 0:
                t = sequence[0][0]
                n = 0
                while sequence[n+1][1][d['name']]['v'] == sequence[n][1][d['name']]['v']:
                    t += sequence[n+1][0]
                    if n < len(sequence)-2:
                        n += 1
                    else:
                        break
                ba += [int(eval(hex(self.ramp_rate(dv, t))) >> i & 0xff) for i in range(0, 16, 8)]
                ba += [int(eval(hex(self.time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)]
            else:
                t = sequence[0][0]
                ba += [int(eval(hex(self.ramp_rate(dv, t))) >> i & 0xff) for i in range(0, 16, 8)]
                ba += [int(eval(hex(self.time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)]
        for m in range(1, len(sequence)):
            for k, d in sorted(self.channels.items()):
                if float(sequence[m][1][d['name']]['v']) != float(sequence[m-1][1][d['name']]['v']): # we need to change voltage
                    dv = sequence[m][1][d['name']]['v'] - sequence[m-1][1][d['name']]['v']
                    t = sequence[m][0]
                    ba += [int(eval(hex(self.ramp_rate(dv, t))) >> i & 0xff) for i in range(0, 16, 8)]
                    ba += [int(eval(hex(self.time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)]
                elif sequence[m-1][1][d['name']]['v'] != sequence[m-2][1][d['name']]['v']: # we need to keep voltage
                    dv = 0
                    t = 0
                    n = 0
                    while sequence[m+n][1][d['name']]['v'] == sequence[m+n-1][1][d['name']]['v']:
                        t += sequence[m+n][0]
                        if m + n < len(sequence)-1:
                            n += 1
                        else:
                            break
                    ba += [int(eval(hex(self.ramp_rate(dv, t))) >> i & 0xff) for i in range(0, 16, 8)]
                    ba += [int(eval(hex(self.time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)]
        ba += [0]*12
        return ba
    
    def _program_sequence(self, sequence):
        ba = self._make_sequence(sequence)
        self.set_sequencer_mode('idle')
        self.set_sequencer_mode('load')
        self.xem.WriteToPipeIn(0x80, bytearray(ba))
        self.set_sequencer_mode('idle')
    
    def set_sequencer_mode(self, mode):
        self.xem.SetWireInValue(0x00, self.sequencer_mode_num[mode])
        self.xem.UpdateWireIns()
        self.seuqencer_mode = mode

    @setting(01, 'get channels')
    def get_channels(self, c):
        return str({k: d['name'] for k, d in self.channels.items()})

    @setting(07, 'run sequence', sequence='s')
    def run_sequence(self, c, sequence):
        self._program_sequence(sequence)
        self.set_sequencer_mode('run')
    
    @setting(02, 'run sequence from file', file_name='s', returns='s')
    def run_sequence_from_file(self, c, file_name):
        infile = open(file_name, 'r')
        sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
        self._program_sequence(sequence)
        self.set_sequencer_mode('run')
        yield None
        returnValue(file_name)

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
    config_name = 'analog_config'
    __server__ = SequencerServer(config_name)
    from labrad import util
    util.runServer(__server__)
