#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
import datetime as dt
import time
# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..","YoctoLib.python.12553","Sources"))
from yocto_api import *
from yocto_current import *

def die(msg):
    sys.exit(msg+' (check USB cable)')

def unix_time(aDate):
    epoch = dt.datetime.utcfromtimestamp(0)
    delta = aDate - epoch
    return delta.total_seconds()

def unix_time_millis(aDate):
    return unix_time(aDate) * 1000.0

class CurrentSample:
	def __init__(self, module, sensorDC):
		if not module.isOnline():
			die('Module not connected')
		self.value = sensorDC.get_currentValue()
		self.timestamp = unix_time_millis(dt.datetime.utcnow())
	def getValue(self):
		return self.value
	def timestamp(self):
		return self.timestamp
	def millisecondsSince(self, startMilliseconds):
		return self.timestamp - startMilliseconds


class CurrentModule:
	def __init__(self):

		errmsg=YRefParam()
		# Setup the API to use local USB devices
		if YAPI.RegisterHub("usb", errmsg)!= YAPI.SUCCESS:
			sys.exit("init error"+errmsg.value)

		sensor = YCurrent.FirstCurrent()
		if sensor is None :
			die('No module connected')

		if sensor.isOnline():
			self.module = sensor.get_module()
			self.sensorDC = YCurrent.FindCurrent(self.module.get_serialNumber() + '.current1')
		else:
			die('Module not connected')
		self.startMillis = unix_time_millis(dt.datetime.utcnow())

	def getSample(self):
		return CurrentSample(self.module, self.sensorDC)

	def startMilliseconds(self):
		return self.startMillis

