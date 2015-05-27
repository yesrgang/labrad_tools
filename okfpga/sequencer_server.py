
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from sequencer_configuration import SequencerConfiguration
from sequencer_api import SequencerAPI

class SequencerServer(LabradServer):
    name = 'sequencer'

    @inlineCallbacks
    def initServer(self):
        self.channels = SequencerConfiguration.channels
        self.initialize_board()

    def initialize_board(self):
        connected = self.connect_board()
        if not connected:
            raise Exception("Sequencer not found")
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

    def _program_sequence(self, sequence):
        """ sequence is list of tuples [(duration, [logic]), ...] """
        ba = []
        for t, l in sequence:
            ba += list([sum([2**j for j, b in enumerate(l[i:i+8]) if b]) for i in range(0, 64, 8)])
            ba += list([int(eval(hex(time_to_ticks(t))) >> i & 0xff) for i in range(0, 32, 8)])
        self.set_mode('idle')
        self.set_mode('load')
        self.xem.WriteToPipeIn(ba)
        self.set_mode('idle')

    def set_mode(self, mode):
        if mode == 'idle':
            mode_num = 0
        elif mode == 'load':
            mode_num = 1
        elif mode == 'run':
            mode_num = 2
        self.xem.SetWireInValue(0x00, mode_num)
        
