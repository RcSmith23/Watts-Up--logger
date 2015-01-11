#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb as mdb
import sys, os
import psutil
from platform import uname
    
tables = {}

tables[0] = """CREATE TABLE IF NOT EXISTS machines (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    cores INT,
    memory BIGINT
    );"""
tables[1] = '''CREATE TABLE IF NOT EXISTS recordings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    time_stamp TIMESTAMP NOT NULL,
    watts DOUBLE(4,1) NOT NULL,
    amps DOUBLE(4,1) NOT NULL,
    volts DOUBLE(4,1) NOT NULL,
    cpu_usage DOUBLE(3,1) NOT NULL,
    mem_usage DOUBLE(3,1) NOT NULL,
    io_usage DOUBLE(3,1) NOT NULL,
    machine_id INT NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
    );'''
tables[2] = '''CREATE TABLE IF NOT EXISTS instances (
    id INT PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    machine_id INT NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
    );'''
tables[3] = '''CREATE TABLE IF NOT EXISTS benchmarks (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    mem_intensive BOOL,
    cpu_intensive BOOL,
    description TEXT
    );'''
tables[4] = '''CREATE TABLE IF NOT EXISTS benchmark_relation (
    id INT PRIMARY KEY,
    instance_id INT NOT NULL,
    benchmark_id INT NOT NULL,
    FOREIGN_KEY (instance_id) REFERENCES instances(id),
    FOREIGN_KEY (benchmark_id) REFERENCES benchmarks(id)
    );'''

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USERNAME')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

cores = psutil.cpu_count()
machine = uname()[1]
memory = psutil.virtual_memory()[0]
machineInsert = """INSERT INTO machines (name, cores, memory) 
                    SELECT * FROM (SELECT '%s', '%d', '%d') AS tmp
                    WHERE NOT EXISTS (
                        SELECT name FROM machines WHERE name = '%s'
                    ) LIMIT 1;""" % (machine, cores, memory, machine)
try:
    # Setting up the database connection
    con = mdb.connect(db_host, db_user, db_pass, db_name)
    cur = con.cursor()

    # Creating the required tables if they do not exist
    for t in xrange(len(tables)):
        try:
            cur.execute(tables[t])
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
    con.commit()

    # Adding an entry for this machine if not exists
    cur.execute(machineInsert)
    con.commit()

except mdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:
     if con:
        con.close()
