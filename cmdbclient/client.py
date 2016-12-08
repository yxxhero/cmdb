#!/usr/bin/env python2.7
#coding:utf-8
import os
import sys
import platform
import socket
print os.environ
print platform.platform()
print platform.system()
class get_system_info(object):
    def __init__(self):
        self.ip=None
        self.system_type_info=None
        self.services=[]
        self.hostname=''
        self.system_info={}
    def ip_info(self):
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tempSock.connect(('8.8.8.8', 80))
        addr = tempSock.getsockname()[0]
        tempSock.close()
        self.ip = addr
        return self.ip
    def system_type(self):
        self.system_type_info=platform.platform()
        return self.system_type_info
    def hostname_info(self):
        self.hostname=os.environ['HOSTNAME']
        return self.hostname
    def systeminfo(self):
        self.system_info['ip']=self.ip_info()
        self.system_info['systemtype']=self.system_type()
        self.system_info['hostname']=self.hostname_info()
        return self.system_info
if __name__=='__main__':
    client=get_system_info()
    print client.systeminfo()
        
    
