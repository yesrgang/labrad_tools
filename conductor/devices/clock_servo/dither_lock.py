import json
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

import lib.pid
reload(lib.pid)
from lib.pid import Dither, DitherPIID, DitherPID

class DitherLock(ConductorParameter):
    priority = 9

    def __init__(self, config):
        super(DitherLock, self).__init__(config)
        #self.pid = {lock_name: DitherPIID(**lock_conf['pid']) 
        self.pid = {lock_name: DitherPID(**lock_conf['pid']) 
            for lock_name, lock_conf in config.items()}
        self.dither = {lock_name: Dither(**lock_conf['dither']) 
            for lock_name, lock_conf in config.items()}
        self._value = {}

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.pmt.select_device('blue_pmt')
#        yield self.cxn.yesr10_andor.select_device('ikon')

    @inlineCallbacks
    def update(self):
        """ sefl.value == {
            'dither': [dither_name, side],
            'pid': [pid_name, side],
        }
        """
        current_value = self.value.copy()
        pid_value = current_value.get('pid')
        if pid_value:
            name = pid_value[0]
            side = pid_value[1]
            readout_type = self.pid[name].readout_type
            if readout_type == 'pmt':
                try:
                    # this line is important. check. make sure experiment is at least
                    # two cycles old before we start feeding back
                    #frac = self.conductor.data['pico']['fit_frac'][-2]
                    #tot = self.conductor.data['pico']['fit_tot'][-2]

#                    frac = self.conductor.data['pico']['fit_frac'][-1]
#                    tot = self.conductor.data['pico']['fit_tot'][-1]
                    i_retrive = -2
                    pmt_data_json = yield self.cxn.pmt.retrive(i_retrive)
                    print i_retrive
                    pmt_data = json.loads(pmt_data_json)
                    frac = pmt_data['frac_fit']
                    tot = pmt_data['tot_fit']

                    print 'pid: ', name, side
                    print 'frac: ', frac
                except Exception as e:
                    print e
                    frac = None
                except Exception as e:
                    print e
                    print 'error getting frac from camera'
                    frac = None
            
            if frac:
                if tot > self.pid[name].tot_cutoff:
                    out = self.pid[name].tick(side, frac)
                    yield self.conductor.set_parameter_value(name, 'frequency', out, True)
                    print 1
                else:
                    out = self.pid[name].output
                    yield self.conductor.set_parameter_value(name, 'frequency', out, True)
                    print 2
            else:
                out = self.pid[name].output
                yield self.conductor.set_parameter_value(name, 'frequency', out, True)
                print 3
        
        dither_value = current_value.get('dither')
        if dither_value:
            name = dither_value[0]
            side = dither_value[1]

            center = self.pid[name].output
            out = self.dither[name].tick(side, center)

#            yield self.conductor.set_parameter_value('clock_aom', 'center_frequency', center)
#            yield self.conductor.set_parameter_value('clock_aom', 'frequency', out)
            
            aom_center = 177.77e6 - center
            aom_out = 177.77e6 - out
            yield self.conductor.set_parameter_value('clock_aom', 'center_frequency', aom_center)
            yield self.conductor.set_parameter_value('clock_aom', 'frequency', aom_out)
            yield self.conductor.set_parameter_value('clock_aom', 'hr_frequency', aom_out)
            yield self.conductor.set_parameter_value('clock_fiber_aom', 'center_demod_frequency', center)
            yield self.conductor.set_parameter_value('clock_fiber_aom', 'demod_frequency', out)
            yield self.conductor.set_parameter_value('clock_fiber_aom', 'hr_demod_frequency', out)

