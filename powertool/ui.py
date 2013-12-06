# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import importlib
from exceptions import NotImplementedError

class UI(object):
    """ This is an abstract base class for UI creation and running. """

    @classmethod
    def create(cls, ui, suite, show):
        try:
            # import the module
            m = importlib.import_module('.'.join(['powertool', ui.lower() + "_ui"]))

            # get the name of the UI subclass
            uicls = getattr(m, 'UIClass')

            # get the sample displayer class
            ctor = getattr(m, uicls)

        except:
            raise Exception("Unsupported UI: %s" % ui)

        # create an instance, do this outside of the try/except
        # because we want any UI errors to be reported directly...
        return ctor(suite, show)

    def run(self):
        """ Enter the main run loop for the UI. """
        raise NotImplementedError( "UI.run not implemented" )

