#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import argparse

from sample_source import SampleSource
from test_suite import TestSuite
from test_suite_saver import TestSuiteSaver
from ui import UI

def main():
    
    try:
        # set up and parse arguments
        parser = argparse.ArgumentParser(description='Mozilla Powertool')
        parser.add_argument('-d', '--device', type=str,  default=['mozilla','yocto'], 
                            choices=['yocto','mozilla'], action='append',
                            help="specify ammeter device to use")
        parser.add_argument('-p', '--path', type=str, default=None,
                            help="specify path to ammeter device (e.g. /dev/ttyACM0)")
        parser.add_argument('-u', '--ui', type=str, required=True,
                            choices=['tk','cli'], default='cli', help="specify which UI to use")
        parser.add_argument('-f', '--file', type=str,  default=None, help="test run config file")
        parser.add_argument('-o', '--out', type=str, default=None, help="output data file")
        parser.add_argument('-s', '--show', type=str, default=None, help="name of the sample source to display")
        args = parser.parse_args()

        # create the sample source
        source = SampleSource.create( args.device, args.path )
        
        # create the test suite
        suite = TestSuite.create( args.file )

        # add the sample source
        suite.addSource( source )

        # create the saver
        saver = TestSuiteSaver.create( args.out )

        # create the displayer
        ui = UI.create( args.ui, suite, args.show )

        # run the app
        ui.run()

        # save the data
        saver.save( suite )

        # shut down the sample source
        source.close()
        
        sys.exit(0)

    except Exception, e:
        print("\nERROR: %s\n" % e)
        parser.print_help()
        sys.exit(1)

