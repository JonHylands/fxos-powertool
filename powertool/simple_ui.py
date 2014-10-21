from Tkinter import *

from suite_runner import SuiteRunner
from time_utils import now_in_millis
from ui import UI

UIClass = "SimpleUI"

RIGHT_SIDE = 320
BOTTOM_SIDE = 91
LINE_HEIGHT = 30
APP_NAME = "FxOS Powertool -- "
FRAMERATE = 125
FRAME_DELAY = 1000 / FRAMERATE

class SimpleUI(UI, SuiteRunner):

    def __init__(self, suite, show=None):
        super(SimpleUI, self).__init__()
        self._suite = suite
        self._show = show
        self._test_index = 0

        self._root = Tk()
        self._updateTitle()

        self._canvasFrame = Frame(self._root)
        self._canvasFrame.pack(side=TOP)
        self._mainCanvas = Canvas(self._canvasFrame, width=RIGHT_SIDE, height=1)
        self._mainCanvas.pack(side=TOP, fill=X)

        self._startStopButton = Button(self._canvasFrame, text="Start", command=self._startStopTest)
        self._startStopButton.pack(side=TOP, fill=X)
        self._nextButton = Button(self._canvasFrame, text="Next Test", command=self.nextTest)
        self._nextButton.pack(side=TOP, fill=X)
        self._prevButton = Button(self._canvasFrame, text="Prev Test", command=self.prevTest)
        self._prevButton.pack(side=TOP, fill=X)
        self._root.bind("<Key>", self._keyEvent)

	self._reset()

    def _reset(self):
	self._timer_id = None

    def _tick(self):
        self._timer_id = self._mainCanvas.after(FRAME_DELAY, self._tick)
        try:
            # extract a dict of samples from the test run
            self._suite.getSample()
        except:
            self.stopTest()
            return



    def _updateTitle(self):
        self._root.title(APP_NAME + " -- Test: " + self._suite.tests[self._test_index])

    # handle key presses
    def _keyEvent(self, event):
        if event.char == 'q':
            if self._suite.testRunning:
                self.stopTest()
            self._root.destroy()
        elif event.char == ' ':
            self._startStopTest()
        elif not self._suite.testRunning:
            if event.char == 'l':
                self.nextTest()
            elif event.char == 'h':
                self.prevTest()

    def _startStopTest(self):
        if self._suite.testRunning:
            self.stopTest()
            if self._timer_id != None:
                self._mainCanvas.after_cancel(self._timer_id)
            self._startStopButton.config(text="Start")
            self._nextButton.config(state=NORMAL)
            self._prevButton.config(state=NORMAL)
        else:
            self._reset()
            self._startStopButton.config(text="Stop")
            self._nextButton.config(state=DISABLED)
            self._prevButton.config(state=DISABLED)
            self.startTest()

    def run(self):
        self._root.mainloop()

    def startTest(self):
        try:
            self._suite.startTest(self._suite.tests[self._test_index])
        except Exception, e:
            print("failed to start test: %s" % e)

        self._tick()

    def stopTest(self):
        try:
            self._suite.stopTest()
        except Exception, e:
            print("failed to stop test: %s" % e)
        
    def nextTest(self):
        if self._test_index + 1 < len(self._suite.tests):
            self._test_index += 1
        self._reset()
        self._updateTitle()

    def prevTest(self):
        if self._test_index > 0:
            self._test_index -= 1
        self._reset()
        self._updateTitle()
