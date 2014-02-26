# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import importlib
from exceptions import NotImplementedError, Exception

class SampleSourceError(Exception):
    """ Base class for all SampleSource errors """
    def __init__(self, msg):
        super(SampleSourceError, self).__init__(msg)

class SampleSourceNoDeviceError(SampleSourceError):
    """ Error raised when the specified device is not present """
    def __init__(self, msg):
        super(SampleSourceNoDeviceError, self).__init__(msg)


class SampleSource(object):
    """ This is an abstract base class for sources of data samples. All sources
    of data samples should derive from, and implement the interface of, this class. """

    @classmethod
    def create(cls, devices, path):
        for device in devices:
            try:
                # import the module
                m = importlib.import_module('.'.join(['powertool',device]))

                # get the name of the sample source class
                sscls = getattr(m, 'SampleSourceClass')

                # get the sample source class
                ctor = getattr(m, sscls)

                # create an instance
                return ctor(path)

            except SampleSourceNoDeviceError, d:
                #print "No %s devices found" % d
                pass

            except NameError:
                raise Exception("Unsupported device: %s" % device)

            except Exception, e:
                classname = str(type(e))[:-2].split('.')[-1]
                raise Exception("Failed to load: %s (REASON: %s -- %s)" % (device, classname, str(e)))

        raise Exception("No Mozilla or Yocto devices found")

    @property
    def names(self):
        """ Return the names of the data sources (e.g. 'current', 'voltage', etc) """
        raise NotImplementedError( "SampleSource.names not implemented" )

    def getSample(self, name):
        """ Return the next sample from the source with the given name """
        raise NotImplementedError( "SampleSource.getSample not implemented" )

    def close(self):
        """ Release any resources associated with collecting samples """
        raise NotImplementedError( "SampleSource.close not implemented" )


class Sampler(object):
    """ Functor that binds a named source and a reference to a SampleSoruce.getSample
    into a callable object that can be used anonymously to get the next sample from
    the SampleSource. """

    def __init__(self, names, source):
        self._names = names
        self._source = source

    def __call__(self):
        return self._source.getSample(self._names)

