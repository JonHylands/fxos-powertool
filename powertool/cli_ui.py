# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from ui import UI
from suite_runner import SuiteRunner

# The name of the SampleDisplayer class to use
UIClass = "CLIUI"

class CLIUI(UI, SuiteRunner):

    def __init__(self, suite, show=None):
        super(CLIUI, self).__init__()
        self._suite = suite
        self._show = show

    def run(self):
        pass

    def startTest(self):
        pass

    def stopTest(self):
        pass

    def nextTest(self):
        pass

    def prevTest(self):
        pass

