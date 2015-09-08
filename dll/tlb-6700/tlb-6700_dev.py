import ctypes as c
from time import sleep

npdll = c.WinDLL('C:\Program Files (x86)\Newport\Newport USB Driver\Bin\usbdll.dll')

npdll.newp_usb_init_system()
Buffer = c.create_string_buffer(64)
npdll.newp_usb_get_device_info(c.byref(Buffer))
print Buffer.value

DeviceID = c.c_long(int(Buffer.value[0]))

def piezo(percentage=None):
    if percentage is not None:
        send('source:voltage:piezo {}\r\n'.format(percentage))
	get()
    send('source:voltage:piezo?\r\n')
    get()

def diode(current=None):
    if current is not None:
        send('source:current:diode {}\r\n'.format(current))
	get()
    send('source:current:diode?\r\n')
    get()

def send(command):
    Command = c.create_string_buffer(64)
    Command.value = command
    CommandLength = c.c_ulong(len(command))
    npdll.newp_usb_send_ascii(DeviceID, c.byref(Command), CommandLength)
    print 'command: ', Command.value

def get():
#    sleep(1)
    BufferLength = c.c_ulong(64)
    Buffer = c.create_string_buffer(BufferLength.value)
    BytesRead = c.c_ulong(1)
    error = npdll.newp_usb_get_ascii(DeviceID, c.byref(Buffer), BufferLength, c.addressof(BytesRead))
    print 'bytes read: ', BytesRead.value
    print 'error: ', error
    print 'buf: ', Buffer.value.split('\r\n')[0]
    return error, Buffer



#send('*IDN?\r\n')
#err, buf = get()
#print err, buf.value
#piezo(61.65)
diode(158.0)
