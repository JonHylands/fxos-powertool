
import sys
import json
import time

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

from ui import UI
from suite_runner import SuiteRunner

UPDATE_FREQUENCY = 50 # Hz

TIMER_DELAY = 1.0 / UPDATE_FREQUENCY # TIMER_DELAY is in seconds

# The name of the SampleDisplayer class to use
UIClass = "WebUI"

class WebUI(UI, SuiteRunner):

    def __init__(self, suite, show=None):
        super(WebUI, self).__init__()
        self._suite = suite
        self._show = show

        ServerFactory = PowerServerFactory
        self._factory = ServerFactory("ws://localhost:9000", False, False)

        self._factory.protocol = PowerServerProtocol
        self._factory.setProtocolOptions(allowHixie76 = True)
        self._factory.setSuite(self._suite)
        listenWS(self._factory)

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

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "{} from {}".format(payload.decode('utf8'), self.peer)
            print(msg)


class PowerServerFactory(WebSocketServerFactory):

    def __init__(self, url, debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
        self.clients = []
        self._tick_pending = False

    def setup(self):
        sample = None
        try:
            sample = self._suite.getSample()
        except Exception, e:
            print("failed to get initial sample: %s" % e)
            sys.exit(0)

        msTime = int(time.time() * 1000)
        msAmmeterTime = sample["time"].value
        self._msOffset = msTime - msAmmeterTime

    def setSuite(self, suite):
        self._suite = suite
        print("Tests: {}".format(suite.tests))
        try:
            self._suite.startTest("Null Test")
        except Exception, e:
            print("failed to start test: %s" % e)
            sys.exit(0)
        reactor.callLater(0.5, self.setup)

    def tick(self):
        if self.clients:
            try:
                sample = self._suite.getSample()
                sampleMap = { \
                    "current": sample["current"].value, \
                    "voltage": sample["voltage"].value, \
                    "time": self._msOffset + sample["time"].value}
                json_string = json.dumps(sampleMap)
            except Exception, e:
                print("failed to get sample: %s" % e)
            # sometimes we get an unregister immediately followed by a register - make sure we 
            # don't propogate ticks from unregistered clients
            for c in self.clients:
                #print("sending to client: {}".format(json_string))
                c.sendMessage(json_string)
            reactor.callLater(TIMER_DELAY, self.tick)
            self._tick_pending = True
        else:
            self._tick_pending = False

    def register(self, client):
        tickLater = len(self.clients) == 0
        if not client in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)
            if not self._tick_pending:
                self.tick()

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)
            self._current_client = ""
