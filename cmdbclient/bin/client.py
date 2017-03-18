#!/usr/bin/env python2.7
# coding:utf-8
import gevent
from gevent import monkey
monkey.patch_all()
import socket
import commands
import sys
import os
import psutil
import platform
import urllib
import urllib2
import time
import argparse
import signal
import logging
from configobj import ConfigObj
import zerorpc
if 'threading' in sys.modules:
    del sys.modules['threading']
class system_info(object):
    def __init__(self):
        self.systeminfo = {}
        self.hostname = ''
        self.ip_dict = {}
        self.cpu_info = {}
        self.system_name = ''
        self.process_info = {}
        self.mem_info = {}
        self.disk_info = {}
	
    def get_sysinfo(self):
        uptime = int(time.time() - psutil.boot_time())
        sysinfo = {
            'uptime': uptime,
            'hostname': socket.gethostname(),
            'os': platform.platform(),
            'num_cpus': psutil.cpu_count()
        }

        return sysinfo
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
        return self.disk_info
    
    def get_system_name(self):
        self.system_name =''.join(platform.linux_distribution()[0:2]) 
        return self.system_name

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
        self.mem_info['percent'] = psutil.virtual_memory().percent
        return self.mem_info

    def get_process_info(self,*args,**kwargs):
        ps_list=[]
        list=psutil.process_iter()
        for proc in list:
            ps=proc.as_dict(attrs=['pid', 'name'])['name']
            if ps in args[0]: 
               if ps not in ps_list:
                   ps_list.append(ps)
        return ps_list
		
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
        self.cpu_info['load_avg']=' '.join([str(i) for i in os.getloadavg()])
        self.cpu_info['user']=psutil.cpu_times().user
        self.cpu_info['system']=psutil.cpu_times().system
        self.cpu_info['idle']=psutil.cpu_times().idle
        self.cpu_info['iowait']=psutil.cpu_times().iowait
        return self.cpu_info

    def get_system_info(self,*args,**kwargs):
        self.systeminfo['hostname'] = self.get_hostname()
        self.systeminfo['ip_dict'] = self.get_ip_dict()
        self.systeminfo['cpu_info'] = self.get_cpu_info()
        self.systeminfo['mem_info'] = self.get_mem_info()
        self.systeminfo['system_name'] = self.get_system_name()
        self.systeminfo['disk_info'] = self.get_disk_info()
        self.systeminfo['processlist'] = self.get_process_info(*args,**kwargs)
        
        return self.systeminfo
    def post_system_info(self,url,data):
        format_data=urllib.urlencode(data)
        req=urllib2.Request(url,format_data)
        response=urllib2.urlopen(req)
        content=response.read()
        return content

LOG = logging.getLogger(__name__)


def daemonrun(proclist):
        gevent.joinall(proclist)


def foo(client,url,interval,psinfo):
    while True:
        client_data=client.get_system_info(pslist)
        host_data={'host_info':client_data}
        result=client.post_system_info(url,host_data)
        gevent.sleep(interval)

if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='cmdbclient')
    parser.add_argument('--config',default='/opt/cmdb/cmdbclient/etc/cmdbclient.conf',type=str,help='指定配置文件')
    parser.add_argument('action',type=str,choices=['start','restart','stop','run','status'],help='启动方式')
    args=parser.parse_args()
    action=args.action
    config_file=args.config
    config=ConfigObj(config_file,encoding='UTF8')
    interval=int(config['client']['interval'])
    host=config['server']['server_host']
    port=config['server']['server_port']
    uri=config['server']['uri']
    url='http://'+host+':'+port+uri
    pidfile=config['client']['pidfile']
    pslist=config['client']['process_list'].split('^')
    logging.basicConfig(filename="daemon.log", level=logging.DEBUG)
    client_info=system_info()
    if action=='start':
       s = zerorpc.Server(system_info())
       s.bind("tcp://0.0.0.0:4242")
       zero_daemon=gevent.spawn(s.run)
       client_daemon=gevent.spawn(foo,client_info,url,interval,pslist)
       daemonlist=[zero_daemon,client_daemon]
       daemonrun(daemonlist)
