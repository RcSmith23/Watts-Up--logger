
Run method in the dacapo class. Run it as a thread, then have it 
spawn the subprocess benchmarks and monitor those until they finish. 
Record the results to the database.

Dacapo class needs to keep track of the run method that is spawned in 
a new thread. 
