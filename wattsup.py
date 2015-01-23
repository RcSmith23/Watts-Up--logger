#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

import os, serial
import datetime, time
from platform import uname
import numpy as np
import psutil
import threading
import datetime
import MySQLdb as mdb

class WattsUp(object):
    def __init__(self, machineId, interval=None):
        if not port:
            port = '/dev/ttyUSB0'
        if os.path.isfile(port):
            self.s = serial.Serial(port, 115200 )
        else:
            self.meter = False

        self.meter = True
        self.interval = 1.0 if not interval else interval
        self.thread = None
        self.dbConnect = False
        self.machineId = machineId

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
        except mdb.Error, e:
            self.stop()

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
                    time = datetime.datetime.now().strftime("%Y-%m-%d \
                    %H:%M:%S.%f")
                    
                    insertValues = """INSERT INTO recordings 
                                        (time_stamp, watts, amps, volts, cpu_usage,
                                        mem_usage, io_usage, machineId) VALUES 
                                        ('%s', '%f', '%f', '%f', '%f', '%f',
                                        '%f', '%d')""", \
                                        (time, watts, amperage, voltage, cpu, \
                                                memory, 0.0, self.machineId)
                    try:
                        cur.execute(insertValues)
                        con.commit()
                    except mdb.Error, e:
                        pass
                        # Print out some sort of log message maybe

                    n += self.interval
            line = self.s.readline()
