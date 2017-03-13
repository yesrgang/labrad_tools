"""
### BEGIN NODE INFO
[info]
name = msquared_comb_lock
version = 1.0
description = 
instancename = msquared_comb_lock

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet import task, defer, reactor
import os
import json
import numpy as np
from lib.pid import PID
from lib.detect_peaks import detect_peaks
import sys
from datetime import datetime
from time import time

class MSquaredCombLockServer(LabradServer):
    """
    Comb lock LabRAD server for the M-squared laser
    """
    name = 'msquared_comb_lock'

    def __init__(self, config_path='./config.json'):
        self.config = self.load_config(config_path)
        self.is_locked = False
        self.lock_status = False
        self.log_path = None

        pid_config = self.config['pid']
        self.pid = PID(overall_gain=pid_config['overall_gain'],
                  prop_gain=pid_config['prop_gain'],
                  int_gain=pid_config['int_gain'],
                  diff_gain=pid_config['diff_gain'],
                  min_max=pid_config['range'],
                  offset=pid_config['offset'])

        sa_config = self.config['spectrum_analyzer']
        self.peak_threshold = sa_config['threshold']
        self.capture_range = sa_config['capture_range']
        self.lock_span = sa_config['lock_span']

        self.name = '{}_comb_lock'.format(self.config['lock_name'])
        LabradServer.__init__(self)
    
    @defer.inlineCallbacks
    def initServer(self):
        yield self.client.spectrum_analyzer.select_device(self.config['spectrum_analyzer_name'])
        yield self.client.msquared.select_device(self.config['msquared_name'])
        self.feedbackTask = task.LoopingCall(self.feedback)
        self.feedbackTask.start(2.5)

    def stopServer(self):
        self.feedbackTask.stop()

    @defer.inlineCallbacks
    def feedback(self):
        if not self.is_locked:
            return
        shutter_open = yield self.client.sequencer.channel_manual_output(self.config['shutter_name'])
        if not shutter_open:
            return

        trace = yield self.spectrum_analyzer.trace()
        trace = np.array(trace)

        position = np.where(trace == np.max(trace))[0][0]
        setpoint = self.pid.setpoint*1e6
        frequency = setpoint + (  float(position-len(trace)/2) * ( self.lock_span / len(trace) )  )

#        has_good_snr = (np.max(trace) - np.min(trace)) > self.peak_threshold
        has_good_snr = (np.max(trace) - np.mean(trace)) > self.peak_threshold
        if not has_good_snr:
            self.lock_status = False
            print 'Feedback disabled due to bad signal'
            return
        
        shutter_open = yield self.client.sequencer.channel_manual_output(self.config['shutter_name'])
        if not shutter_open:
            return

        self.lock_status = True
        feedback = self.pid.tick(frequency/1e6)

        value = round(feedback, 4)
        yield self.client.msquared.resonator_tune(value)

        #print 'Err %.3fMHz | Out %.4f' % (self.pid.error, feedback)

        self.log()

    def log(self):
        if self.log_path == None:
            return

        with open(self.log_path, 'a') as f:
            f.write('%s,%s\n' % (time(), self.pid.error))

    @property
    def spectrum_analyzer(self):
        return self.client.spectrum_analyzer

    @property
    def msquared(self):
        return self.client.msquared

    @setting(0, 'get_lock_points', returns='*2v[]')
    def get_lock_points(self, c):
        """
        Find possible lock points
        """

        if self.is_locked:
            raise Exception('Cannot get lock points while being locked. Unlock first')

        # zoom out
        yield self.spectrum_analyzer.frequency_range(*self.capture_range)

        # find peaks
        trace = yield self.spectrum_analyzer.trace()
        trace = np.array(trace)
        average = np.average(trace)

        positions = detect_peaks(trace, mph=average + self.peak_threshold, mpd=10)
        powers = trace[positions]

        df = (self.capture_range[1] - self.capture_range[0]) / len(trace)
        frequencies = np.array(positions) * df + self.get_capture_range(c)[0]

        defer.returnValue([frequencies, powers])

    @setting(1, 'get_lock_points_table', returns='s')
    def get_lock_points_table(self, c):
        """
        Returns pretty table with possible lock points
        """

        table = ('+-----------------+-------------+\n' +
                 '| Frequency (MHz) | Power (dBm) |\n' +
                 '+=================+=============+\n')

        values = yield self.get_lock_points(c)
        values = np.array(values).T

        for row in values:
            frequency, power = row
            f = ('%.2f' % (frequency/1e6)).rjust(15)
            p = ('%.1f' % power).rjust(11)

            table += '| %s | %s |\n' % (f, p)

        table += '+-----------------+-------------+'

        defer.returnValue(table)

    @setting(2, 'lock', frequency='v[]', returns='v[]')
    def lock(self, c, frequency):
        """
        Locks to <frequency>
        """

        # assume values < 500 are in units of MHz
        if (frequency < 500):
            frequency *= 1e6

        # find optimal lock point from target frequency
        frequencies, _ = yield self.get_lock_points(c)

        frequency_offsets = np.abs(frequencies - frequency)
        min_offset = np.min(frequency_offsets)
        min_index = np.where(frequency_offsets == min_offset)[0][0]

        f_0 = frequencies[min_index]

        # zoom into lock point
        df = self.lock_span/2
        yield self.spectrum_analyzer.frequency_range(f_0-df, f_0+df)

        # set pid setpoint to f_0
        self.pid.setpoint = f_0/1e6

        # spectrum analyzer might glitch
        # => wait for one second before applying lock
        reactor.callLater(1, self.enable_lock)

        defer.returnValue(f_0)

    @setting(3, 'lock_smart', returns='?')
    def lock_smart(self, c):
        """
        Locks to the best/lagest lock point
        """

        values = yield self.get_lock_points(c)
        if len(values) == 0:
            defer.returnValue(False)
        else:
            frequencies, powers = np.array(values)

            frequency = frequencies[np.argmax(powers)]
            lock_frequency = yield self.lock(c, frequency)

            defer.returnValue(lock_frequency)

    @setting(4, 'unlock')
    def unlock(self, c, frequency):
        """
        Removes lock
        """

        self.is_locked = False

        # reset pid buffers
        self.pid.reset()

        # stop logging
        yield self.stop_logging(c)

        # zoom out
        yield self.spectrum_analyzer.frequency_range(*self.capture_range)

    @setting(5, 'get_lock_status', returns='b')
    def get_lock_status(self, c):
        """
        Returns current lock status
        """

        return self.is_locked and self.lock_status

    @setting(6, 'set_setpoint', setpoint='v[]')
    def set_setpoint(self, c, setpoint):
        """
        Sets PID setpoint to <setpoint>
        """

        self.pid.setpoint = setpoint/1e6

    @setting(7, 'get_setpoint', returns='v[]')
    def get_setpoint(self, c):
        """
        Returns PID setpoint
        """

        return self.pid.setpoint*1e6

    @setting(8, 'set_gain', gain='v[]')
    def set_gain(self, c, gain):
        """
        Sets PID overall gain to <gain>
        """

        self.pid.set_params(overall_gain=gain)

    @setting(9, 'get_gain', returns='v[]')
    def get_gain(self, c):
        """
        Returns PID overall gain
        """

        return self.pid.overall_gain

    @setting(10, 'set_prop_gain', gain='v[]')
    def set_prop_gain(self, c, gain):
        """
        Sets PID proportional gain to <gain>
        """

        self.pid.set_params(prop_gain=gain)

    @setting(11, 'get_prop_gain', returns='v[]')
    def get_prop_gain(self, c, gain):
        """
        Returns PID proportional gain
        """

        return self.pid.prop_gain

    @setting(12, 'set_int_gain', gain='v[]')
    def set_int_gain(self, c, gain):
        """
        Sets PID integrator gain to <gain>
        """

        self.pid.set_params(int_gain=gain)

    @setting(13, 'get_int_gain', returns='v[]')
    def get_int_gain(self, c):
        """
        Return PID integrator gain
        """

        return self.pid.int_gain

    @setting(14, 'set_diff_gain', gain='v[]')
    def set_diff_gain(self, c, gain):
        """
        Sets PID differentiator gain to <gain>
        """

        self.pid.set_params(diff_gain=gain)

    @setting(15, 'get_diff_gain', returns='v[]')
    def get_diff_gain(self, c):
        """
        Returns PID differentiator gain
        """

        return self.pid.diff_gain

    @setting(16, 'set_offset', offset='v[]')
    def set_offset(self, c, offset):
        """
        Sets PID offset to <offset>
        """
        yield self.msquared.resonator_tune(offset)
        self.pid.offset = offset

    @setting(17, 'get_offset', returns='v[]')
    def get_offset(self, c):
        """
        Returns PID offset
        """

        return self.pid.offset

    @setting(18, 'set_clamp', rng='(vv)')
    def set_clamp(self, c, rng):
        """
        Sets PID clamp values to <rng>
        """

        self.pid.min_max = rng

    @setting(19, 'get_clamp', returns='(vv)')
    def get_clamp(self, c):
        """
        Returns PID clamp values
        """

        return self.pid.min_max

    @setting(20, 'get_error', returns='v[]')
    def get_error(self, c):
        """
        Returns PID error
        """

        return self.pid.error

    @setting(21, 'get_peak_threshold', returns='v[]')
    def get_peak_threshold(self, c):
        """
        Returns peak threshold
        """

        return self.peak_threshold

    @setting(22, 'set_peak_threshold', threshold='v[]')
    def set_peak_threshold(self, c, threshold):
        """
        Sets peak threshold to <threshold>
        """

        self.peak_threshold = threshold

    @setting(23, 'get_capture_range', returns='(vv)')
    def get_capture_range(self, c):
        """
        Returns capture range
        """

        return self.capture_range

    @setting(24, 'set_capture_range', range='(vv)')
    def set_capture_range(self, c, range):
        """
        Sets capture range to <range>
        """

        self.capture_range = range

    @setting(25, 'get_lock_span', returns='v')
    def get_lock_span(self, c):
        """
        Returns lock span
        """

        return self.lock_span

    @setting(26, 'set_lock_span', span='v')
    def set_lock_span(self, c, span):
        """
        Sets lock span to <span>
        """

        self.lock_span = span

    @setting(27, 'save_current_settings')
    def save_current_settings(self, c):
        """
        Saves current settings to disk
        """

        settings = self.current_settings
        settings_json = json.dumps(settings, indent=2)

        with open('config.json', 'w') as f:
            f.write(settings_json)

        print 'Saved current settings to config.json'

    @setting(28, 'start_logging')
    def start_logging(self, c):
        """
        Starts logging pid error to disk
        """

        log_filename = 'log-%s.csv' % datetime.now().strftime("%Y%m%d%H%M%S")
	root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(os.sep, root, 'logs', log_filename)
        self.log_path = os.path.abspath(path)

        # touch
        open(self.log_path, 'a').close()

    @setting(29, 'stop_logging')
    def stop_logging(self, c):
        """
        Stops logging
        """

        self.log_path = None
    
    @setting(30)
    def enable_lock(self):
        self.is_locked = True

    @setting(31)
    def disable_lock(self):
        self.is_locked = False

    @property
    def current_settings(self):
        settings = {
                'pid': {
                    'overall_gain': self.pid.overall_gain,
                    'prop_gain': self.pid.prop_gain,
                    'int_gain': self.pid.int_gain,
                    'diff_gain': self.pid.diff_gain,
                    'range': self.pid.min_max,
                    'offset': self.pid.offset
                },
                'spectrum_analyzer': {
                    'capture_range': self.capture_range,
                    'lock_span': self.lock_span,
                    'threshold': self.peak_threshold
                }
            }

        return settings

    @staticmethod
    def load_config(path):
        if (not os.path.isfile(path)):
            raise Exception('DS815Server: Could not find configuration (%s).', config_path)

        f = open(path, 'r')
        json_data = f.read()
        f.close()

        return json.loads(json_data)

if __name__ == '__main__':
    from labrad import util

    server = MSquaredCombLockServer()
    util.runServer(server)
