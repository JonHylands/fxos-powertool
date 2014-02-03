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

# the name of the SampleSource class to use
SampleSourceClass = 'MozillaAmmeter'

SAMPLE_RATE = 100
SAMPLE_TIME = 1000 / SAMPLE_RATE

class MozillaDevice(threading.Thread):

    BAUD = 1000000
    TIMEOUT = 1
    RESPONSE_SIZE = 86

    # commands
    SET_ID = bytearray.fromhex("ff ff 01 02 01 FB")
    START_ASYNC = bytearray.fromhex("ff ff 01 02 02 FA")
    STOP_ASYNC = bytearray.fromhex("ff ff 01 02 03 F9")
    TURN_OFF_BATTERY = bytearray.fromhex("ff ff 01 02 05 F7") #TURN_OFF_BATTERY
    TURN_ON_BATTERY = bytearray.fromhex("ff ff 01 02 06 F6") #TURN_ON_BATTERY

    def __init__(self, path):
        super(MozillaDevice, self).__init__()
        self._path = path
        self._cmds = Queue.Queue()
        self._quit = threading.Event()
        self._packets = collections.deque(maxlen=10)
        self._module = serial.Serial(port=self._path, baudrate=self.BAUD, timeout=self.TIMEOUT)

        # start the thread
        super(MozillaDevice, self).start()

    def sendCommand(self, cmd):
        """ adds a command to the command queue """
        self._cmds.put_nowait(cmd)

    @property
    def packet(self):
        try:
            # this is atomic
            return self._packets.popleft()
        except:
            return None

    # make packet a read-only property
    @packet.setter
    def packet(self, data):
        pass

    def quit(self):
        # send STOP_ASYNC command to wake up the worker thread, if needed
        self.sendCommand(self.STOP_ASYNC)

        # set the quit flag, all remaining commands will be processed before
        # the thread function exits
        self._quit.set()

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
            self._packets.append( self._module.read(self.RESPONSE_SIZE) )


class MozillaPacketHandler(threading.Thread):

    def __init__(self, device):
        super(MozillaPacketHandler, self).__init__()
        self._quit = threading.Event()
        self._samples = collections.deque(maxlen=20)
        self._device = device

        # start the thread
        super(MozillaPacketHandler, self).start()

    @property
    def sample(self):
        try:
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
        super(MozillaPacketHandler, self).join()

    def run(self):

        while True:
            if self._quit.is_set():
                return

            # get a packet from the device thread
            data = self._device.packet

            # if we didn't get a packet, sleep a little and try again
            if data == None:
                time.sleep(0.1)
                continue

            # sanity check
            packetLength = len(data)
            if packetLength != 86:
                print >> sys.stderr, "Packet is not 86 bytes long - %d bytes" % packetLength
                continue

            # unpack the first sample from the packet
            dataPortion = data[5:packetLength-1]
            for index in range(0, 10):
                startIndex = index * 8
                endIndex = startIndex + 8
                sampleBytes = dataPortion[startIndex:endIndex]
                
                # get the current in mA
                current = int(ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256) / 10)
                if (current > 32767):
                    current = (65536 - current) * -1;

                # get the voltage in mV
                voltage = ord(sampleBytes[2]) + (ord(sampleBytes[3]) * 256)

                self._samples.append({'current':current, 'voltage':voltage })


class MozillaAmmeter(SampleSource, DeviceManager):
    """ This is a concrete class that interfaces with the Mozilla USB Ammeter
    and implements the SampleSource interface.  It provides sources called
    'current', 'voltage', and 'time'. """

    UNITS = { 'current': 'mA', 'voltage': 'mV', 'time': 'ms' }

    def __init__(self, path):
        super(MozillaAmmeter, self).__init__()

        # create the threaded device object and get the thread going
        self._device = MozillaDevice(path)
        self._handler = MozillaPacketHandler(self._device)

    @property
    def names(self):
        #return ('current','voltage','time')
        return ('current','voltage')

    def getSample(self, names):
        # get a sample
        sample = self._handler.sample

        # pull the requested samples out
        return { name: Sample(int(sample[name]), self.UNITS[name]) for name in names }

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

