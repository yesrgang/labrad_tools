'''
Created on Dec 22, 2010

@author: christopherreilly
'''
# General class representing device server
# that communicates with serial ports.

# Handles writing, reading operations from
# serial port, as well as connecting.

# Subclass this if you are writing a device
# server that communicates using serial port

# Only connects to one port right now.
# Might be cleaner to keep it this way.

from twisted.internet.defer import returnValue, inlineCallbacks
from labrad.server import LabradServer, setting
from labrad.types import Error

class SerialConnection():
    """
    Wrapper for our server's client connection to the serial server.
    @raise labrad.types.Error: Error in opening serial connection
    """
    def __init__( self, serial_server, port, **kwargs ):
        timeout = kwargs.get('timeout')
        baudrate = kwargs.get('baudrate')
        stopbits = kwargs.get('stopbits')
        bytesize = kwargs.get('bytesize')
        serial_server.open(port)
        if timeout is not None: 
            serial_server.timeout(timeout)
        if baudrate is not None: 
            serial_server.baudrate(baudrate)
        if stopbits is not None: 
            serial_server.stopbits(stopbits)
        if bytesize is not None: 
            serial_server.bytesize(bytesize)
        self.write = lambda s: serial_server.write(s)
        self.write_line = lambda s: serial_server.write_line(s)
        self.write_lines = lambda s: serial_server.write_lines(s)
        self.read = lambda x = 0: serial_server.read(x)
        self.read_line = lambda: serial_server.read_line()
        self.read_lines = lambda: serial_server.read_lines()
        self.close = lambda: serial_server.close()
        self.flushinput = lambda: serial_server.flushinput()
        self.flushoutput = lambda: serial_server.flushoutput()
        self.ID = serial_server.ID

class SerialDeviceServer( LabradServer ):
    """
    Base class for serial device servers.
    Contains a number of methods useful for using labrad's serial server.
    Functionality comes from ser attribute, which represents a connection that performs reading and writing to a serial port.
    subclasses should assign some or all of the following attributes:
    name: Something short but descriptive
    timeOut: Time to wait for response before giving up.
    """
    name = 'serial_device'
    port = None
    baudrate = None
    timeout = None
    stopbits = None
    bytesize = None
    serial_server = None
    open_connections = []
    

    def init_serial(self, serial_server_name, port, **kwargs):
        if kwargs.get('timeout') is None and self.timeout: 
            kwargs['timeout'] = self.timeout
        if kwargs.get('baudrate') is None and self.baudrate: 
            kwargs['baudrate'] = self.baudrate
        if kwargs.get('stopbits') is None and self.stopbits: 
            kwargs['stopbits'] = self.stopbits
        if kwargs.get('bytesize') is None and self.bytesize: 
            kwargs['bytesize'] = self.bytesize

        print '\nAttempting to connect at:'
        print '\n\tserver:\t%s' % serial_server_name
        print '\n\tport:\t%s' % port
        print '\n\tbaudrate:\t%s' % (str(kwargs.get('baudrate')) if kwargs.get('baudrate') is not None else 'Default')
        print '\n\tstopbits:\t%s' % (str(kwargs.get('stopbits')) if kwargs.get('stopbits') is not None else 'Default')
        print '\n\tbytesize:\t%s' % (str(kwargs.get('bytesize')) if kwargs.get('bytesize') is not None else 'Default')
        print '\n\ttimeout:\t%s\n\n' % (str(kwargs.get('timeout')) if kwargs.get('timeout') is not None else 'No timeout' )
        
        try:
            # get server wrapper for serial server
            serial_server = self.client.servers[serial_server_name]
            # instantiate SerialConnection convenience class
            serial_server_connection = SerialConnection( serial_server=serial_server, port=port, **kwargs )
            print 'serial connection opened.'
            self.open_connections.append(serial_server_connection)
            return serial_server_connection
        except Exception:
            serial_server_connection = None
            print "unable to open serial connection"

    def stopServer( self ):
        """
        Close serial connections before exiting.
        """
        for c in self.open_connections:
            c.close()

