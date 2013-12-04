#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
import serial
import time

# when we run from Notepad++, the working directory is wrong - fix it here
currentPath = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentPath)

from Tkinter import *

def ProcessPacket(packetBytes):
	packetLength = len(packetBytes)
	if packetLength != 86:
		print 'Packet is not 86 bytes long - {} bytes'.format(packetLength)
		return

	dataPortion = packetBytes[5:packetLength-1]
	for index in range(0, 10):
		startIndex = index * 8
		endIndex = startIndex + 8
		sampleBytes = dataPortion[startIndex:endIndex]
		current = ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256)
		if (current > 32767):
			current = (65536 - current) * -1;
		voltage = ord(sampleBytes[2]) + (ord(sampleBytes[3]) * 256)
		msCounter = ord(sampleBytes[4]) + (ord(sampleBytes[5]) * 256) + (ord(sampleBytes[6]) * 65536) + (ord(sampleBytes[7]) * 16777216)
		print 'Sample %(index)d  - current: %(current)d voltage: %(voltage)d msCounter: %(counter)d' \
			% {"index": index, "current": current, "voltage": voltage, "counter": msCounter}


print 'MozAmpTest'

serialPort = serial.Serial(port='/dev/ttyACM0', baudrate=1000000, timeout=1)

# commandBytes = bytearray.fromhex("ff ff 01 02 01 FB") #SET_ID
commandBytes = bytearray.fromhex("ff ff 01 02 02 FA") #START_ASYNC
# commandBytes = bytearray.fromhex("ff ff 01 02 03 F9") #STOP_ASYNC
# commandBytes = bytearray.fromhex("ff ff 01 02 05 F7") #TURN_OFF_BATTERY
# commandBytes = bytearray.fromhex("ff ff 01 02 06 F6") #TURN_ON_BATTERY

serialPort.write(commandBytes)
serialPort.flush()

bytes = serialPort.read(86)

f = open('data.txt', 'wb')
f.write(bytes)
f.close()

ProcessPacket(bytes)

commandBytes = bytearray.fromhex("ff ff 01 02 03 F9") #STOP_ASYNC
serialPort.write(commandBytes)
serialPort.flush()
serialPort.close()
