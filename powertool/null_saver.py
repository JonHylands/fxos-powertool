# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from test_suite import TestSuite
from test_suite_saver import TestSuiteSaver

# the name of the TestRunSaver class to use
TestSuiteSaverClass = 'NullSaver'

class NullSaver(TestSuiteSaver):
    """ Doesn't output any data. """

    def __init__(self, out_file_path):
        super(NullSaver, self).__init__()

    def save(self, suite, normalize=False):
        series = suite.data

        for series_name, data_series in series.iteritems():
            print "Test: %s" % series_name
            print "\tRuns: %d" % len(data_series)

            for series in data_series:
                print "\t\tSensors: %d" % len(series.data.keys())

                for sensor, samples in series.data.iteritems():
                    print "\t\t\tSensor: %s" % sensor
                    print "\t\t\tSamples: %d" % len(samples)

