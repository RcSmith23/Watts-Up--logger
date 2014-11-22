#!/usr/bin/env python

import time
import subprocess

class DacapoSuite(object):
    def __init__(self):
        self.delay = 7
        self.dacapo = 'dacapo-9.12-bach.jar'
        self.times = []
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
            #set sample for larger size
        processes = []
        time.sleep(self.delay)
        try:
            for test in tests:
                processes << subprocess.Popen(['java', '-jarma']
        
