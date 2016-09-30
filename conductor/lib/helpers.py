from inflection import camelize

def import_parameter(device_name, parameter_name):
    path = 'devices.{}.{}'.format(device_name, parameter_name)
    class_name = camelize(parameter_name)
    module = __import__(path, fromlist=[class_name])
    return getattr(module, class_name)

def remaining_points(parameters):
    try:
        return min([len(p.value) for dp in parameters.values() 
                                 for p in dp.values()])
    except:
        return 0

def advance_parameter_value(parameter):
    value = parameter.value
    if type(value).__name__ == 'list':
        old = value.pop(0)
        if len(value) <= 1:
            parameter.value = value[0]

def get_parameter_value(parameter):
    value = parameter.value
    if parameter.value_type == 'single' and type(value).__name__ == 'list':
        return value[0]
    else: 
        return value
