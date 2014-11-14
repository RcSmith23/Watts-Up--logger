#!/usr/bin/env python

import pysftp
from wattsup import *

def main():
    sftp = pysftp.Connection('harvey2.cc.binghamton.edu', username='rsmith23', password='')
    sftp.cwd('public_html/Readings')
    print sftp.pwd
    sftp.put('Readings/avrora')
    sftp.close()
    meter = WattsUp()
    

if __name__ == '__main__':
    main()
