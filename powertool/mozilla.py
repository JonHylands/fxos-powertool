# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import collections
import Queue
import serial
import sys
import threading
import time

from sample_source import SampleSource
from device_manager import DeviceManager
from sample import Sample
from time_utils import now_in_millis
from serial.tools import list_ports

# the name of the SampleSource class to use
SampleSourceClass = 'MozillaAmmeter'

SAMPLE_RATE = 100
SAMPLE_TIME = 1000 / SAMPLE_RATE

class MozillaDevice(threading.Thread):

    BAUD = 1000000
    TIMEOUT = 1
    ASYNC_RESPONSE_SIZE = 86
    SYNC_RESPONSE_SIZE = 14

    # commands
    SET_ID = bytearray.fromhex("ff ff 01 02 01 FB")
    START_ASYNC = bytearray.fromhex("ff ff 01 02 02 FA")
    STOP_ASYNC = bytearray.fromhex("ff ff 01 02 03 F9")
    TURN_OFF_BATTERY = bytearray.fromhex("ff ff 01 02 05 F7")
    TURN_ON_BATTERY = bytearray.fromhex("ff ff 01 02 06 F6")
    GET_SAMPLE = bytearray.fromhex("ff ff 01 02 07 F5")
    GET_RAW_SAMPLE = bytearray.fromhex("ff ff 01 02 0A F2")
    GET_VERSION = bytearray.fromhex("ff ff 01 02 0B F1")
    GET_SERIAL = bytearray.fromhex("ff ff 01 02 0E EE")

    #SET_SERIAL = bytearray.fromhex("ff ff 01 04 0D")
    #SET_SERIAL also includes 2 bytes (little endian) of the serial#, plus the CRC

    #SET_CALIBRATION = bytearray.fromhex("ff ff 01 0A 09")
    #SET_CALIBRATION also includes two 4-byte floats (floor and scale), plus the CRC

    def __init__(self, path, async=True):
        super(MozillaDevice, self).__init__()
        self._path = path
        if path == None:
            self._path = self._scanForDevice()
        else:
            self._path = path
        self._cmds = Queue.Queue()
        self._quit = threading.Event()
        self._packets = collections.deque(maxlen=10)
        self._module = serial.Serial(port=self._path, baudrate=self.BAUD, timeout=self.TIMEOUT)
        self._async = async

        if self._async:
            self._responseSize = self.ASYNC_RESPONSE_SIZE
            # start the thread
            super(MozillaDevice, self).start()
        else:
            self._responseSize = self.SYNC_RESPONSE_SIZE

    def _scanForDevice(self):
        # get the list of os-specific serial port names that have a Mozilla ammeter connected to them
        ports = [p[0] for p in serial.tools.list_ports.comports() if p[2].lower().startswith('usb vid:pid=03eb:204b') or p[2].lower().startswith('usb vid:pid=3eb:204b')]
        if len(ports) > 0:
            print "Found Mozilla Ammeter attached to: %s" % ports[0]
            return ports[0]
        raise SampleSourceNoDeviceError('mozilla')

    def sendCommand(self, cmd):
        """ adds a command to the command queue """
        self._cmds.put_nowait(cmd)

    def getPacket(self):
        # We use this when we're running in sync mode
        self._module.write(self.GET_SAMPLE)
        self._module.flush()
        return self._module.read(self._responseSize)

    @property
    def packet(self):
        try:
            if not self._async:
                self._packets.append( self._module.read(self._responseSize) )
            # this is atomic
            return self._packets.popleft()
        except:
            return None

    # make packet a read-only property
    @packet.setter
    def packet(self, data):
        pass

    def quit(self):
        if self._async:
            # send STOP_ASYNC command to wake up the worker thread, if needed
            self.sendCommand(self.STOP_ASYNC)

        # set the quit flag, all remaining commands will be processed before
        # the thread function exits
        self._quit.set()

        if self._async:
            # join the thread and wait for the thread function to exit
            super(MozillaDevice, self).join()

        # when we get here, the thread has stopped so close the serial port
        self._module.close()

    def run(self):
        """ This is run in a separate thread """

        # start off by putting the START_ASYNC command in the command queue
        self.sendCommand(MozillaDevice.START_ASYNC)

        while True:
            if not self._cmds.empty():
                try:
                    # block waiting for a command at most 100ms
                    cmd = self._cmds.get( True, 0.1)

                    # send the command to the device
                    self._module.write(cmd)
                    self._module.flush()

                    # mark the command as processed
                    self._cmds.task_done()

                except Queue.Empty:
                    # if we get here, the get() timed out or the queue was empty
                    pass

            elif self._quit.is_set():
                # time to quit
                return

            # read a packet from the device and queue it up
            self._packets.append( self._module.read(self._responseSize) )


class MozillaPacketHandler(threading.Thread):

    ASYNC_PACKET_SIZE = 86
    SYNC_PACKET_SIZE = 14

    def __init__(self, device, async=True):
        super(MozillaPacketHandler, self).__init__()
        self._quit = threading.Event()
        self._samples = collections.deque(maxlen=20)
        self._device = device
        self._async = async

        if self._async:
            self._packetSize = self.ASYNC_PACKET_SIZE
            # start the thread
            super(MozillaPacketHandler, self).start()
        else:
            self._packetSize = self.SYNC_PACKET_SIZE

    @property
    def sample(self):
        try:
            if not self._async:
                self.processPacket(self._device.getPacket())
            # this is atomic
            return self._samples.popleft()
        except:
            return {}

    # make packet a read-only property
    @sample.setter
    def sample(self, data):
        pass

    def quit(self):
        self._quit.set()
        if self._async:
            super(MozillaPacketHandler, self).join()

    def processPacket(self, data):
        # sanity check
        packetLength = len(data)
        if packetLength != self._packetSize:
            print >> sys.stderr, "Packet is not %d bytes long - %d bytes" % (self._packetSize, packetLength)
            return

	checksum = 0
	for index in range(2, packetLength - 1):
	    checksum = ((checksum + ord(data[index])) & 255)
	checksum = checksum ^ 255
	packetChecksum = ord(data[packetLength - 1])
	if checksum != packetChecksum:
	    print >> sys.stderr, "Packet checksum: %d does not match expected: %d" % (packetChecksum, checksum)
            return
        # unpack the first sample from the packet
        dataPortion = data[5:packetLength-1]
        packetCount = (packetLength - 6) / 8
        for index in range(0, packetCount):
            startIndex = index * 8
            endIndex = startIndex + 8
            sampleBytes = dataPortion[startIndex:endIndex]
            
            # get the current in mA
            # current = int((ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256)) / 10)
            current = ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256)
            if (current > 32767):
                current = (65536 - current) * -1;
            current = current / 10.0 # convert 1/10 mA to mA

            # get the voltage in mV
            voltage = ord(sampleBytes[2]) + (ord(sampleBytes[3]) * 256)
            time = ord(sampleBytes[4]) + (ord(sampleBytes[5]) * 256) + (ord(sampleBytes[6]) * 65536) + (ord(sampleBytes[7]) * 16777216)

            self._samples.append({'current':current, 'voltage':voltage, 'time':time})
            #print "time: ", time


    def run(self):

        while True:
            if self._quit.is_set():
                return

            # get a packet from the device thread
            data = self._device.packet

            # if we didn't get a packet, sleep a little and try again
            if data == None:
                time.sleep(0.0001)
                #print "Sleeping"
                continue

            self.processPacket(data)


class MozillaAmmeter(SampleSource, DeviceManager):
    """ This is a concrete class that interfaces with the Mozilla USB Ammeter
    and implements the SampleSource interface.  It provides sources called
    'current', 'voltage', and 'time'. """

    UNITS = { 'current': 'mA', 'voltage': 'mV', 'time': 'ms' }

    def __init__(self, path, async=True):
        super(MozillaAmmeter, self).__init__()

        # create the threaded device object and get the thread going
        self._async = async
        self._device = MozillaDevice(path, self._async)
        self._handler = MozillaPacketHandler(self._device, self._async)

    @property
    def names(self):
        return ('current','voltage', 'time')

    def getSample(self, names):
        # get a sample
        sample = self._handler.sample

        if sample:
            # pull the requested samples out
            return { name: Sample(sample[name], self.UNITS[name]) for name in names }
        else:
            return None

    def close(self):
        # stop the packet handler thread and wait for it to finish
        self._handler.quit()
        # stop the device handler thread and wait for it to finish
        self._device.quit()

    # FIXME: refactor this to use an ADBDeviceManager mixin eventually
    def startCharging(self, charge_complete):
        pass

    def stopCharging(self):
        pass

    def disconnectUSB(self):
        pass

    def connectUSB(self):
        pass

    def hardPowerOff(self):
        self._device.sendCommand(MozillaDevice.TURN_OFF_BATTERY)

    def hardPowerOn(self):
        self._device.sendCommand(MozillaDevice.TURN_ON_BATTERY)

