# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict
import json

from test_suite import TestSuite
from test_suite_saver import TestSuiteSaver
from statistics import Statistics

# the name of the TestRunSaver class to use
TestSuiteSaverClass = 'JSONSaver'

class JSONSaver(TestSuiteSaver):
    """ Outputs the data in a TestRun object in JSON format. """

    def __init__(self, out_file_path):
        super(JSONSaver, self).__init__()
        self._path = out_file_path

    def _aggregate(self, series):
        agg = defaultdict(list)
        units = defaultdict()

        for s in series:
            for sensor, samples in s.data.iteritems():
                row = []
                unt = None
                for sample in samples:
                    row.append(sample.value)
                    if unt == None:
                        unt = sample.units
                agg[sensor].append(row)
                units[sensor] = unt

        for sensor, rows in agg.iteritems():
            trimmed = []

            # find the shortest row 
            smallest_dim = -1
            for row in rows:
                if smallest_dim < 0:
                    smallest_dim = len(row)
                elif len(row) < smallest_dim:
                    smallest_dim = len(row)

            # store trimed lists of samples
            for row in rows:
                trimmed.append(row[:smallest_dim])

            agg[sensor] = trimmed

        return agg, units

    def save(self, suite):
        output = { 'series':[] }
        series = suite.data

        for series_name, data_series in series.iteritems():

            series = { 'name': series_name, 'sensors':[] }
            
            # get the aggregate data
            agg, units = self._aggregate(data_series)

            # now write out the csv
            for sensor_name, data in agg.iteritems():

                # calculate and save basic statistics
                stats = Statistics(data)
                sensor = { 'name': sensor_name,
                           'units': units[sensor_name],
                           'mean': stats.mean,
                           'std dev': stats.std,
                           'min': stats.minimum,
                           'max': stats.maximum,
                           'data': data }

                series['sensors'].append(sensor)

            output['series'].append(series)

        with open(self._path, 'wb') as json_file:
            json.dump(output, json_file, indent=1)

