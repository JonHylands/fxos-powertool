# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import importlib
from exceptions import NotImplementedError

class SampleSource(object):
    """ This is an abstract base class for sources of data samples. All sources
    of data samples should derive from, and implement the interface of, this class. """

    @classmethod
    def create(cls, device):
        try:
            # import the module
            m = importlib.import_module('.'.join(['powertool',device]))

            # get the name of the sample source class
            sscls = getattr(m, 'SampleSourceClass')

            # get the sample source class
            ctor = getattr(m, sscls)

            # create an instance
            return ctor()

        except:
            raise Exception("Unsupported device: %s" % device)

    @property
    def names(self):
        """ We only provide 'current' samples """
        return ('current',)

    def getSample(self, name):
        """ Return the next sample from the source with the given name """
        raise NotImplementedError( "SampleSource.getSample not implemented" )


class Sampler(object):
    """ Functor that binds a named source and a reference to a SampleSoruce.getSample
    into a callable object that can be used anonymously to get the next sample from
    the SampleSource. """

    def __init__(self, name, source):
        self._name = name
        self._source = source

    def __call__(self):
        return self._source.getSample(self._name)

