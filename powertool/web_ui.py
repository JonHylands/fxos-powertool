
import sys
import json

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

from ui import UI
from suite_runner import SuiteRunner


# The name of the SampleDisplayer class to use
UIClass = "WebUI"

class WebUI(UI, SuiteRunner):

    def __init__(self, suite, show=None):
        super(WebUI, self).__init__()
        self._suite = suite
        self._show = show

        ServerFactory = PowerServerFactory
        factory = ServerFactory("ws://localhost:9000", False, False)

        factory.protocol = PowerServerProtocol
        factory.setProtocolOptions(allowHixie76 = True)
        factory.setSuite(self._suite)
        listenWS(factory)

        webdir = File(".")
        web = Site(webdir)
        reactor.listenTCP(8080, web)

    def run(self):
        reactor.run()

    def startTest(self):
        pass

    def stopTest(self):
        pass

    def nextTest(self):
        pass

    def prevTest(self):
        pass



class PowerServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class PowerServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
        self.clients = []

    def setSuite(self, suite):
        self._suite = suite

    def tick(self):
        if self.clients:
            sample = self._suite.getSample()
            json_string = json.dumps(sample)
            for c in self.clients:
                c.sendMessage(json_string)
            reactor.callLater(0.02, self.tick)

    def register(self, client):
        tickLater = len(self.clients) == 0
        if not client in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)
            if tickLater:
                self.tick()

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)
