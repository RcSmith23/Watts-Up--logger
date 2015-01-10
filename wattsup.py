#!/usr/bin/env python

import os, serial
import datetime, time
from platform import uname
import numpy as np
import sqlite3
import subprocess
import psutil
import threading

EXTERNAL_MODE = 'E'
INTERNAL_MODE = 'I'
TCPIP_MODE = 'T'
FULLHANDLING = 2

class WattsUp(object):
    def __init__(self, port=None, interval=None):
        if not port:
            system = uname()[0]
            if system == 'Darwin':          # Mac OS X
                port = '/dev/tty.usbserial-A1000wT3'
            elif system == 'Linux':
                port = '/dev/ttyUSB0'
        if os.path.isfile(port):
            self.s = serial.Serial(port, 115200 )
        else:
            self.meter = False

        self.meter = True
        self.interval = 1.0 if not interval else interval
        self.t = []
        self.power = []
        self.potential = []
        self.current = []
        self.cpu = []
        self.memory = []
        self.thread = None

    # Checking to see if there is a thread logging already
    def logging(self):  
        True if self.thread is not None else False

    # Start logging
    def start(self):
        if self.thread is None:
            self.thread_event = threading.Event()
            self.thread = threading.Thread(target=self.run)
            try:
                self.thread.start()
            except:
                raise Exception("Could not start thread")

    # Stop logging
    def stop(self):
        if self.thread is not None:
            self.thread_event.set()
            if not self.thread.is_alive():
                self.thread = None
            else:
                raise Exception("Could not kill thread")

    # The logging code, run on a separate thread.
    def run(self, stop_event):
        #Need to open up database connection first
        line = self.s.readline()
        n = 0
        while not self.thread_event.is_set():
            time.sleep(self.interval)
            if line.startswith( '#d' ):
                fields = line.split(',')
                if len(fields)>5:
                    watts = float(fields[3]) / 10;
                    voltage = float(fields[4]) / 10;
                    amperage = float(fields[5]) / 1000;
                    cpu = pustil.cpu_percent()
                    memory = psutil.virtual_memory().percent
                    time = datetime.datetime.now()
                        
                    #
                    # Where to write to database
                    #
            n += self.interval
            line = self.s.readline()

    # This code is still here only as reference. Will move a similar version
    # in to the run function.
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


    # Returns False if process is a zombie, otherwise True
    def procStatus(self, pid):
        for line in open("/proc/%d/status" % pid).readlines():
            if line.startswith("State:"):
                values = line.split(":", 1)[1].strip().split(' ')[0]
                if values[0] == 'Z':
                    return False
                else:
                    return True
