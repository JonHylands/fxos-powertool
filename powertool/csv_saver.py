# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict
import csv
import os
import shutil
from math import sqrt

from test_suite import TestSuite
from test_suite_saver import TestSuiteSaver
from statistics import Statistics

# the name of the TestRunSaver class to use
TestSuiteSaverClass = 'CSVSaver'

class CSVSaver(TestSuiteSaver):
    """ Outputs the data in a TestSuite object in CSV format.  It creates
    a directory and outputs each test as a .csv file in the directory.
    Inside the .csv file for each test, the data from every run of the test
    is stored as a column.  If normalize is True, then the data for each 
    test will be trimmed so that the number of samples in each run of
    the test is the same. """

    def __init__(self, out_file_path):
        super(CSVSaver, self).__init__()
        self._path = out_file_path

    def _createDir(self):
        # trim .csv off
        self._dir = self._path[:-4]

        try:
            # create the directory
            os.mkdir(self._dir)
        except:
            # clear out previous tree and try again
            shutil.rmtree(self._dir)
            os.mkdir(self._dir)

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

        """ at this point we have:
        {
                sensor1: [
                    [ sampleA, sampleB, sampleC, ... ],
                    [ sampleD, sampleE, sampleF, ... ],
                    ...
                ],
                ...
        }

        what we want is:
        {
                sensor1: [
                    [ sampleA, sampleD ],
                    [ sampleB, sampleE ],
                    [ sampleC, sampleF ],
                    ...
                ],
                ...
        }

        the data needs to be in column-major order with each
        column containing the data for each run

        """

        # first step is to pad out each of the shorter runs with
        # zeros so that the runs all have the same number of samples

        groups = []
        runs = 0
        sensors = 0
        for sensor, rows in agg.iteritems():

            sensors += 1

            # find the length of the longest data run
            largest_dim = 0
            for row in rows:
                if len(row) > largest_dim:
                    largest_dim = len(row)

            # pad out the rest of the data runs
            padded = []
            runs = len(rows)
            for row in rows:
                row = [sensor] + row
                if len(row) < largest_dim:
                    row.extend([0] * (largest_dim - len(row)))
                padded.append(row)

            groups.append(padded)


        """
        we now have this:
        [
          [
            [ 'current', sample, sample, sample, ... ],
            [ 'current', sample, sample, sample, ... ]
          ],
          [
            [ 'time', sample, sample, sample, ... ],
            [ 'time', sample, sample, sample, ... ]
          ],
          [
            [ 'voltage', sample, sample, sample, ... ],
            [ 'voltage', sample, sample, sample, ... ]
          ]
        ]

        what we want is for the rows for each test run to 
        be adjacent in the array:
        [
          [ 'current', sample, sample, sample, ... ],
          [ 'time', sample, sample, sample, ... ],
          [ 'voltage', sample, sample, sample, ... ],
          [ 'current', sample, sample, sample, ... ],
          [ 'time', sample, sample, sample, ... ],
          [ 'voltage', sample, sample, sample, ... ]
        ]
        """
        reordered = []
        for i in range(0, runs):
            for j in range(0, sensors):
                reordered.append( groups[j][i] )

        # now transpose everything
        data = zip(*reordered)

        return data, units

    def save(self, suite):
        # create the directory for the .csv files
        self._createDir()

        series = suite.data

        for series_name, data_series in series.iteritems():

            # clean up the series name into a better filename
            nice_name = series_name.replace(',', '').replace(' ', '_')
            csv_path = os.path.join(self._dir, nice_name + '.csv')

            # get the aggregate data
            data, units = self._aggregate(data_series)

            print "saving to: %s" % csv_path

            # write the csv file
            with open(csv_path, 'wb') as csv_file:

                # create csv writer in excel dialect (i.e. comma delimeter, 
                # double quote field quoting)
                csv_writer = csv.writer(csv_file, dialect='excel')

                # FIXME: Statistics is now broken since the data has been
                # changed to be column-major
                # calculate and write out basic statistics from the data
                #stats = Statistics(data)
                #csv_writer.writerow(['mean', stats.mean])
                #csv_writer.writerow(['std dev', stats.std])
                #csv_writer.writerow(['min', stats.minimum])
                #csv_writer.writerow(['max', stats.maximum])

                # write out rows of raw data
                for row in data:
                    csv_writer.writerow(row)

