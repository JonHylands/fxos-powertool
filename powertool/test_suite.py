# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict
import json
import magic

from data_series import DataSeries
from sample_source import SampleSource, Sampler

class TestSuite(object):

    @classmethod
    def create(cls, in_file):
        if in_file == None:
            # return an empty TestRun if we're just looking at live samples
            return cls( "FxOS Powertool", ['Null Test'] )

        mime = magic.from_file( in_file, mime=True )
        if mime == 'text/plain':
            if in_file.endswith('json'):
                return cls.fromJSON( in_file )

        raise ValueError( "unsupported test run config file format" )


    @classmethod
    def fromJSON(cls, json_file_path):
        """ creates an instance of TestRun configured with the data from a JSON file.  The config
        file should look like:

        {
            "title": "Title of Test Run",
            "tests": [
                "first test",
                "second test",
                "third"
            ]
        }
        """
        json_file = open(json_file_path, 'r')
        json_data = json.load(json_file)
        json_file.close()

        if json_data.has_key('title') and json_data.has_key('tests'):
            return cls( **json_data )

        raise KeyError( "test run config file must have title and tests as top level keys" )

    def __init__(self, title, tests):
        """ initializes the TestRun instance with the title an tests """

        if not (isinstance(title, str) or isinstance(title, unicode)) or not isinstance(tests, list):
            raise TypeError("title must be a string, tests must be a list")

        self._title = title
        self._tests = tests
        self._current_test = None
        self._data = defaultdict(list)
        self._sources = []

    @property
    def title(self):
        return self._title

    @property
    def tests(self):
        return self._tests

    @property
    def data(self):
        return self._data

    @property
    def testRunning(self):
        return self._current_test != None

    def addSource(self, source):
        if not isinstance(source, SampleSource):
            raise TypeError("source must be an instance of SampleSource")
        self._sources.append(source)

    def startTest(self, test_name):
        if not test_name in self._tests:
            raise KeyError( "unknown test name" )

        if self.testRunning:
            raise RuntimeError( "test is already running" )

        # create the new DataSeries
        self._current_test = DataSeries(test_name)

        # add all of the source to the DataSeries
        for src in self._sources:
            for name in src.names:
                sampler = Sampler( name, src )
                self._current_test.addSource( name, sampler )

    def getSample(self):
        if not self.testRunning:
            raise RuntimeError( "test is not running" )

        # tell the DataSeries to take another sample
        return self._current_test.getSample()

    def stopTest(self):
        if not self.testRunning:
            raise RuntimeError( "test is not running" )

        # store the DataSeries in the accumulated data store
        name = self._current_test.name
        self._data[name].append(self._current_test)
        self._current_test = None

