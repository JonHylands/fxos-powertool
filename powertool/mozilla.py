# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import collections
import Queue
import serial
import threading
import time

from sample_source import SampleSource
from device_manager import DeviceManager
from sample import Sample
from time_utils import now_in_millis

# the name of the SampleSource class to use
SampleSourceClass = 'MozillaAmmeter'

SAMPLE_RATE = 25
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
        self._queue = Queue.Queue()
        self._quit = threading.Event()
        self._sampling = threading.Event()
        self._samples = collections.deque(maxlen=10)
        self._module = serial.Serial(port=self._path, baudrate=self.BAUD, timeout=self.TIMEOUT)

        # start the thread
        super(MozillaDevice, self).start()


    @property
    def module(self):
        if hasattr(self, '_module') and self._module:
            return self._module

        return None

    def sendCommand(self, cmd):
        """ adds a command to the command queue """
        self._queue.put_nowait(cmd)

    @property
    def isSampling(self):
        return self._sampling.is_set()

    @property
    def sample(self):
        try:
            # this is atomic
            return self._samples.popleft()
        except:
            return {}

    # make sample a read-only property
    @sample.setter
    def sample(self, data):
        pass

    def quit(self):
        # set the quit flag, all remaining commands will be processed before
        # the thread function exits
        self._quit.set()

        # send STOP_ASYNC command to wake up the worker thread, if needed
        self.sendCommand(self.STOP_ASYNC)

        # join the thread and wait for the thread function to exit
        super(MozillaDevice, self).join()

        # when we get here, the thread has stopped so close the serial port
        self._module.close()

    def run(self):
        """ This is run in a separate thread """

        while True:
            s1 = now_in_millis()
            try:
                # try to get a command to process...
                if self._sampling.is_set():
                    # don't wait for a command
                    cmd = self._queue.get_nowait()
                else:
                    # block waiting for a command
                    cmd = self._queue.get( True )
                    s1 = now_in_millis()

                self.module.write(cmd)
                self.module.flush()
                # mark the command as processed
                self._queue.task_done()

                if cmd == self.START_ASYNC:
                    self._sampling.set()
                elif cmd == self.STOP_ASYNC:
                    self._sampling.clear()

            except Queue.Empty:
                # if we're sampling and there are no queued commands, the get_nowait()
                # causes an exception and execution resumes here
                pass

            if self._queue.empty() and self._quit.is_set():
                # time to quit
                return

            if self._sampling.is_set():
                #print "reading data from module"
                # read any data from the device
                data = self.module.read(self.RESPONSE_SIZE)

                packetLength = len(data)
                if packetLength != 86:
                    print 'Packet is not 86 bytes long - {} bytes'.format(packetLength)
                    return

                dataPortion = data[5:packetLength-1]
                for index in range(0, 10):
                    startIndex = index * 8
                    endIndex = startIndex + 8
                    sampleBytes = dataPortion[startIndex:endIndex]
                    # get the current in mA
                    current = int(ord(sampleBytes[0]) + (ord(sampleBytes[1]) * 256) / 10)
                    if (current > 32767):
                        current = (65536 - current) * -1;
                    voltage = ord(sampleBytes[2]) + (ord(sampleBytes[3]) * 256)
                    #msCounter = ord(sampleBytes[4]) + (ord(sampleBytes[5]) * 256) + (ord(sampleBytes[6]) * 65536) + (ord(sampleBytes[7]) * 16777216)

                    # this is atomic
                    self._samples.append({'current':current, 'voltage':voltage })

            elapsed = int(now_in_millis() - s1)
            waitTime = max(SAMPLE_TIME - elapsed, 1)
            if waitTime > 0:
                time.sleep(waitTime / 1000)


class MozillaAmmeter(SampleSource, DeviceManager):
    """ This is a concrete class that interfaces with the Mozilla USB Ammeter
    and implements the SampleSource interface.  It provides sources called
    'current', 'voltage', and 'time'. """

    UNITS = { 'current': 'mA', 'voltage': 'mV', 'time': 'ms' }

    def __init__(self, path):
        super(MozillaAmmeter, self).__init__()

        # create the threaded device object and get the thread going
        self._device = MozillaDevice(path)

    @property
    def names(self):
        #return ('current','voltage','time')
        return ('current','voltage')

    def getSample(self, names):
        for name in names:
            if name not in self.names:
                raise ValueError( "MozillaAmmeter only provides 'current', 'voltage', and 'time' samples" )

        if not self._device.isSampling:
            self._device.sendCommand(MozillaDevice.START_ASYNC)

        # get a sample
        sample = self._device.sample

        # pull the requested samples out
        samples = {}
        for name in names:
            if sample.has_key(name):
                samples[name] = Sample(int(sample[name]), self.UNITS[name])

        return samples

    def close(self):
        # stop the thread and wait for everything to finish
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
        self.sendCommand(MozillaDevice.TURN_OFF_BATTERY)

    def hardPowerOn(self):
        self.sendCommand(MozillaDevice.TURN_ON_BATTERY)

