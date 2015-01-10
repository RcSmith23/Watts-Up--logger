#!/usr/bin/env python

# This class will spawn a dacapo benchmark, and record it as
# an instance in the database. 
#
# Only has simple capabilities currently. Runs all the tests 
# sequentially.
# 
# To Do: Allow the choice to run specific set of tests at a time.
# Add in delay to the begginning of each test run.
# Log to the database

import time
import subprocess

class DacapoSuite(object):
    def __init__(self):
        self.delay = 7
        self.dacapo = 'dacapo-9.12-bach.jar'
        self.times = []
        self.processes = []
        self.suite = {0 : 'avrora',
                1 : 'batik',
                2 : 'eclipse',
                3 : 'fop',
                4 : 'h2',
                5 : 'jython',
                6 : 'luindex',
                7 : 'lusearch',
                8 : 'pmd',
                9 : 'sunflow',
                10 : 'tomcat',
                11 : 'tradebeans',
                12 : 'tradesoap',
                13 : 'xalan',
                14 : 'idle' }

    def run(self, tests=['avrora'], sample=None):
        if not sample:
            pass
            #set sample for larger 
        time.sleep(self.delay)
        try:
            for test in tests:
                self.processes << subprocess.Popen(['java', '-jar', 'dacapo-9.12-bach.jar', test])
	except:
            print 'Failed to launch all benchmarks'
            clean(False)
        
        clean()

    def running(self):
        if self.processes.length > 0:
            return True
        else:
            return False

    def clean(self, success=True):
        for p in self.processes:
            pass
            # clean up all processes
        self.processes = []
        if success:
            pass
            # Record times in DB
