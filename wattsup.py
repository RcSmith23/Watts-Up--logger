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
    def __init__(self, port, interval):
        if args.sim:
            self.s = open(port,'r')     # not a serial port, but a file
        else:
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
        self.tests = {0 : 'idle',
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

    def mode(self, runmode):
        if args.sim:
            return                      # can't set run mode while in simulation
        self.s.write('#L,W,3,%s,,%d;' % (runmode, self.interval) )
        if runmode == INTERNAL_MODE:
            self.s.write('#O,W,1,%d' % FULLHANDLING)

    def benchmark(self, logfile = None):
        print 'Running Benchmarks...'
        if not args.sim:
            self.mode(EXTERNAL_MODE)
        if args.raw:
            rawfile = '.'.join([os.path.splitext(self.logfile)[0],'raw'])
            try:
                r = open(rawfile,'w')
            except:
                print 'Opening raw file %s failed!' % rawfile
                args.raw = False
        line = self.s.readline()
        # set up curses
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.nodelay(1)
        try:
            curses.curs_set(0)
        except:
            pass
        for x in range(0, 29):
            for y in range(0, 10):
                line = self.s.readline()
                psutil.cpu_percent(1)
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
            while True:
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
                        screen.clear()
                        if x < 15:
                            screen.addstr(2, 4, 'Running test: %s, path: %s' % (self.tests[x], pid_path))
                        else:
                            screen.addstr(2, 4, 'Running tests: %s and %s, paths: %s, %s' 
                                            % (self.tests[5], self.tests[29-x], pid_path, pid_path2))
                        screen.addstr(4, 4, 'Time:     %d s' % n)
                        screen.addstr(5, 4, 'Power:   %3.1f W' % W)
                        screen.addstr(6, 4, 'Voltage: %5.1f V' % V)
                        screen.addstr(8, 4, 'Loop iteration: %d' % x)
                        if A<1000:
                            screen.addstr(7, 4, 'Current: %d mA' % int(A*1000))
                        else:
                            screen.addstr(7, 4, 'Current: %3.3f A' % A)
                        screen.addstr(10, 4, 'Press "s" to end current test ')
                        screen.addstr(11, 4, 'Press "q" to quit test sequence \n\n')
                        screen.refresh()
                        c = screen.getch()
                        if c in (ord('s'), ord('S')):
                            if x != 14:
                                proc.kill()
                            break  # Exit the while()
                        if self.logfile:
                            fd.write('%s %d %3.1f %3.1f %5.3f %3.1f %3.1f\n' % (datetime.datetime.now(), n, W, V, A, C, M))
                        if x == 0 and n >= 30:
                            break
                        if not os.path.exists(pid_path) or not self.procStatus(pid):
                            if x < 15:
                                break
                            else:
                                if not os.path.exists(pid_path2) or not self.procStatus(pid2):
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

    def record(self):
        conn = sqlite3.connect('Databases/records.db')
        cursor = conn.cursor()
        for x in range(0, 15):
           total_watts = 0
           peak_watts = 0
           end_time = None
           peak_current = 0
           peak_voltage = 0       
           test_name = self.tests[x]
           test_file = 'Readings/' + test_name
           try:
               fd = open(test_file, 'r')
           except:
               print "Couldn't open file %s, cannot record", test_file
           i = 0
           for l in fd:
               l = l.rstrip()
               values = l.split(" ")
               total_watts += float(values[3])
               if float(values[3]) > peak_watts:
                   peak_watts = float(values[3])
               if float(values[4]) > peak_voltage:
                   peak_voltage = float(values[4])
               if float(values[5]) > peak_current:
                   peak_current = float(values[5])
               if i == 0:
                   temp_start_time = values[0] + ' ' + values[1]
               i += 1
           start_time = datetime.datetime.strptime(temp_start_time, '%Y-%m-%j %H:%M:%S.%f')
           temp_end_time = values[0] + ' ' + values[1]
           end_time = datetime.datetime.strptime(temp_end_time, '%Y-%m-%j %H:%M:%S.%f')
           fd.close()
           time_elapsed = end_time - start_time
           start_time = str(start_time)
           end_time = str(end_time)
           cursor.execute("""INSERT INTO instances (test_name, time_started, time_completed, time_elapsed,
				total_wattage, peak_wattage, peak_current, peak_voltage) VALUES
				(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (test_name, str(start_time), str(end_time), str(time_elapsed),
			        total_watts, peak_watts, peak_current, peak_voltage))
        conn.commit()
        conn.close()

    def average(self):
        conn = sqlite3.connect('Databases/records.db')
        cursor = conn.cursor()
        try:
            fd = open(self.machine_file, 'w')
        except:
            print 'Could not open file %s'
            self.machine_file = None
        for x in range(0, 15):
            test_name = self.tests[x]
            avg_elapsed_time = datetime.datetime.strptime('00:00:00.00', '%H:%M:%S.%f')
            avg_total_watts = 0
            avg_peak_watts = 0
            avg_peak_current = 0
            avg_peak_voltage = 0
            cursor.execute("Select * FROM instances WHERE test_name=?", (test_name,))
            if not cursor.rowcount == 0:
                records = cursor.fetchall()
                i = 0
                for record in records:
                    temp_time = datetime.datetime.strptime(record[4], '%H:%M:%S.%f')
                    avg_elapsed_time += temp_time;
                    avg_total_watts += float(record[5])
                    avg_peak_watts += float(record[6])
                    avg_peak_current += float(record[7])
                    avg_peak_voltage += float(record[8])
                    i += 1
                avg_elapsed_time = (avg_elapsed_time / i)
                avg_total_watts = (avg_total_watts / i)
                avg_peak_watts = (avg_peak_watts / i)
                avg_peak_current = (avg_peak_current / i)
                avg_peak_voltage = (avg_peak_voltage / i)
            cursor.execute("SELECT * FROM averages WHERE test_name=?", (test_name,))
            if cursor.fetchall() is None:
                cursor.execute("""UPDATE averages SET avg_time_elapsed=?, avg_total_wattage=?, avg_peak_wattage=?,
				avg_peak_current=?, avg_peak_voltage=?  WHERE test_name=?""",
				(avg_elapsed_time, avg_total_watts, avg_peak_watts, avg_peak_current, avg_peak_voltage, test_name))
            else:
                cursor.execute("""INSERT INTO averages (test_name, avg_time_elapsed, avg_total_wattage, avg_peak_wattage,
				avg_peak_current, avg_peak_voltage) VALUES (?, ?, ?, ?, ?, ?, ?)""", 
				(test_name, avg_elapsed_time, avg_total_watts, avg_peak_watts, avg_peak_current, avg_peak_voltage))
            if self.machine_file:
                fd.write('%s %s %3.1f %3.1f %5.3f %3.1f %3.1f\n' % (test_name, avg_elapsed_time, avg_total_watts, avg_peak_watts, avg_peak_current, avg_peak_voltage))
        conn.commit()
        conn.close()
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
            for i in range(0, 29):
                if i < 15:
                    test_file = 'Readings/' + self.tests[i]
                else:
                    test_file = 'Readings/' + self.tests[5] + self.tests[29-i]
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
    if not args.port:
        system = uname()[0]
        if system == 'Darwin':          # Mac OS X
            args.port = '/dev/tty.usbserial-A1000wT3'
        elif system == 'Linux':
            args.port = '/dev/ttyUSB0'
    if not os.path.exists(args.port):
        if not args.sim:
            print ''
            print 'Serial port %s does not exist.' % args.port
            print 'Please make sure FDTI drivers are installed'
            print ' (http://www.ftdichip.com/Drivers/VCP.htm)'
            print 'Default ports are /dev/ttyUSB0 for Linux'
            print ' and /dev/tty.usbserial-A1000wT3 for Mac OS X'
            exit()
        else:
            print ''
            print 'File %s does not exist.' % args.port
    if args.web:
         passwd = getpass.getpass('Webserver password: ')
    meter = WattsUp(args.port, args.interval)
    if args.bench:
        #createDB();
        meter.benchmark(args.outfile)
        #meter.record()
        #meter.average()
    if args.web:
         meter.transfer(passwd)
    if args.internal:
        meter.mode(INTERNAL_MODE)

def createDB():
    conn = sqlite3.connect(r"Databases/records.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE if NOT EXISTS instances (id INTEGER PRIMARY KEY, test_name TEXT,
			 time_started TEXT, time_completed TEXT, time_elapsed TEXT, 
			total_wattage REAL, peak_wattage REAL, peak_current REAL, 
			peak_voltage REAL)''')
    cursor.execute('''CREATE TABLE if NOT EXISTS averages (id INTEGER PRIMARY KEY, test_name TEXT, 
		avg_time_elapsed REAL, avg_total_wattage REAL, avg_peak_wattage REAL, 
		avg_peak_current REAL, avg_peak_voltage REAL)''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from Watts Up power meter.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debugging output')
    parser.add_argument('-m', '--simulation-mode', dest='sim', action='store_true', help='simulate logging by reading serial data from disk with delay of sample interval between lines')
    parser.add_argument('-i', '--internal-mode', dest='internal', action='store_true', help='Set meter to internal logging mode')
    parser.add_argument('-l', '--log', dest='log', action='store_true', help='log data in real time')
    parser.add_argument('-r', '--raw', dest='raw', action='store_true', help='output raw file')
    parser.add_argument('-o', '--outfile', dest='outfile', default='log.out', help='Output file')
    parser.add_argument('-s', '--sample-interval', dest='interval', default=1.0, type=float, help='Sample interval (default 1 s)')
    parser.add_argument('-p', '--port', dest='port', default=None, help='USB serial port')
    parser.add_argument('-w', '--weblog', dest='web', action='store_true', default=None, help='log data to webserver')
    parser.add_argument('-b', '--benchmark', dest='bench', action='store_true', default=None, help='Run and record Dacapo')
    args = parser.parse_args()
    main(args)
