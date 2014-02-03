# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict

from yoctopuce.yocto_api import YAPI, YRefParam, YModule
from yoctopuce.yocto_current import YCurrent

from sample_source import SampleSource
from device_manager import DeviceManager
from sample import Sample

# the name of the SampleSource class to use
SampleSourceClass = 'YoctoAmmeter'

class YoctoDevice(object):

    @property
    def module(self):
        if hasattr(self, '_module') and self._module:
            return self._module

        # need to verify that the yocto device is attached
        errmsg = YRefParam()
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            raise Exception('could not register yocto usb connection')
        sensor = YCurrent.FirstCurrent()
        if sensor is None:
            raise Exception('could not find yocto ammeter device')
        if sensor.isOnline():
            self._module = sensor.get_module()
        return self._module

    @property
    def beacon(self):
        return self._module.get_beacon()

    @beacon.setter
    def beacon(self, value):
        if value:
            self._module.set_beacon(YModule.BEACON_ON)
        else:
            self._module.set_beacon(YModule.BEACON_OFF)


class YoctoAmmeter(YoctoDevice, SampleSource, DeviceManager):
    """ This is a concrete class that interfaces with the Yoctopuce USB Ammeter
    and implements the SampleSource interface.  It provides a source called
    'current' that delivers DC current samples in mA. """

    def __init__(self, path):
        super(YoctoAmmeter, self).__init__()
        self._delivery = defaultdict(list)

    @property
    def sensor(self):
        if hasattr(self, '_sensor') and self._sensor:
            return self._sensor

        # get a handle to the ammeter sensor
        self._sensor = YCurrent.FindCurrent(self.module.get_serialNumber() + '.current1')
        if not self.module.isOnline() or self._sensor is None:
            raise Exception('could not get sensor device')
        return self._sensor

    @property
    def names(self):
        """ We only provide 'current' samples """
        return ('current',)

    def getSample(self, names):
        for name in names:
            if name not in self.names:
                raise ValueError( "YoctoAmmeter only provides 'current' samples" )

        # return a Sample with the current value from the ammeter sensor
        return { name: Sample( self.sensor.get_currentValue(), 'mA' ) }

    def close(self):
        pass

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
        pass

    def hardPowerOn(self):
        pass

