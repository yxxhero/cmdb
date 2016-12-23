#!/usr/bin/env python2.7
# coding:utf-8
import commands
import sys
import os
import psutil
import platform
import socket
import urllib
import urllib2
import time
import argparse
import atexit
import errno
import signal
from configobj import ConfigObj
from __future__ import print_function
class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin=os.devnull,
                 stdout=os.devnull, stderr=os.devnull,
                 home_dir='.', umask=0o22, verbose=1,
                 use_gevent=False, use_eventlet=False):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.home_dir = home_dir
        self.verbose = verbose
        self.umask = umask
        self.daemon_alive = True
        self.use_gevent = use_gevent
        self.use_eventlet = use_eventlet

    def log(self, *args):
        if self.verbose >= 1:
            print(*args)

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        if self.use_eventlet:
            import eventlet.tpool
            eventlet.tpool.killall()
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        if sys.platform != 'darwin':  # This block breaks on OS X
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            si = open(self.stdin, 'r')
            so = open(self.stdout, 'a+')
            if self.stderr:
                try:
                    se = open(self.stderr, 'a+', 0)
                except ValueError:
                    # Python 3 can't have unbuffered text I/O
                    se = open(self.stderr, 'a+', 1)
            else:
                se = so
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

        def sigtermhandler(signum, frame):
            self.daemon_alive = False
            sys.exit()

        if self.use_gevent:
            import gevent
            gevent.reinit()
            gevent.signal(signal.SIGTERM, sigtermhandler, signal.SIGTERM, None)
            gevent.signal(signal.SIGINT, sigtermhandler, signal.SIGINT, None)
        else:
            signal.signal(signal.SIGTERM, sigtermhandler)
            signal.signal(signal.SIGINT, sigtermhandler)

        self.log("Started")

        # Write pidfile
        atexit.register(
            self.delpid)  # Make sure pid file is removed if we quit
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        try:
            # the process may fork itself again
            pid = int(open(self.pidfile, 'r').read().strip())
            if pid == os.getpid():
                os.remove(self.pidfile)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

    def start(self, *args, **kwargs):
        """
        Start the daemon
        """

        self.log("Starting...")

        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            message = "pidfile %s already exists. Is it already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run(*args, **kwargs)

    def stop(self):
        """
        Stop the daemon
        """

        if self.verbose >= 1:
            self.log("Stopping...")

        # Get the pid from the pidfile
        pid = self.get_pid()

        if not pid:
            message = "pidfile %s does not exist. Not running?\n"
            sys.stderr.write(message % self.pidfile)

            # Just to be sure. A ValueError might occur if the PID file is
            # empty but does actually exist
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)

            return  # Not an error in a restart

        # Try killing the daemon process
        try:
            i = 0
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                if i % 10 == 0:
                    os.kill(pid, signal.SIGHUP)
        except OSError as err:
            if err.errno == errno.ESRCH:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

        self.log("Stopped")

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def get_pid(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid

    def is_running(self):
        pid = self.get_pid()

        if pid is None:
            self.log('Process is stopped')
            return False
        elif os.path.exists('/proc/%d' % pid):
            self.log('Process (pid %d) is running...' % pid)
            return True
        else:
            self.log('Process (pid %d) is killed' % pid)
            return False

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        raise NotImplementedError
class system_info(object):
    def __init__(self):
        self.system_info = {}
        self.hostname = ''
        self.ip_dict = {}
        self.cpu_info = {}
        self.kernel_info = ''
        self.system_name = ''
        self.architecture = ''
        self.process_info = {}
        self.mem_info = {}
        self.disk_info = {}
	
    def get_disk_info(self):
        disks=psutil.disk_partitions()
        tmp_disk_detail = {}
        for disk in disks:
            device = disk[0]
            tmp_disk_detail["mount_point"] = disk[1]
            tmp_disk_detail["fs_type"] = disk[2]
            tmp_disk_detail["mount_options"] = disk[3]
            tmp_disk_detail["total"] = psutil.disk_usage(disk[1])[0]/1024/1024
            tmp_disk_detail["used"] = psutil.disk_usage(disk[1])[1]/1024/1024
            tmp_disk_detail["free"] = psutil.disk_usage(disk[1])[2]/1024/1024
            tmp_disk_detail["percent"] = psutil.disk_usage(disk[1])[3]/1024/1024
            self.disk_info[device] = tmp_disk_detail
            self.disk_info["total_read_count"] = psutil.disk_io_counters()[0]
            self.disk_info["total_write_count"] = psutil.disk_io_counters()[1]
            self.disk_info["total_read_bytes"] = psutil.disk_io_counters()[2]/1024/1024
            self.disk_info["total_write_bytes"] = psutil.disk_io_counters()[3]/1024/1024
            self.disk_info["total_read_time"] = psutil.disk_io_counters()[4]
            self.disk_info["total_write_time"] = psutil.disk_io_counters()[5]
            self.disk_info["total_read_merged_count"] = psutil.disk_io_counters()[6]
            self.disk_info["total_write_merged_count"] = psutil.disk_io_counters()[7]
            self.disk_info["total_busy_time"] = psutil.disk_io_counters()[8]
        return self.disk_info
    
    def get_kernel_info(self):
        self.kernel_info = commands.getstatusoutput("uname -r")[1]
        return self.kernel_info

    def get_system_name(self):
        self.system_name = commands.getstatusoutput("uname -o")[1]
        return self.system_name
	
    def get_architecture(self):
        self.architecture= commands.getstatusoutput("uname -m")[1]
        return self.architecture

    def get_mem_info(self):
        self.mem_info['total'] = psutil.virtual_memory().total/1024/1024
        self.mem_info['available'] = psutil.virtual_memory().available/1024/1024
        self.mem_info['used'] = psutil.virtual_memory().used/1024/1024
        self.mem_info['free'] = psutil.virtual_memory().free/1024/1024
        self.mem_info['active'] = psutil.virtual_memory().active/1024/1024
        self.mem_info['inactive'] = psutil.virtual_memory().inactive/1024/1024
        self.mem_info['buffers'] = psutil.virtual_memory().buffers/1024/1024
        self.mem_info['cached'] = psutil.virtual_memory().cached/1024/1024
        self.mem_info['shared'] = psutil.virtual_memory().shared/1024/1024
        return self.mem_info

    def get_process_info():
        pass
		
    def get_hostname(self):
        self.hostname=socket.gethostname()
        return self.hostname

    def get_ip_dict(self):
        if platform.system() == 'Linux':
            for line in os.popen("ip add | grep \"scope global\" ").readlines():
                device = line.split()[-1]
                ip = line.split()[1]
                self.ip_dict[device] = ip
        if platform.system() == 'Windows':
            adapter_num = 0
            for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
                adapter_num = adapter_num + 1
                device = "adapter"+str(adapter_num)
                self.ip_dict[device] = ip
        return self.ip_dict
	
    def get_cpu_info(self):
        self.cpu_info['logical_cores'] = psutil.cpu_count()
        self.cpu_info['physical_cores'] = psutil.cpu_count(logical = False)
        self.cpu_info["cpu_usage"] = psutil.cpu_percent()
        return self.cpu_info

    def get_system_info(self):
        self.system_info['hostname'] = self.get_hostname()
        self.system_info['ip_dict'] = self.get_ip_dict()
        self.system_info['cpu_info'] = self.get_cpu_info()
        self.system_info['mem_info'] = self.get_mem_info()
        self.system_info['kernel_info'] = self.get_kernel_info()
        self.system_info['system_name'] = self.get_system_name()
        self.system_info['architecture'] = self.get_architecture()
        self.system_info['disk_info'] = self.get_disk_info()
        return self.system_info
    def post_system_info(self,url,data):
        format_data=urllib.urlencode(data)
        req=urllib2.Request(url,format_data)
        response=urllib2.urlopen(req)
        content=response.read()
        return content
		
class pantalaimon(Daemon):
    def run(self):
        while True:
            config_file = "/opt/cmdb/cmdbclient/etc/cmdbclient.conf"
            config = ConfigObj(config_file,encoding='UTF8')
            host=config['server']['server_host']
            port=config['server']['server_port']
            uri=config['server']['uri']
            interval=config['client']['interval']
            url='http://'+host+':'+port+uri
            print url
            time.sleep(int(interval))
            client = system_info()
            data={"host_info":client.get_system_info()}
            print data
            result=client.post_system_info(url,data)
            print result
if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='cmdbclient')
    parser.add_argument('action',choices=['start','restart','stop','run'],default='start',type=str,help='指定操作类型')
    parser.add_argument('-c',type=str,help='指定配置文件')
    args=parser.parse_args()
    action=args.action
    d = pantalaimon('/var/lib/cmdb.pid', verbose=1)
    getattr(d, action)()
