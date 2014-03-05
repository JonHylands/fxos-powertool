# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from math import sqrt,fsum,pow


class Statistics(object):

    def __init__(self, data=[[]]):
        # flatten 2d-array and convert to float
        for x in data:
            self._data = [float(d) for d in x]

    @property
    def mean(self):
        if hasattr(self, '_mean'):
            return self._mean

        s = fsum(self._data)
        self._mean = s / float(len(self._data))
        return self._mean

    @property
    def minimum(self):
        if hasattr(self, '_minimum'):
            return self._minimum

        self._minimum = None
        for d in self._data:
            if d < self._minimum or self._minimum is None:
                self._minimum = d

        return self._minimum

    @property
    def maximum(self):
        if hasattr(self, '_maximum'):
            return self._maximum

        self._maximum = None
        for d in self._data:
            if d > self._maximum or self._maximum is None:
                self._maximum = d

        return self._maximum
    
    @property
    def variance(self):
        if hasattr(self, '_variance'):
            return self._variance

        m = self.mean
        sqdiffs = []
        for d in self._data:
            diff = d - m
            sqdiffs.append(pow(diff, 2))

        s = fsum(sqdiffs)
        self._variance = s / float(len(sqdiffs))
        return self._variance
        
    @property
    def std(self):
        if hasattr(self, '_std'):
            return self._std

        v = self.variance
        self._std = sqrt(v)
        return self._std

    # make all properties read-only
    @mean.setter
    def mean(self, v):
        pass

    @minimum.setter
    def minimum(self, v):
        pass

    @maximum.setter
    def maximum(self, v):
        pass

    @variance.setter
    def variance(self, v):
        pass

    @std.setter
    def std(self, v):
        pass


