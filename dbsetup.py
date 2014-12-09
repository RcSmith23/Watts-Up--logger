#!/ust/bin/python
# -*- coding: utf-8 -*-
import MySQLdb as mdb
import sys

db_name = 'energy_research'
tables = {}
tables['machines'] = 
    '''CREATE TABLE if NOT EXISTS machines (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        cores INT,
        memory INT
        )'''
tables['recordings'] = 
    '''CREATE TABLE if NOT EXISTS recordings (
        id INTEGER PRIMARY KEY,
        time_stamp TIMESTAMP NOT NULL,
        watts DOUBLE(4,1) NOT NULL,
        amps DOUBLE(4,1) NOT NULL,
        volts DOUBLE(4,1) NOT NULL,
        cpu_usage DOUBLE(3,1) NOT NULL,
        mem_usage DOUBLE(3,1) NOT NULL,
        io_usage DOUBLE(3,1) NOT NULL,
        machine_id INT FOREIGN KEY,
        )'''
tables['recordings'] = 
    '''CREATE TABLE if NOT EXISTS instances (
        id INTEGER PRIMARY KEY,
        time_stamp TIMESTAMP NOT NULL,
        watts DOUBLE(4,1) NOT NULL,
        amps DOUBLE(4,1) NOT NULL,
        volts DOUBLE(4,1) NOT NULL,
        cpu_usage DOUBLE(3,1) NOT NULL,
        mem_usage DOUBLE(3,1) NOT NULL,
        io_usage DOUBLE(3,1) NOT NULL,
        machine_id INT FOREIGN KEY,
        )'''

try:
    con = mdb.connect('beast', 'rsmith23', 'rsmith231', 'energy_reseach')
    cur = con.cursor(:)
	
except: mdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:
    if con:
        con.close()
