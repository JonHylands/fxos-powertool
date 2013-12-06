# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from exceptions import NotImplementedError

class DeviceManager(object):
    """ This is an abstract base class for managing hardware test devices (e.g. mobile phones). """

    def startCharging(self, charge_complete):
        """ Start charging the device and callable to execute when charging is complete. """
        raise NotImplementedError( "DeviceManager.startCharging not implemented" );

    def stopCharging(self):
        """ Stop charging the device. """
        raise NotImplementedError( "DeviceManager.stopCharging not implemented" );

    def disconnectUSB(self):
        """ Disconnect the USB connection from the device """
        raise NotImplementedError( "DeviceManager.disconnectUSB not implemented" );

    def connectUSB(self):
        """ Connect the USB connection to the device """
        raise NotImplementedError( "DeviceManager.connectUSB not implemented" );

    def hardPowerOff(self):
        """ Disconnects the battery from the device """
        raise NotImplementedError( "DeviceManager.hardPowerOff not implemented" );

    def hardPowerOn(self):
        """ Connects the battery to the device """
        raise NotImplementedError( "DeviceManager.hardPowerOn not implemented" );

