#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Adds the machines info to the database

import MySQLdb as mdb
import sys, os
import psutil
from platform import uname

def main():
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USERNAME')
    db_pass = os.getenv('DB_PASS')
    db_name = os.getenv('DB_NAME')

    cores = psutil.NUM_CPUS
    machine = uname()[1]
    memory = psutil.virtual_memory()[0] / 1000000000
    machineInsert = """INSERT INTO machines (name, cores, memory) 
                        SELECT * FROM (SELECT '%s', '%d', '%d') AS tmp
                        WHERE NOT EXISTS (
                            SELECT name FROM machines WHERE name = '%s'
                        ) LIMIT 1;""" % (machine, cores, memory, machine)

    try:
        con = mdb.connect(db_host, db_user, db_pass, db_name)
        cur = con.cursor()

        try:
            cur.execute(machineInsert)
            con.commit()
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])

    finally:
        if con:
            con.close()

if __name__ == '__main__':
    main()
