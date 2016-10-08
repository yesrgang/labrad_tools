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
            return None
    module_name = 'devices.{}.{}'.format(device_name, parameter_name)
    class_name = camelize(parameter_name)
    module = __import__(module_name, fromlist=[class_name])
    reload(module)
    return getattr(module, class_name)

def remaining_points(parameters):
    try:
        return max([remaining_points_parameter(p) for dp in parameters.values()
                                                  for p in dp.values()
                                                  if p.priority])
    except:
        return 0

def remaining_points_parameter(parameter):
    value = parameter.value
    if parameter.priority:
        if parameter.value_type == 'single':
            if type(value).__name__ == 'list':
                return len(value)
    else:
        return 0

def advance_parameter_value(parameter):
    value = parameter.value
    if type(value).__name__ == 'list' and parameter.value_type == 'single':
        old = value.pop(0)
        if len(value) <= 1:
            parameter.value = value[0]
    if type(value).__name__ == 'list' and parameter.value_type == 'list':
        if type(value[0]).__name__ == 'list':
            old = value.pop(0)
            if len(value) <= 1:
                parameter.value = value[0]


def get_parameter_value(parameter):
    value = parameter.value
    try:
        value = parameter.value()
    except:
        value = parameter.value
    if parameter.value_type == 'single' and type(value).__name__ == 'list':
        return value[0]
    if parameter.value_type == 'list' and type(value).__name__ == 'list':
        if type(value[0]).__name__ == 'list':
            return value[0]
        else: 
            return value
    else: 
        return value
