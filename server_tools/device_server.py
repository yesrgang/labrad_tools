import re
import json
import types
import os
import pkgutil

from twisted.internet.defer import returnValue, inlineCallbacks
from labrad.server import LabradServer, setting
from labrad.wrappers import connectAsync

from decorators import quickSetting

def import_device(device_name):
    try:
        module_path = 'devices.{}'.format(device_name)
        device_class_name = '__device__'
        module = __import__(module_path, fromlist=[device_class_name])
        reload(module)
        device = getattr(module, device_class_name)
        device.name = device_name
        return device
    except Exception as e:
        print e
        print 'invalid device in ./devices/{}'.format(device_name)

class Device(object):
    autostart = False
    update_parameters = []
    
    def initialize(self):
        pass

    def terminate(self):
        pass

    @inlineCallbacks
    def connect_labrad(self):
        connection_name = '{} - {}'.format(self.device_server_name, self.name)
        self.cxn = yield connectAsync(name=connection_name)

class DeviceServer(LabradServer):
    devices = {}
    
    @inlineCallbacks
    def initServer(self):
        for device in self.get_configured_devices():
            if getattr(device, 'autostart'):
                yield self.initialize_device(device.name)

    def get_configured_devices(self):
        assert os.path.exists('./devices/')
        device_names = [name 
            for _, name, ispkg in pkgutil.iter_modules(['./devices/'])
            if not ispkg
            ]
        configured_devices = []
        for device_name in device_names:
            device = import_device(device_name)
            if device:
                configured_devices.append(device)
        return configured_devices
    
    @inlineCallbacks 
    def initialize_device(self, device_name):
        if device_name in self.devices:
            message = 'device {} is already active'.format(device_name)
            raise Exception(message)
        try:
            device_class = import_device(device_name)
            device = device_class()
            device.device_server = self
            device.device_server_name = self.name
            yield device.initialize()
            self.devices[device_name] = device
        except Exception as e:
            print e
            print 'unable to initialize device {}'.format(device_name)

    @inlineCallbacks 
    def terminate_device(self, device_name):
        if device_name not in self.devices:
            message = 'device {} is not active'.format(device_name)
            raise Exception(message)
        try:
            device = self.devices.pop(device_name)
            yield device.terminate()
        except Exception as e:
            print e
            print 'unable to cleanly terminate device {}'.format(device.name)
        finally:
            del device

    def get_selected_device(self, c):
        device_name = c.get('device_name')
        if device_name is None:
            raise Exception('select a device first')
        return self.devices[device_name]
    
    @setting(0, returns='s')
    def list_devices(self, c):
        """ list available devices
        
        Args:
            None
        Returns:
            json dumped dict
            {
                'active': active_devices,
                'configured': configured_devices,
            }
            where active_devices is list of names of running devices
            and configured_devices is list of names of devices configured in './devices'
        """
        active_device_names = self.devices.keys()
        configured_devices = self.get_configured_devices()
        configured_device_names = [device.name for device in configured_devices]
        response = {
            'active': active_device_names,
            'configured': configured_device_names,
            }
        return json.dumps(response)

    @setting(1, device_name='s', returns=['s', ''])
    def select_device(self, c, device_name):
        if device_name not in self.devices.keys():
            yield self.initialize_device(device_name)

        if device_name in self.devices.keys():
            c['device_name'] = device_name
            device = self.get_selected_device(c)
            device_info = {x: getattr(device, x) for x in dir(device) if x[0] != '_'}
            # ignore if cannot serialise
            device_info = json.loads(json.dumps(device_info, default=lambda x: None))
            device_info = {k: v for k, v in device_info.items() if v is not None}
            returnValue(json.dumps(device_info))
        else:
            message = 'Device {} could not be initialized. See server log for details.'.format(device_name)
            raise Exception(message)
    
    @setting(2)
    def send_update(self, c):
        device = self.get_selected_device(c)
        update = {c['device_name']: {p: getattr(device, p) 
                  for p in device.update_parameters}}
        yield self.update(json.dumps(update))

    @setting(3, device_name='s')
    def reload_device(self, c, device_name=None):
        if device_name is None:
            device_name = c.get('device_name')
        if device_name in self.devices:
            yield self.terminate_device(device_name)
        yield self.initialize_device(device_name)

