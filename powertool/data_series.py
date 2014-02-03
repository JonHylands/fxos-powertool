# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict

class DataSeries(object):

    def __init__(self, name):
        self._name = name
        self._sources = []
        self._data = defaultdict(list)

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def addSource(self, src):
        """ src must be a callable object that returns a single data sample """
        self._sources.append(src)

    def getSample(self):
        """ iterate over the sources getting the next sample from each.
        return a dict with the src names as keys and samples as values. """
        s = {}
        for src in self._sources:
            """ this gets a dict of with names as keys and Sample objecst as values.  one
            for each data source the device can sample """
            samples = src()

            """ merge the two dicts """
            s.update(samples)

            """ add each sample to the data series lists """
            for name, sample in samples.iteritems():
                """ we need to unpack each data sample and store it in the data series """
                self._data[name].append( sample )

        return s
