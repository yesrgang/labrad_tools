import os
import sys
sys.path.append('devices')

from inflection import camelize

def import_parameter(device_name, parameter_name, generic=False):
    path = os.path.join('devices', device_name, parameter_name)
    if not os.path.isfile(path+'.py'):
        if generic:
            device_name = 'generic_device'
            parameter_name = 'generic_parameter'
        else: 
            message = "could not import parameter {} {}\
                      ".format(device_name, parameter_name)
            raise Exception(message)
    module_name = 'devices.{}.{}'.format(device_name, parameter_name)
    class_name = camelize(parameter_name)
    module = __import__(module_name, fromlist=[class_name])
    reload(module)
    return getattr(module, class_name)

def remaining_points(parameters):
    return max([parameter.remaining_values() 
        for device_parameters in parameters.values()
        for parameter in device_parameters.values()])
