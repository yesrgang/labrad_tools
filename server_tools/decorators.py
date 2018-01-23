from labrad.decorators import setting
from twisted.internet.defer import returnValue, inlineCallbacks

#def is_generator(function):
#    return bool(function.func_code.co_flags & 20)
#
#@inlineCallbacks
#def device_call(device_method, *args, **kwargs):
#    if is_generator(device_method):
#        response = yield device_method(*args, **kwargs)
#        returnValue(response)
#    else:
#        yield None
#        response = device_method(*args, **kwargs)
#        returnValue(response)
#
#
def quickSetting(lr_ID, arg_type, do_set=True, do_get=True):
    def decorator(f):
        name = f.__name__
        def wrapper(self, c, arg=None):
            device = self.get_selected_device(c)
            
            if not hasattr(device, 'set_'+name) and do_set:
                message = 'device not configured for setting {}'.format(name)
                raise Exception(message)
            if not hasattr(device, 'get_'+name) and do_get:
                message = 'device not configured for getting {}'.format(name)
                raise Exception(message)

            @inlineCallbacks
            def do():
                ans = None
                if arg is not None and do_set:
                    device_method = getattr(device, 'set_' + name)
                    yield device_method(arg)
                if do_get:
                    device_method = getattr(device, 'get_' + name)
                    ans = yield device_method()
                returnValue(ans)

            try:
                ans = yield do()
            except:
                print 'error with {} call {}'.format(device.name, name)
                print 'reinitializing...'
#                yield device_call(device.initialize)
                yield device.initialize()
                ans = yield do()

            setattr(device, name, ans)
            yield self.send_update(c)
            returnValue(getattr(device, name))
        return setting(lr_ID, name, arg_type)(wrapper)
    return decorator

def autoSetting(lr_ID, lr_name=None, returns=[], unflatten=True, **params):
    def decorator(f):
        name = f.__name__
        def wrapper(self, c, arg):
            device = self.get_selected_device(c)
            try:
                ans = yield f(c, args)
            except:
                yield device.initialize()
                ans = yield f(c, args)

            returnValue(ans)
        return setting(lr_ID, lr_name, returns, unflatten, **params)(wrapper)
    return decorator
