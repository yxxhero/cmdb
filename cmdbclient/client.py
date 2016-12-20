#!/usr/bin/env python2.7
# coding:utf-8
import os,sys,commands
import psutil
import platform
import socket
from configobj import ConfigObj

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

if __name__ == '__main__':
	config_file = "./cmdbclient.conf"
	config = ConfigObj(config_file,encoding='UTF8')
	print config['server']
	print config['server']['server_name']

	print
	print
	client = system_info()
	for key,item in  client.get_system_info().items():
		print key,"\t----->",item

	print
	print
