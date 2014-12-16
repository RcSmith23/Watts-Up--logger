#!/usr/bin/env python
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

class WattsUp(object):
    def __init__(self, port, interval):
        self.s = serial.Serial(port, 115200 )
        if args.web:
            self.webserver = True
        else: 
	    self.webserver = None
        self.logfile = None
        self.machine_file = 'Readings/' + uname()[1]
        self.interval = interval
        # initialize lists for keeping data
        self.t = []
        self.power = []
        self.potential = []
        self.current = []
        self.cpu = []
        self.mem = []
        self.tests = {
		0 : 'idle',
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
		14 : 'avrora' }

    def benchmark(self):
        print 'Running Benchmarks...'
        line = self.s.readline()
        n = 0
        self.logfile = "Readings/" + self.tests[args.bench]
        dacapo = 'dacapo-9.12-bach.jar'
        proc = None
        try:
            fd = open(self.logfile, "w")
        except:
            print 'Failed to open %s, will not log to file.' % self.logfile
            self.logfile = False
        
        if args.bench != 0:
            try:
                proc = [subprocess.Popen(['java', '-jar', dacapo, self.tests[self.bench]]) for _ in range(4)]
            except:
                print 'Failed to launch benchmark.'
        while True:
            if line.startswith( '#d' ):
                fields = line.split(',')
                if len(fields)>5:
                    W = float(fields[3]) / 10;
                    V = float(fields[4]) / 10;
                    A = float(fields[5]) / 1000;
                    C = psutil.cpu_percent(1)
                    M = psutil.virtual_memory()[2]
                    c = screen.getch()
                    if self.logfile:
                        fd.write('%s %d %3.1f %3.1f %5.3f %3.1f %3.1f\n' % (datetime.datetime.now(), n, W, V, A, C, M))
            if args.bench == 0 and n >= 30:
                break
            ps_status = [p.poll() for p in proc]
            if all([x is not None for x in ps_status]):
                break
            n += self.interval         
            line = self.s.readline()
        try:
            fd.close()
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
            test_file = 'Readings/' + self.tests[i] + '4'
            try:
                sftp.put(test_file)
            except:
                print 'Failed to transfer log file'
            machine_file = 'Readings/' + info[1]
            try:
                sftp.put(machine_file)
            except:
                print "Failed to transfer machine file."
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
    args.interval = 1
    if not args.port:
        system = uname()[0]
        if system == 'Darwin':          # Mac OS X
            args.port = '/dev/tty.usbserial-A1000wT3'
        elif system == 'Linux':
            args.port = '/dev/ttyUSB0'
    if not os.path.exists(args.port):
        print ''
        print 'File %s does not exist.' % args.port
    if args.web:
        passwd = getpass.getpass('Webserver password: ')
    meter = WattsUp(args.port, args.interval)
    if args.bench:
        meter.benchmark()
    if args.web:
         meter.transfer(passwd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from Watts Up power meter.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose')
    parser.add_argument('-l', '--log', dest='log', action='store_true', help='log data in real time')
    parser.add_argument('-p', '--port', dest='port', default=None, help='USB serial port')
    parser.add_argument('-w', '--weblog', dest='web', action='store_true', default=None, help='log data to webserver')
    parser.add_argument('-b', '--benchmark', dest='bench', type=int, default=None, help='Run and record Dacapo')
    args = parser.parse_args()
    main(args)
