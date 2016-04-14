
#!/usr/bin/python
import argparse
import json
import re
import urllib
import urllib2

import socket
import time
import platform

import os
import ConfigParser

#__author__ = 'onagorodniuk'
parser = argparse.ArgumentParser(description='This is a demo script by nixCraft.')
parser.add_argument('-c','--config',help='located /root/bin/jolokia-graphite.conf', required=True)
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read('/root/bin/jolokia-graphite.conf')
memory = config.get('main', 'memory')
gcyounggen = config.get('main', 'gcyounggen')
gcoldgen = config.get('main', 'gcoldgen')
threadscount = config.get('main', 'threadscount')
graphite = config.get('main', 'graphite')
prefix = config.get('main', 'prefix')
jolokiaurl = config.get('main', 'jolokiaurl')
verbose = config.get('main', 'verbose')


if jolokiaurl != None:
        BASE_URL = jolokiaurl
else:
        BASE_URL = "http://localhost:8080/jolokia"
###DEFINE STANDART VALUES
#short hostname
node = platform.node().replace('.', '-')
timestamp = int(time.time())
#memory = 'java.lang:type=Memory/HeapMemoryUsage'
#args.gcyounggen = 'java.lang:name=G1 Young Generation,type=GarbageCollector'
#args.threadscount = 'java.lang:type=Threading'
#args.gcoldgen = 'java.lang:name=G1 Old Generation,type=GarbageCollector'
GRAPHITE_PORT = 2003
#BASE_URL = "http://localhost:8080/jolokia"
READ_URL = BASE_URL + "/?ignoreErrors=true&p=read/%s"

def heap_usage(READ_URL):
        url =  READ_URL % urllib.quote(memory)
        heap_data = json.load(urllib2.urlopen(url, timeout=5))
        heap_usage.max =  heap_data['value']['max']
        heap_usage.used = heap_data['value']['used']
#hi()
#print hi.bye
def gc_young_gen(READ_URL):
        url =  READ_URL % urllib.quote(gcyounggen)
        gc_data = json.load(urllib2.urlopen(url, timeout=5))
#        print gc_data
        gc_young_gen.duration =  gc_data['value']['LastGcInfo']['duration']
#        heap_usage.used = heap_data['value']['used']

def gc_old_gen(READ_URL):
        url =  READ_URL % urllib.quote(gcoldgen)
        gc_data = json.load(urllib2.urlopen(url, timeout=5))
#        print gc_data
        gc_old_gen.duration =  gc_data['value']['LastGcInfo']['duration']
#        heap_usage.used = heap_data['value']['used']
#gc_old_gen(READ_URL)


def threads_count(READ_URL):
        url =  READ_URL % urllib.quote(threadscount)
        threads_data = json.load(urllib2.urlopen(url, timeout=5))
#        print gc_data
        threads_count.count =  threads_data['value']['ThreadCount']
#        heap_usage.used = heap_data['value']['used']

def send_msg(message):
    if verbose == 'True':
            print 'sending message:\n%s' % message
    sock = socket.socket()
    sock.settimeout(2)
    sock.connect((graphite, GRAPHITE_PORT))
    sock.sendall(message)
    sock.close()

###SEND DATA TO GRAPHITE
if memory != None:
        message = ''
        heap_usage(READ_URL)
        lines = [
                '%s.%s.jmx.java.lang.type_Memory.HeapMemoryUsage.max %s %d' % (prefix, node, heap_usage.max, timestamp),
                '%s.%s.jmx.java.lang.type_Memory.HeapMemoryUsage.used %s %d' % (prefix, node, heap_usage.used, timestamp)]
        message = '\n'.join(lines) + '\n'
        send_msg(message)
#       send_msg(heap_usage.max)
else:
        print 'memory Mbean not defined'

if gcyounggen != None:
        message = ''
        try:
                gc_young_gen(READ_URL)
                lines = [
                '%s.%s.jmx.java.lang.name_G1_Young_Generation.type_GarbageCollector.LastGcInfo.duration %s %d' % (prefix, node, gc_young_gen.duration, timestamp)]
                message = '\n'.join(lines) + '\n'
                send_msg(message)
        except:
                pass
else:
        print 'GC Young Gen Mbean not defined'
if gcoldgen != None:
        try:
                message = ''
                gc_old_gen(READ_URL)
                lines = [
                '%s.%s.jmx.java.lang.name_G1_Old_Generation.type_GarbageCollector.LastGcInfo.duration %s %d' % (prefix, node, gc_old_gen.duration, timestamp)]
                message = '\n'.join(lines) + '\n'
                send_msg(message)
        except:
                pass
else:
        print 'GC Old Gen Mbean not defined'

if threadscount != None:
        try:
                message = ''
                threads_count(READ_URL)
                lines = [
                '%s.%s.jmx.java.lang.type_Threading.ThreadCount %s %d' % (prefix, node, threads_count.count, timestamp)]
                message = '\n'.join(lines) + '\n'
                send_msg(message)
        except:
                pass
else:
        print 'Threading Mdean not defined'
