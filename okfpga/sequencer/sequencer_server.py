
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from sequencer_configuration import SequencerConfiguration
from sequencer_api import SequencerAPI

class SequencerServer(LabradServer):
    name = 'sequencer'

    def __init__(self, config_name):
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()

    def load_configuration(self):
        config = __inport__(self.config_name).SequencerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
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
                self.programOKBoard()
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
        """ sequence is list of tuples [(duration, [logic]), ...] """
        ba = []
        for t, l in sequence:
            ba += list([sum([2**j for j, b in enumerate(l[i:i+8]) if b]) for i in range(0, 64, 8)])
            ba += list([int(eval(hex(self._time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)])
        self.set_mode('idle')
        self.set_mode('load')
        self.xem.WriteToPipeIn(ba)
        self.set_mode('idle')

    def set_mode(self, mode):
        self.xem.SetWireInValue(0x00, self.mode_num[mode])

    @setting(01, 'get channels', returns='s')
    def get_channels(self, c):
        returnValue(str(self.channels))

    @setting(02, 'run sequence', file_name='s')
    def run_sequence(self, c, file_name):
        infile = open(file_name, 'r')
        sequence = [eval(line.split('\n')[:-1][0]) for line in infile.readlines()]
        self._program_sequence(sequence)

if __name__ == "__main__":
    config_name = 'sequencer_config'
    __server__ = SequencerServer(config_name)
    form labrad import util
    util.runServer(__server__)


        
