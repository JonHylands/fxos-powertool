# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

class Sample(object):

    def __init__(self, value, units=None):
        self._value = value
        self._units = units
        self._tstamp = time.mktime(time.gmtime())

    @property
    def value(self):
        return self._value

    @property
    def units(self):
        return self._units

    @property
    def timestamp(self):
        return self._tstamp

