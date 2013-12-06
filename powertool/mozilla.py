# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from sample_source import SampleSource
from device_manager import DeviceManager
from sample import Sample

# the name of the SampleSource class to use
SampleSourceClass = 'MozillaAmmeter'

class MozillaAmmeter(SampleSource, DeviceManager):
    """ This is a concrete class that interfaces with the Mozilla USB Ammeter
    and implements the SampleSource interface.  It provides a source called
    'current' that delivers DC current samples in mA. """

    def __init__(self):
        super(MozillaAmmeter, self).__init__()

    @property
    def names(self):
        """ We only provide 'current' samples """
        return ('current',)

    def getSample(self, name):
        if name != 'current':
            raise ValueError( "MozillaAmmeter only provides 'current' samples" )

        return Sample(0, 'mA')

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

