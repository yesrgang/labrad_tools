"""
### BEGIN NODE INFO
[info]
name = plotter
version = 1.0
description = 
instancename = plotter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import imp
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os

from time import time

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.reactor import callLater
import StringIO

from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory

WEBSOCKET_PORT = 9000

class MyServerProtocol(WebSocketServerProtocol):
    connections = list()

    def onConnect(self, request):
        self.connections.append(self)
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
    
    @classmethod
    def send_figure(cls, figure):
        print 'num connections', len(cls.connections)
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendMessage, c, figure, False)
    
    @classmethod
    def close_all_connections(cls):
        for c in set(cls.connections):
            reactor.callFromThread(cls.sendClose, c)
    
    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.connections.remove(self)
        print("WebSocket connection closed: {0}".format(reason))

class PlotterServer(LabradServer):
    name = 'plotter'
    is_plotting = False

    def initServer(self):
        """ socket server """
        url = u"ws://0.0.0.0:{}".format(WEBSOCKET_PORT)
        factory = WebSocketServerFactory()
        factory.protocol = MyServerProtocol
        reactor.listenTCP(WEBSOCKET_PORT, factory)
    
    def stopServer(self):
        """ socket server """
        MyServerProtocol.close_all_connections()

    @setting(0)
    def plot(self, c, settings_json='{}'):
        settings = json.loads(settings_json)
        if not self.is_plotting:
            reactor.callInThread(self._plot, settings)
        else:
            print 'still making previous plot'

    def _plot(self, settings):
        try:
            self.is_plotting = True
            print 'plotting'
            path = settings['plotter_path']                 
            function_name = settings['plotter_function'] # name of function that will process data
            module_name = os.path.split(path)[-1].strip('.py')
            module = imp.load_source(module_name, path)
            function = getattr(module, function_name)
            fig = function(settings)
            sio = StringIO.StringIO()
            fig.savefig(sio, format='svg')
            sio.seek(0)
            figure_data = sio.read()
            MyServerProtocol.send_figure(figure_data)
            print 'done plotting'
        except Exception as e:
            raise e
            print 'failed plotting'
        finally:
            self.is_plotting = False
            try:
                plt.close(fig)
                del fig
                del sio
                del figure_data
            except:
                pass

__server__ = PlotterServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__())
