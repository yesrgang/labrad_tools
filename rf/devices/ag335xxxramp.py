from ag335xxx import AG335xxx

class AG335xxxRamp(AG335xxx):
    @inlineCallbacks
    def set_ramprate(self, f_start, f_stop):
        ramp_rate = (f_stop-f_stop)/self.t_ramp
        commands = [
            'SOUR{}:FREQ {}'.format(self.source, f_start),
            'SOUR{}:FREQ:STAR {}'.format(self.source, f_start),
            'SOUR{}:FREQ:STOP {}'.format(self.source, f_stop),
            'SOUR{}:SWEEp:TIME {}'.format(self.source, self.t_ramp),
            'SOUR{}:FREQ:MODE SWE'.format(self.source),
            'TRIG{}:SOUR IMM'.format(self.source),
        ]
        for command in commands:
            self.gpib_connection.write(command)

    @inlineCallbacks
    def get_ramprate(self):
        start_command = 'SOUR{}:FREQ:STAR?'.format(self.source)
        stop_command = 'SOUR{}:FREQ:STOP?'.format(self.source)
        T_command = 'SOUR{}:SWEEp:TIME?'.format(self.source)
        f_start = yield self.query(start_command)
        f_stop = yield self.gpib_connection.query(stop_command)
        T_ramp = yield self.gpib_connection.query(T_command)
        ramprate = (float(f_stop) - float(f_start))/float(T_ramp)
        returnValue(ramprate)
