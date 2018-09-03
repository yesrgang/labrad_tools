import os

def import_recorder(recorder_name):
    path = os.path.join('devices', 'ikon', 'recorders', recorder_name)
    module_name = 'devices.ikon.recorders.{}'.format(recorder_name)
    module = __import__(module_name, fromlist=['__recorder__'])
    reload(module)
    return getattr(module, '__recorder__')

def import_processor(processor_name):
    path = os.path.join('devices', 'ikon', 'processors', processor_name)
    module_name = 'devices.ikon.processors.{}'.format(processor_name)
    module = __import__(module_name, fromlist=['__processor__'])
    reload(module)
    return getattr(module, '__processor__')
