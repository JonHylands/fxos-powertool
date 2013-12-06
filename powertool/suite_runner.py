# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import importlib
from exceptions import NotImplementedError

class SuiteRunner(object):
    """ This is an abstract base class for running a suite of tests. """

    def beginTest(self):
        """ Begin a run of the current test """
        raise NotImplementedError( "SuiteRunner.beginTest not implemented" )

    def endTest(self):
        """ End a run of the current test """
        raise NotImplementedError( "SuiteRunner.endTest not implemented" )

    def nextTest(self):
        """ Move to the next test in the suite. """
        raise NotImplementedError( "SuiteRunner.nextTest not implemented" )

    def prevTest(self):
        """ Move to the previous test in the suite. """
        raise NotImplementedError( "SuiteRunner.prevTest not implemented" )

