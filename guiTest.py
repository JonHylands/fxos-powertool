#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys,math
import datetime as dt

# when we run from Notepad++, the working directory is wrong - fix it here
currentPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentPath)

from sample import *
from Tkinter import *

#==============================================================================

RIGHT_SIDE = 800
BOTTOM_SIDE = 800
ZERO_LINE = BOTTOM_SIDE / 2
SCALE_FACTOR = 2
FRAMERATE = 10
FRAME_DELAY = 1000 / FRAMERATE

class SampleDisplayer:
	def __init__(self):
		self.module = CurrentModule()

		master = Tk()
		master.title("Firefox OS Current Usage")

		self.scaleCanvas = Canvas(master, width=100, height=BOTTOM_SIDE)
		self.scaleCanvas.pack(side=LEFT, anchor=NW)

		self.canvasFrame = Frame(master)
		self.canvasFrame.pack(side=LEFT)
		self.canvasScroll = Scrollbar(self.canvasFrame, orient=HORIZONTAL)
		self.canvasScroll.pack(side=BOTTOM, fill=X)
		self.mainCanvas = Canvas(self.canvasFrame, width=RIGHT_SIDE, height=BOTTOM_SIDE, xscrollincrement=1)
		self.mainCanvas.pack(side=TOP)
		self.mainCanvas.config(xscrollcommand=self.canvasScroll.set)
		self.canvasScroll.config(command=self.mainCanvas.xview)
		self.mainCanvas.config(scrollregion=(0, 0, 0, BOTTOM_SIDE))

		BUTTON_COUNT = 2
		LINE_COUNT = (BOTTOM_SIDE / 16) - (BUTTON_COUNT * 2)
		self.frameWidget = Frame(master)
		self.frameWidget.pack(side=LEFT, anchor=NW)
		self.logWidget = Listbox(self.frameWidget, width=10, height=LINE_COUNT)
		self.logWidget.pack(side=TOP)
		self.startButton = Button(self.frameWidget, text="Start", command=self.startRunning)
		self.startButton.pack(side=TOP, fill=X)
		self.stopButton = Button(self.frameWidget, text="Stop", command=self.stopRunning)
		self.stopButton.pack(side=TOP, fill=X)

		self.drawScaleCanvas()
		self.drawInitialMainCanvas()
		self.xPosition = 0
		sample = self.module.getSample()
		current = sample.getValue()
		self.yPosition = ZERO_LINE - (current / SCALE_FACTOR)
		self.previousCurrent = 0
		self.running = False
		self.lastLine = None
		self.samples = []
		self.startTimestamp = dt.datetime.utcnow()

	def drawCurrentLine(self):
		startTime = unix_time_millis(dt.datetime.utcnow())

		# auto-scroll the canvas one pixel
		if self.xPosition > RIGHT_SIDE:
			scrollPair = self.canvasScroll.get()
			scrollPos = scrollPair[1]
			# only auto-scroll if the scroll bar is hard-right...
			if scrollPos > 0.98:
				self.mainCanvas.xview_scroll(1, "units")

		# extract a sample from the usb ammeter, and scale it to the screen
		sample = self.module.getSample()
		self.samples.append(sample)
		current = sample.getValue()
		newYPosition = ZERO_LINE - (current / SCALE_FACTOR)

		# log the current sample
		self.logWidget.insert(END, str(current) + " mA")
		self.logWidget.see(END)

		# we want horizontal lines each 100 mA
		if (self.xPosition % RIGHT_SIDE) == 0:
			for index in range(-7, 8):
				lineY = ZERO_LINE - (index * (100 / SCALE_FACTOR));
				self.mainCanvas.create_line(RIGHT_SIDE, lineY, self.xPosition + RIGHT_SIDE, lineY, fill="grey")

		# we want vertical lines every second
		if (self.xPosition % 10) == 0:
			if (self.xPosition % 100) == 0:
				color = "dark grey"
			else:
				color = "grey"
			if self.lastLine != None:
				self.mainCanvas.tag_lower(self.lastLine)
			self.lastLine = self.mainCanvas.create_line(self.xPosition, 0, self.xPosition, BOTTOM_SIDE, fill=color)

		# we want time labels every 10 seconds
		if (self.xPosition % 100) == 0:
			label = str(self.xPosition / 10)
			xPos = self.xPosition
			if xPos == 0:
				xPos = 5
			# we have this nonesense with lastLine so the last seconds text label will be above the next line
			self.mainCanvas.create_text(xPos, BOTTOM_SIDE - 10, text=label, fill="blue")

		# draw the current line(s)
		if current < 0:
			if self.previousCurrent > 0:
				self.mainCanvas.create_line(self.xPosition, self.yPosition, self.xPosition, ZERO_LINE, fill="black")
				self.mainCanvas.create_line(self.xPosition, ZERO_LINE, self.xPosition + 1, newYPosition, fill="red")
			else:
				self.mainCanvas.create_line(self.xPosition, self.yPosition, self.xPosition + 1, newYPosition, fill="red")
		else:
			if self.previousCurrent < 0:
				self.mainCanvas.create_line(self.xPosition, self.yPosition, self.xPosition, ZERO_LINE, fill="red")
				self.mainCanvas.create_line(self.xPosition, ZERO_LINE, self.xPosition + 1, newYPosition, fill="black")
			else:
				self.mainCanvas.create_line(self.xPosition, self.yPosition, self.xPosition + 1, newYPosition, fill="black")

		# update continuous values, and compute the 10 Hz delay
		self.xPosition = self.xPosition + 1
		self.mainCanvas.config(scrollregion=(0, 0, self.xPosition, BOTTOM_SIDE))
		self.yPosition = newYPosition
		self.previousCurrent = current
		drawTime = int(unix_time_millis(dt.datetime.utcnow()) - startTime)
		waitTime = max(FRAME_DELAY - drawTime, 0)
		if self.running:
			self.mainCanvas.after(waitTime, self.drawCurrentLine)

	# draw the scale lines & text down the left side of the window
	def drawScaleCanvas(self):
		self.scaleCanvas.create_line(99, 0, 99, BOTTOM_SIDE)
		for index in range(-7, 8):
			current = index * 100
			yPosition = (ZERO_LINE - 3) - (index * 50)
			label = str(current) + ' mA'
			self.scaleCanvas.create_text(10, yPosition, text=label, anchor=SW)
			self.scaleCanvas.create_line(0, yPosition + 5, 99, yPosition + 5)
		self.scaleCanvas.create_text(90, BOTTOM_SIDE - 2, text="seconds:", anchor=SE, fill="blue")
		self.scaleCanvas.create_line(0, BOTTOM_SIDE - 1, 99, BOTTOM_SIDE - 1)

	# we need to fill in the left side of the canvas which isn't really used
	def drawInitialMainCanvas(self):
		for index in range(-7, 8):
			newY = ZERO_LINE - (index * 50);
			self.mainCanvas.create_line(0, newY, RIGHT_SIDE, newY, fill="grey")

	def startRunning(self):
		self.running = True
		self.drawCurrentLine()

	def stopRunning(self):
		self.running = False

#===========================================================

displayer = SampleDisplayer()
displayer.startRunning()
mainloop()
