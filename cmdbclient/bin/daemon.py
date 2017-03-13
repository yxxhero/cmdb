#!/usr/bin/python
#coding=utf8
"""
# Author: yxx
# Created Time : 2017-03-13 23:01:15

# File Name: daemon.py
# Description:

"""
import os
import time
import sys
import atexit
import string
from signal import SIGTERM
class Daemon:
    def __init__(self,pidfile,Debug=False):
        if Debug:
            self.stdin='/dev/stdin'
            self.stdout='/dev/stdout'
            self.stderr='/dev/stderr'
        else:
            self.stdin=stdin
            self.stdout=stdout
            self.stderr=stderr
        self.pidfile=pidfile
    def _daemonize(self):
        try:
            pid=os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.stderr.write('fork #1 faid: %d (%s)\n' % (e.errno,e.strerror))
            sys.exit(1)
        os.chdir('/')
        os.setreuid()
        os.umask(0)
        try:
            pid=os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError,e:
            sys.stderr.write('fork #1 faid: %d (%s)\n' % (e.errno,e.strerror))
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()
        si=file(self.stdin,'r')
        so=file(self.stdout,'a+')
        se=file(self.stderr,'a+',0)
        os.dup2(si.fileno(),sys.stdin.fileno())
        os.dup2(so.fileno(),sys.stdin.fileno())
        os.dup2(se.fileno(),sys.stdin.fileno())
        atexit.register(self.delpid)
        pid=str(os.getpid())
        file(self.pidfile,'w+').write('%s\n' %pid)
    def start(self):
        try:
            pf=file(self.pidfile,'r')
            pid=int(pf.read().strip())
            pf.close()
        except IOError:
            pid=None
        if pid:
            message='pidfile %s already exist. Daemon already running!\n'
            sys.stderr.write(message,% self.pidfile)
            sys.exit(1)
        self._daemonize()
        self._run()
    def stop(self):
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = 'pidfile %s does not exist. Daemon not running!\n'
            sys.stderr.write(message % self.pidfile)
            return
        try:
            while 1:
                os.kill(pid,SIGTERM)
                time.sleep(0.1)
        except OSError,err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print str(err)
                    sys.exit(1)''
    def restart(self):
        self.stop()
        self.start()
    def _run(self):
        """run your fun"""





            
