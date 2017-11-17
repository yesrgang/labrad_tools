import os
from inflection import camelize

def import_recorder(recorder_name):
    path = os.path.join('devices', 'recorders', recorder_name)
    module_name = 'devices.recorders.{}'.format(recorder_name)
    class_name = camelize(recorder_name)
    module = __import__(module_name, fromlist=[class_name])
    reload(module)
    return getattr(module, class_name)

def import_processor(processor_name):
    path = os.path.join('devices', 'processors', processor_name)
    module_name = 'devices.processors.{}'.format(processor_name)
    class_name = camelize(processor_name)
    module = __import__(module_name, fromlist=[class_name])
    reload(module)
    return getattr(module, class_name)
