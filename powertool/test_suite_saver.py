# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import importlib

from test_suite import TestSuite

class TestSuiteSaver(object):
    """ This is an abstract base class for saver object that translate
    TestSuite objects into some serialized output """

    @classmethod
    def create(cls, out_file_path):
        try:
            # import the module
            if out_file_path == None:
                ext = "null"
            else:
                ext = out_file_path.split('.')[-1]
            m = importlib.import_module('.'.join(['powertool', ext.lower() + '_saver']))

            # get the name of the saver class
            scls = getattr(m, 'TestSuiteSaverClass')

            # get the saver class
            ctor = getattr(m, scls)

            return ctor(out_file_path)

        except:
            raise Exception("Unsupported output file type: %s" % ext)

    def save(self, testrun):
        raise NotImplementedError( "TestRunSaver.save not implemented" )

