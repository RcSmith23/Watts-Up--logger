#!/usr/bin/env python

import pysftp

def main():
    sftp = pysftp.Connection('harvey2.cc.binghamton.edu', username='rsmith23', password='Pureroot5')
    sftp.cwd('public_html/Readings')
    print sftp.pwd
    sftp.put('Readings/avrora')
    sftp.close()

if __name__ == '__main__':
    main()
