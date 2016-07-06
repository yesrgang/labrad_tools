# Class for talking to the M-squared ICE module
#
# Example usage:
#   m = MSquaredConnection(("128.138.107.135", 39933), debug=True)
#   m.open()
#   print m.get('get_status')
#   m.close()

import socket, json, random

class MSquaredConnection:
    def __init__(self, addr, debug=False):
        self.addr = addr
        self.transmission_id = 0
        self.debug = debug

    def print_debug(self, s):
        if self.debug: 
            print s

    def open(self):
        self.socket = socket.create_connection(self.addr, timeout=5)

        interface = self.socket.getsockname()[0]
        response_message = self.send(op='start_link',
                                     params={ 'ip_address': interface })

        ok = response_message.is_ok(status='ok')
        return ok != None and ok

    def close(self):
        try:
            self.socket.close()
        except:
            pass

        return True

    def send(self, **kwargs):
        message = MSquaredMessage(**kwargs)
        message_json = message.to_json()

        self.print_debug('(m-squared) <- %s' % message_json)

        self.socket.send(message_json)
        response_json = self.socket.recv(1024)

        self.print_debug('(m-squared) -> %s' % response_json)


        return MSquaredMessage.from_json(response_json)

    def set(self, setting, value, key_name='setting'):
        params = {}
        params[key_name] = value

        if key_name == 'setting':
            params[key_name] = [params[key_name]]

        response_message = self.send(op=setting, params=params)

        print response_message
        ok = response_message.is_ok(status=[0])
        return ok != None and ok

    def get(self, setting):
        response_message = self.send(op=setting,
                                     params=None)

        ok = response_message.is_ok(status=[0])

        if ok:
            params = self.normalize_params(response_message.params)
            return params
        else:
            return None

    @staticmethod
    def normalize_params(p):
        params = dict(p)

        if params['status']: 
            del params['status']

        for key, value in params.iteritems():
            if (isinstance(value, list) and len(value) == 1):
                params[key] = value[0]

        return params

class MSquaredMessage:
    def __init__(self, op, params, transmission_id=False):
        self.op = op
        self.params = params

        if transmission_id:
            self.transmission_id = transmission_id
        else:
            self.transmission_id = random.randint(1, 999)

    @classmethod
    def from_json(klass, json_string):
        msg = json.loads(json_string)['message']

        op              = msg['op']
        params          = msg['parameters']
        transmission_id = msg['transmission_id'][0]

        return klass(op, params, transmission_id)

    def message(self):
        m = {
            'transmission_id': [self.transmission_id],
            'op': self.op,
            'parameters': self.params
        }
        if self.params == None: 
            del m['parameters']

        return m

    def to_json(self):
        return json.dumps({'message': self.message()})

    def is_ok(self, status='ok'):
        if 'status' in self.params:
            return self.params['status'] == status
        else:
            return None

    def __repr__(self):
        return '<MSquaredMessage transmission_id=%s op=%s params=%s>' % \
                (str(self.transmission_id), self.op, str(self.params))
