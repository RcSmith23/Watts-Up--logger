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
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USERNAME')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')

        try:
            con = mdb.connect(db_host, db_user, db_pass, db_name)
            cur = con.cursor()

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
                    
                    insertValues = """INSERT INTO recordings 
                                        (watts, amps, volts, cpu_usage,
                                        mem_usage, io_usage, machineId)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                        (watts, amperage, voltage, cpu, memory, 0)
                    #
                    # Where to write to database
                    #
            n += self.interval
            line = self.s.readline()

    # Returns False if process is a zombie, otherwise True
    def procStatus(self, pid):
        for line in open("/proc/%d/status" % pid).readlines():
            if line.startswith("State:"):
                values = line.split(":", 1)[1].strip().split(' ')[0]
                if values[0] == 'Z':
                    return False
                else:
                    return True
