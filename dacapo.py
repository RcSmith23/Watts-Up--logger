#!/usr/bin/env python2.7

# This class will spawn a dacapo benchmark, and record it as
# an instance in the database. 
#
# Given a set of Dacapo tests they will be run concurrently.
# Records total time taken for all tests to complete.
# Delays test running before and after they are started to 
# allow pc to reach idle power.
#
# Will not record whether or not the actual test was failed
# or failed to complete.
#
# To Do: Add ability to run multiple of same test. (There is a problem
# with the Dacapo suite that is limiting this)

import time
import subprocess
import threading
import datetime

class DacapoSuite(object):
    def __init__(self, machineId):
        self.delay = 10
        self.dacapo = 'dacapo-9.12-bach.jar'
        self.times = []
        self.processes = []
        self.tests = []
        self.thread = None
        self.machineId = machineId
        self.threadingEvent = None
        self.suite = {0 : 'avrora',
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
                13 : 'xalan' }

    # Takes tests as arguments, will add smaple size in future
    def run(self, tests=['avrora']):
        self.tests = tests

        # Launch a thread to monitor the tests
        self.threadingEvent = threading.Event()
        self.thread = threading.Thread(target=self.launch)
        try:
            self.thread.start()
        except:
            raise Exception("Could not start monitor thread")
            clean(False)

    def launch(self):
        # Sleep to fall to idle power
        time.sleep(self.delay)

        # Recording the start of the test
        # Will leave time gaps between tests
        # When retrieving the info, can pull this extra time to show
        # the cooldown afterwards.
        self.times[0] = datetime.datetime.now()

        # Launch the tests as subprocesses
        try:
            for test in self.tests:
                self.processes << subprocess.Popen(['java', '-jar', 'dacapo-9.12-bach.jar', test])
	except:
            print 'Failed to launch all benchmarks'
            clean(False)

        # Wait for subprocesses to terminate, save exit codes for future use
        exitCodes = [p.wait() for p in self.processes]

        # Get the end time, then delay. Then do a clean up.
        self.times[1] = datetime.datetime.now()
        time.sleep(self.delay)
        clean()
        
    def running(self):
        if self.processes.length > 0:
            return True
        else:
            return False

    # Cleans up after tests, adds to database
    def clean(self, success=True):
        # If not successful, just kill the tests
        if not success:
            for p in self.processes:
                os.kill(p.pid(), SIGQUIT)
        else:
            # Place all in the database
            db_host = os.getenv('DB_HOST')
            db_user = os.getenv('DB_USERNAME')
            db_pass = os.getenv('DB_PASS')
            db_name = os.getenv('DB_NAME')

            try:
                con = mdb.connect(db_host, db_user, db_pass, db_name)
                cur = con.cursor()
            except mdb.Error, e:
                pass

            instanceInsert = """INSERT INTO instances (start_time, end_time,
                                machine_id) VALUES (?, ?, ?)""", \
                                (self.times[0], self.times[1], self.machineId)
            try:
                cur.execute(instanceInsert)
                con.commit()
            except mdb.Error, e:
                pass
            instanceId = cur.lastrowid

            # Inserting the benchmark_realtion, one for each test 
            # that was executed in the instance
            for t in self.tests:
                # First need to get the id of the benchmark
                try:
                    cur.execute("SELECT * FROM benchmarks WHERE name = '%s'", \
                            (t) )
                    row = cur.fetchone()
                except mdb.Error, e:
                    pass

                # Next insert into benchmark_relation
                relationInsert = """INSERT INTO benchmark_relation (instance_id,
                                    benchmark_id) VALUES (?, ?)""", \
                                    (instanceId, row[0])
                try:
                    cur.execute(relationInsert)
                    con.commit()
                except mdb.Error, e:
                    pass

            con.close()

        # Then clear all the fields
        self.processes = []
        self.tests = []
        self.times = []
        self.thread = None
        self.threadingEvent = None

    # Ability to stop if necessary 
    def stop(self):
        if self.thread is not None:
            self.threadingEvent.set()
            if not self.thread.is_alive():
                self.thread = None
            else:
                raise Exception("Could not kill monitor thread")
        clean(False)
 
    # Returns true if the process has become a zombie
    # Not currently being used
    def isZombie(self, pid):
        for line in open("/proc/%d/status" % pid).readlines():
            if line.startswith("State:"):
                values = line.split(":", 1)[1].strip().split(' ')[0]
                if values[0] == 'Z':
                    return True
                else:
                    return False
