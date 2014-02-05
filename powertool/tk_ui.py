# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from Tkinter import *

from suite_runner import SuiteRunner
from time_utils import now_in_millis
from ui import UI

# The name of the SampleDisplayer class to use
UIClass = "TkUI"

RIGHT_SIDE = 800
BOTTOM_SIDE = 700
ZERO_LINE = BOTTOM_SIDE / 2
SCALE_FACTOR = 2
FRAMERATE = 25
FRAME_DELAY = 1000 / FRAMERATE
APP_NAME = "FxOS Powertool -- "

class TkUI(UI, SuiteRunner):
    """ This implements a Tk GUI interface for displaying samples """

    def __init__(self, suite, show=None):
        super(TkUI, self).__init__()
        self._suite = suite
        self._show = show
        self._test_index = 0

        self._root = Tk()
        
        # set the application window title
        self._updateTitle()

        self._scaleCanvas = Canvas(self._root, width=100, height=BOTTOM_SIDE)
        self._scaleCanvas.pack(side=LEFT, anchor=NW)

        self._canvasFrame = Frame(self._root)
        self._canvasFrame.pack(side=LEFT)
        self._canvasScroll = Scrollbar(self._canvasFrame, orient=HORIZONTAL)
        self._canvasScroll.pack(side=BOTTOM, fill=X)
        self._mainCanvas = Canvas(self._canvasFrame, width=RIGHT_SIDE, height=BOTTOM_SIDE, xscrollincrement=1)
        self._mainCanvas.pack(side=TOP)
        self._mainCanvas.config(xscrollcommand=self._canvasScroll.set)
        self._canvasScroll.config(command=self._mainCanvas.xview)
        self._mainCanvas.config(scrollregion=(0, 0, 0, BOTTOM_SIDE))

        BUTTON_COUNT = 2
        LINE_COUNT = (BOTTOM_SIDE / 16) - (BUTTON_COUNT * 2)
        self._frameWidget = Frame(self._root)
        self._frameWidget.pack(side=LEFT, anchor=NW)
        self._logWidget = Listbox(self._frameWidget, width=10, height=LINE_COUNT)
        self._logWidget.pack(side=TOP)
        self._startStopButton = Button(self._frameWidget, text="Start", command=self._startStopTest)
        self._startStopButton.pack(side=TOP, fill=X)
        self._nextButton = Button(self._frameWidget, text="Next Test", command=self.nextTest)
        self._nextButton.pack(side=TOP, fill=X)
        self._prevButton = Button(self._frameWidget, text="Prev Test", command=self.prevTest)
        self._prevButton.pack(side=TOP, fill=X)
        self._root.bind("<Key>", self._keyEvent)

        self._reset()

    def _reset(self):
        self._xPos = 0
        self._yPos = ZERO_LINE
        self._prevValue = 0
        self._lastLine = None
        self._timer_id = None
        self._logWidget.delete(0,END)
        self._mainCanvas.delete(ALL)
        self._drawScaleCanvas()
        self._drawInitialMainCanvas()

    def _updateTitle(self):
        self._root.title(APP_NAME + " -- Test: " + 
                         self._suite.tests[self._test_index])

    def _drawCurrentLine(self):
        startTime = now_in_millis()

        # auto-scroll the canvas one pixel
        if self._xPos > RIGHT_SIDE:
            scrollPair = self._canvasScroll.get()
            scrollPos = scrollPair[1]
            # only auto-scroll if the scroll bar is hard-right...
            if scrollPos > 0.98:
                self._mainCanvas.xview_scroll(1, "units")

        try:
            # extract a dict of samples from the test run
            samples = self._suite.getSample()
        except:
            self.stopTest()
            return

        # get the sample we are currently displaying
        sample = samples.get(self._show, None)

        if sample != None:
            # add it to 
            newYPosition = ZERO_LINE - (sample.value / SCALE_FACTOR)

            # log the sample
            self._logWidget.insert(END, " ".join([str(sample.value), sample.units]))
            self._logWidget.see(END)

            # we want horizontal lines each 100 mA
            if (self._xPos % RIGHT_SIDE) == 0:
                for index in range(-7, 8):
                    lineY = ZERO_LINE - (index * (100 / SCALE_FACTOR));
                    self._mainCanvas.create_line(RIGHT_SIDE, lineY, self._xPos + RIGHT_SIDE, lineY, fill="grey")

            # we want vertical lines every second
            if (self._xPos % FRAMERATE) == 0:
                if (self._xPos % (FRAMERATE * 10)) == 0:
                    color = "dark grey"
                else:
                    color = "grey"
                if self._lastLine != None:
                    self._mainCanvas.tag_lower(self._lastLine)
                self._lastLine = self._mainCanvas.create_line(self._xPos, 0, self._xPos, BOTTOM_SIDE, fill=color)

            # we want time labels every 10 seconds
            if (self._xPos % (FRAMERATE * 10)) == 0:
                label = str(self._xPos / FRAMERATE)
                xPos = self._xPos
                if xPos == 0:
                    xPos = 5
                # we have this nonesense with _lastLine so the last seconds text label will be above the next line
                self._mainCanvas.create_text(xPos, BOTTOM_SIDE - 10, text=label, fill="blue")

            # draw the line(s)
            if sample.value < 0:
                if self._prevValue > 0:
                    self._mainCanvas.create_line(self._xPos, self._yPos, self._xPos, ZERO_LINE, fill="black")
                    self._mainCanvas.create_line(self._xPos, ZERO_LINE, self._xPos + 1, newYPosition, fill="red")
                else:
                    self._mainCanvas.create_line(self._xPos, self._yPos, self._xPos + 1, newYPosition, fill="red")
            else:
                if self._prevValue < 0:
                    self._mainCanvas.create_line(self._xPos, self._yPos, self._xPos, ZERO_LINE, fill="red")
                    self._mainCanvas.create_line(self._xPos, ZERO_LINE, self._xPos + 1, newYPosition, fill="black")
                else:
                    self._mainCanvas.create_line(self._xPos, self._yPos, self._xPos + 1, newYPosition, fill="black")

            # update continuous values, and compute the 10 Hz delay
            self._xPos = self._xPos + 1
            self._mainCanvas.config(scrollregion=(0, 0, self._xPos, BOTTOM_SIDE))
            self._yPos = newYPosition
            self._prevValue = sample.value
        
        # set a timer to call this function again
        drawTime = int(now_in_millis() - startTime)
        waitTime = max(FRAME_DELAY - drawTime, 0)
        self._timer_id = self._mainCanvas.after(waitTime, self._drawCurrentLine)

    # draw the scale lines & text down the left side of the window
    def _drawScaleCanvas(self):
        self._scaleCanvas.create_line(99, 0, 99, BOTTOM_SIDE)
        for index in range(-7, 8):
            current = index * 100
            _yPos = (ZERO_LINE - 3) - (index * 50)
            label = str(current) + ' mA'
            self._scaleCanvas.create_text(10, _yPos, text=label, anchor=SW)
            self._scaleCanvas.create_line(0, _yPos + 5, 99, _yPos + 5)
        self._scaleCanvas.create_text(90, BOTTOM_SIDE - 2, text="seconds:", anchor=SE, fill="blue")
        self._scaleCanvas.create_line(0, BOTTOM_SIDE - 1, 99, BOTTOM_SIDE - 1)

    # we need to fill in the left side of the canvas which isn't really used
    def _drawInitialMainCanvas(self):
        for index in range(-7, 8):
            newY = ZERO_LINE - (index * 50);
            self._mainCanvas.create_line(0, newY, RIGHT_SIDE, newY, fill="grey")

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

        self._drawCurrentLine()

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

