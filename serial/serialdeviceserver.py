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

class SerialDeviceError( Exception ):
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return repr( self.value )

class SerialConnectionError( Exception ):
    errorDict = {
        0:'Could not find serial server in list',
        1:'Serial server not connected',
        2:'Attempting to use serial connection when not connected'
        }
    def __init__( self, code ):
        self.code = code
    def __str__( self ):
        return self.errorDict[self.code]

class PortRegError( SerialConnectionError ):
    errorDict = { 0:'Registry not properly configured' , 1:'Key not found in registry' , 2:'No keys in registry' }

NAME = 'SerialDevice'

class SerialDeviceServer( LabradServer ):
    """
    Base class for serial device servers.
    Contains a number of methods useful for using labrad's serial server.
    Functionality comes from ser attribute, which represents a connection that performs reading and writing to a serial port.
    subclasses should assign some or all of the following attributes:
    name: Something short but descriptive
    port: Name of serial port (Better to look this up in the registry using regKey and getPortFromReg())
    regKey: Short string used to find port name in registry
    serNode: Name of node running desired serial server. Used to identify correct serial server.
    timeOut: Time to wait for response before giving up.
    """
    name = NAME
    port = None
    baudrate = None
    regKey = None
    serNode = None
    timeout = None
    stopbits = None
    bytesize = None
    serial_server = None
    deviceFound = False
    
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
            serial_server.open( port )
            if timeout is not None: serial_server.timeout( timeout )
            if baudrate is not None: serial_server.baudrate( baudrate )
            if stopbits is not None: serial_server.stopbits( stopbits )
            if bytesize is not None: serial_server.bytesize( bytesize )
            self.write = lambda s: serial_server.write( s )
            self.write_line = lambda s: serial_server.write_line(s)
            self.write_lines = lambda s: serial_server.write_lines(s)
            self.read = lambda x = 0: serial_server.read( x )
            self.read_line = lambda: serial_server.read_line()
            self.read_lines = lambda: serial_server.read_lines() #sdfa
            self.close = lambda: serial_server.close()
            self.flushinput = lambda: serial_server.flushinput()
            self.flushoutput = lambda: serial_server.flushoutput()
            self.ID = serial_server.ID


    def init_serial( self, serial_server_name, port, **kwargs):
        """
        Initialize serial connection.
        Attempts to initialize a serial connection using
        given key for serial serial and port string.
        Sets server's ser attribute if successful.
        @param serial_server_name: Key for serial server
        @param port: Name of port to connect to
        @raise SerialConnectionError: Error code 1. Raised if we could not create serial connection.
        """
        if kwargs.get('timeout') is None and self.timeout: kwargs['timeout'] = self.timeout
        if kwargs.get('baudrate') is None and self.baudrate: kwargs['baudrate'] = self.baudrate
        if kwargs.get('stopbits') is None and self.stopbits: kwargs['stopbits'] = self.stopbits
        if kwargs.get('bytesize') is None and self.bytesize: kwargs['bytesize'] = self.bytesize

        print '\nAttempting to connect at:'
        print '\n\tserver:\t%s' % serial_server_name
        print '\n\tport:\t%s' % port
        print '\n\tbaudrate:\t%s' % (str( self.baudrate) if kwargs.get('baudrate') is not None else 'Default')
        print '\n\tstopbits:\t%s' % (str( self.stopbits) if kwargs.get('stopbits') is not None else 'Default')
        print '\n\tbytesize:\t%s' % (str( self.bytesize) if kwargs.get('bytesize') is not None else 'Default')
        print '\n\ttimeout:\t%s\n\n' % ( str( self.timeout ) if kwargs.get('timeout') is not None else 'No timeout' )
        
        client = self.client
        try:
            # get server wrapper for serial server
            serial_server = client.servers[ serial_server_name ]
            # instantiate SerialConnection convenience class
            self.serial_server = self.SerialConnection( serial_server=serial_server, port=port, **kwargs )
            print 'Serial connection opened.'
        except Error:
            self.serial_server = None
            raise SerialConnectionError( 1 )

#    @inlineCallbacks
#    def getPortFromReg( self, regKey = None ):
#        """
#        Find port string in registry given key.
#        If you do not input a parameter, it will look for the first four letters of your name attribute in the registry port keys.
#        @param regKey: String used to find key match.
#        @return: Name of port
#        @raise PortRegError: Error code 0. Registry does not have correct directory structure (['','Ports']).
#        @raise PortRegError: Error code 1. Did not find match.
#        """
#        reg = self.client.registry
#        #There must be a 'Ports' directory at the root of the registry folder
#        try:
#            tmp = yield reg.cd()
#            yield reg.cd( ['', 'Ports'] )
#            y = yield reg.dir()
#            if not regKey:
#                if self.name: regKey = self.name[:4].lower()
#                else: raise SerialDeviceError( 'name attribute is None' )
#            portStrKey = filter( lambda x: regKey in x , y[1] )
#            if portStrKey: portStrKey = portStrKey[0]
#            else: raise PortRegError( 1 )
#            portStrVal = yield reg.get( portStrKey )
#            reg.cd(tmp)
#            returnValue( portStrVal )
#        except Error, e:
#            reg.cd(tmp)
#            if e.code == 17: raise PortRegError( 0 )
#            else: raise
#
#    @inlineCallbacks
#    def selectPortFromReg( self ):
#        """
#        Select port string from list of keys in registry
#        @return: Name of port
#        @raise PortRegError: Error code 0. Registry not properly configured (['','Ports']).
#        @raise PortRegError: Error code 1. No port keys in registry.
#        """
#        reg = self.client.registry
#        try:
#            #change this back to 'Ports'
#            yield reg.cd( ['', 'Ports'] )
#            portDir = yield reg.dir()
#            portKeys = portDir[1]
#            if not portKeys: raise PortRegError( 2 )
#            keyDict = {}
#            map( lambda x , y: keyDict.update( { x:y } ) ,
#                 [str( i ) for i in range( len( portKeys ) )] ,
#                 portKeys )
#            for key in keyDict:
#                print key, ':', keyDict[key]
#            selection = None
#            while True:
#                print 'Select the number corresponding to the device you are using:'
#                selection = raw_input( '' )
#                if selection in keyDict:
#                    portStr = yield reg.get( keyDict[selection] )
#                    returnValue( portStr )
#        except Error, e:
#            if e.code == 13: raise PortRegError( 0 )
#            else: raise
#
#    @inlineCallbacks
#    def find_serial_server( self, serNode = None ): # was called findSerial
#        """
#        Find appropriate serial server
#        @param serNode: Name of labrad node possessing desired serial port
#        @return: Key of serial server
#        @raise SerialConnectionError: Error code 0. Could not find desired serial server.
#        """
#        if not serNode: serNode = self.serNode
#        cli = self.client
#        # look for servers with 'serial' and serNode in the name, take first result
#        servers = yield cli.manager.servers()
#        try:
#            returnValue( [ i[1] for i in servers if self._matchSerial( serNode, i[1] ) ][0] )
#        except IndexError: raise SerialConnectionError( 0 )
#
#    @staticmethod
#    def _matchSerial( serNode, potMatch ):
#        """
#        Checks if server name is the correct serial server
#        @param serNode: Name of node of desired serial server
#        @param potMatch: Server name of potential match
#        @return: boolean indicating comparison result
#        """
#        serMatch = 'serial' in potMatch.lower()
#        nodeMatch = serNode.lower() in potMatch.lower()
#        return serMatch and nodeMatch
#
#    def checkConnection( self ):
#        if not self.ser: raise SerialConnectionError( 2 )
#
#    def serverConnected( self, ID, name ):
#        """Check to see if we can connect to serial server now"""
#        if self.ser is None and None not in ( self.port, self.serNode ) and self._matchSerial( self.serNode, name ):
#            self.init_serial( name, self.port, self.timeout )
#            print 'Serial server connected after we connected'
#
#    def serverDisconnected( self, ID, name ):
#        """Close connection (if we are connected)"""
#        if self.ser and self.ser.ID == ID:
#            print 'Serial server disconnected. Relaunch the serial server'
#            self.ser = None

    def stopServer( self ):
        """
        Close serial connection before exiting.
        """
        if self.serial_server:
            self.serial_server.close()
