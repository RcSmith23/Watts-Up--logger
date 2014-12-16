#!/ust/bin/python
# -*- coding: utf-8 -*-
import MySQLdb as mdb
import sys

db_name = 'energy_research'
tables = {}
tables['machines'] = """CREATE TABLE IF NOT EXISTS machines (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    cores INT,
    memory INT
    );"""
tables['recordings'] = '''CREATE TABLE IF NOT EXISTS recordings (
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
tables['instances'] = '''CREATE TABLE IF NOT EXISTS instances (
    id INT PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    machine_id INT NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(id)
    );'''
tables['benchmarks'] = '''CREATE TABLE IF NOT EXISTS benchmarks (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    mem_intensive BOOL,
    cpu_intensive BOOL,
    description TEXT
    );'''
tables['benchmark_relation'] = '''CREATE TABLE IF NOT EXISTS benchmark_relation (
    id INT PRIMARY KEY,
    instance_id INT NOT NULL,
    benchmark_id INT NOT NULL,
    FOREIGN_KEY (instance_id) REFERENCES instances(id),
    FOREIGN_KEY (benchmark_id) REFERENCES benchmarks(id)
    );'''

try:
    con = mdb.connect('beast', 'rsmith23', 'rsmith231', db_name)
    cur = con.cursor()
    for t in tables:
        try:
            cur.execute(tables[t])
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
    con.commit()

except mdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:
     if con:
        con.close()
