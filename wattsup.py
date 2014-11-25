#!/usr/bin/env python
"""record data from WattsUp power meter

Reads data from a Watts Up PRO or compatible power meter (http://www.wattsupmeters.com).
Plots in real time, can run in simulation mode, reading from a file rather than
a physical power meter.

Output format will be space sperated containing:
YYYY-MM-DD HH:MM:SS.ssssss n W V A
where n is sample number, W is power in watts, V volts, A current in amps

Usage: "wattsup.py -h" for options

Author: Kelsey Jordahl
Copyright: Kelsey Jordahl 2011
License: GPLv3
Time-stamp: <Tue Sep 20 09:14:29 EDT 2011>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.  A copy of the GPL
    version 3 license can be found in the file COPYING or at
    <http://www.gnu.org/licenses/>.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

"""

import os, serial
import datetime, time
import argparse
import curses
from platform import uname
import numpy as np
import matplotlib.pyplot as plt
import pysftp
import getpass
import sqlite3
import subprocess
import psutil

EXTERNAL_MODE = 'E'
INTERNAL_MODE = 'I'
TCPIP_MODE = 'T'
FULLHANDLING = 2


class WattsUp(object):
    def __init__(self, port):
        if args.sim:
            self.s = open(port,'r')     # not a serial port, but a file
        else:
            self.s = serial.Serial(port, 115200 )
        if args.web:
            self.webserver = True
        else: 
	    self.webserver = None
        self.logfile = None
        self.interval = 1.0
        self.tests = {0 : 'batik',
		1 : 'eclipse',
		2 : 'fop',
		3 : 'h2',
		4 : 'jython',
		5 : 'luindex',
		6 : 'lusearch',
		7 : 'pmd',
		8 : 'sunflow',
		9 : 'tomcat',
		10 : 'tradebeans',
		11 : 'tradesoap',
		12 : 'xalan',
		13 : 'avrora' }

    def benchmark(self, logfile = None):
        print 'Running Benchmarks...'

        line = self.s.readline()
        for i in range(0, 10):   
            n = 0
            if x < 15:
                self.logfile = "Readings/" + self.tests[x]
            else:
                self.logfile = "Readings/" + self.tests[5] + self.tests[29-x]
            dacapo = 'dacapo-9.12-bach.jar'
            proc = None
            proc2 = None
            pid = None
            pid2 = None
            pid_path = None
            pid_path2 = None
            try:
                 fd = open(self.logfile, "w")
            except:
                 print 'Failed to open %s, will not log to file.' % self.logfile
                 self.logfile = False
            
            if x != 0:
                if x < 15:
                    try:
                        proc = subprocess.Popen(['java', '-jar', dacapo, self.tests[x]])
                    except:
                        print 'Failed to launch benchmark %s. Moving on to %s.' % (test, self.tests[x+1])
                        continue
                    pid = proc.pid
                    pid_path = '/proc/' + str(pid)
                else:
                    try:
                        proc = subprocess.Popen(['java', '-jar', dacapo, self.tests[5]])
                        proc2 = subprocess.Popen(['java', '-jar', dacapo, self.tests[29-x]])
                    except:
                        print 'Failed to launch double benchmarks'
                    pid = proc.pid
                    pid2 = proc2.pid
                    pid_path = '/proc/' + str(pid)
                    pid_path2 = '/proc/' + str(pid2)
            else:                
                pid = os.getpid()
                pid_path = '/proc/' + str(pid)
            while (not os.path.exists(pid_path) or not self.procStatus(pid)) \
                    or (not os.path.exists(pid_path2) or not self.procStatus(pid2)):
                if line.startswith( '#d' ):
                    fields = line.split(',')
                    if len(fields)>5:
                        W = float(fields[3]) / 10;
                        V = float(fields[4]) / 10;
                        A = float(fields[5]) / 1000;
                        C = psutil.cpu_percent(1)
                        M = psutil.virtual_memory()[2]
                        
                        if self.logfile:
                            fd.write('%s %d %3.1f %3.1f %5.3f %3.1f %3.1f\n' % (datetime.datetime.now(), n, W, V, A, C, M))
                        if not os.path.exists(pid_path) or not self.procStatus(pid):
                            if x < 15:
                                break
                            else:
                                    break;
                        n += self.interval                     
                line = self.s.readline()
            n += self.interval
            for i in range(0, 10):
                if line.startswith( '#d' ):
                    if args.raw:
                        r.write(line)
                    fields = line.split(',')
                    if len(fields)>5:
                        W = float(fields[3]) / 10;
                        V = float(fields[4]) / 10;
                        A = float(fields[5]) / 1000;
                        C = psutil.cpu_percent(1)
                        M = psutil.virtual_memory()[2]
                        if self.logfile:
                            fd.write('%s %d %3.1f %3.1f %5.3f %3.1f %3.1f\n' % (datetime.datetime.now(), n, W, V, A, C, M))
                line = self.s.readline()
                n += self.interval
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        try:
            fd.close()
        except:
            pass
        if args.raw:
            try:
                r.close()
            except:
                pass

    def transfer(self, passwrd):
        try:
            sftp = pysftp.Connection("aras", username="rsmith23", password=passwrd)
        except:
            print "Failed to connect to web server."
            self.webserver = None
        if self.webserver:
            info = uname()
            sftp.cwd('Documents/Cluster');
            if not sftp.isdir(info[1]):
                sftp.mkdir(info[1], mode=777)
            sftp.cwd(info[1])

                if i < 15:
                    test_file = 'Readings/' + self.tests[i]
                else:
                    test_file = 'Readings/' + self.tests[] + self.tests[]
                try:
                    sftp.put(test_file)
                except:
                    print 'Failed to transfer log file'
        try:
            sftp.close()
        except:
            pass

    #Returns False if process is a zombie, otherwise True
    def procStatus(self, pid):
        for line in open("/proc/%d/status" % pid).readlines():
            if line.startswith("State:"):
                values = line.split(":", 1)[1].strip().split(' ')[0]
                if values[0] == 'Z':
                    return False
                else:
                    return True

def main(args):
    if not args.port:
        system = uname()[0]
        if system == 'Darwin':          # Mac OS X
            args.port = '/dev/tty.usbserial-A1000wT3'
        elif system == 'Linux':
            args.port = '/dev/ttyUSB0'
    if not os.path.exists(args.port):
        print 'Could not open wattsup logger'
        exit()
    if args.web:
         meter.passwd = getpass.getpass('Webserver password: ')

    meter = WattsUp(args.port, args.interval)
    if args.bench:
        meter.benchmark(args.outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from Watts Up power meter.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose')
    parser.add_argument('-l', '--log', dest='log', action='store_true', help='log data in real time')
    parser.add_argument('-w', '--weblog', dest='web', action='store_true', default=None, help='log data to webserver')
    parser.add_argument('-b', '--benchmark', dest='bench', action='store_true', default=None, help='Run and record Dacapo')
    args = parser.parse_args()
    main(args)
