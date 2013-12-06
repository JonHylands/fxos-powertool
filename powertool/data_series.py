# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict

class DataSeries(object):

    def __init__(self, name):
        self._name = name
        self._src = {}
        self._data = defaultdict(list)

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def addSource(self, name, src):
        """ src must be a callable object that returns a single data sample """
        self._src[name] = src

    def getSample(self):
        """ iterate over the sources getting the next sample from each.
        return a dict with the src names as keys and samples as values. """
        s = {}
        for name, src in self._src.iteritems():
            sample = src()
            self._data[name].append( sample )
            s[name] = sample

        return s
