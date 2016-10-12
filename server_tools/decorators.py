from labrad.decorators import setting
from twisted.internet.defer import returnValue
import inspect

def quickSetting(lr_ID, arg_type):
    def decorator(f):
        name = f.__name__
        def wrapper(self, c, arg=None):
            device = self.get_device(c)
            
            if not hasattr(device, 'set_'+name) or not hasattr(device, 'get_'+name):
                message = 'device not configured for setting {}'.format(name)
                raise Exception(message)

            if arg is not None:
                yield getattr(device, 'set_'+name)(arg)
            ans = yield getattr(device, 'get_'+name)()
            setattr(device, name, ans)
            yield self.send_update(c)
            returnValue(getattr(device, name))
        return setting(lr_ID, name, arg_type)(wrapper)
    return decorator
