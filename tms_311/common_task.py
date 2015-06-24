#!/usr/bin/env python2.6
#encoding=utf-8

import json
import base64
import os
import sys
if not os.path.join( os.getcwd(), '../..' ) in sys.path:
	sys.path.append(os.path.join( os.getcwd(), '../..' ))
import utils.tmslog
from HostedREST.hosted_basetask import HostedBaseTask
from HostedREST.hosted_taskqueue import HostedTaskQueue

class CommonTask(HostedBaseTask):
	'''
	'''
	def __init__(self):
		self.tqconn = HostedTaskQueue()
		self.tags = []
		pass

	def do_add(self, tqname='iosdeploy', account=1, creator=4, type=1, evt=None):
		"""
		To do:
		      Insert one task into task queue by task queue name.
		"""
		#jevt = json.loads(evt)
		tags = ["account=1", "type=1"]
		
		payload = self.do_parse_payload(evt)
		result = self.tqconn.do_add(tqname = tqname, namespace='mobile', account=account, payload=payload, tags=tags, priority='High')
		if result.code == 200 or result.code == 201:
			self.tags = tags
			utils.tmslog.log('Add task success!')
		else:
			utils.tmslog.log('Add task failed!')
			raise ServerInternalException('Failed to add task!')
		return result.code
		pass

	def do_getTask(self, tqname='iosdeploy', account=1,tags=None, tasknum=10):
		"""
		"""
		tasknum = tasknum
		tags = self.tags 
		result = self.tqconn.do_get_multi(tqname=tqname, account=account, tasknum=tasknum, tags=tags)
		self.m_tasks_list = []
		self.m_tasks_num = 0
		self.do_parse(result.content)
		index = self.m_tasks_num - 1
		return self.m_tasks_list[index]

	
	def do_getEventFromTask(self, task):
		"""
		"""
		task = task
		event = task['payload_base64']
		event = base64.decodestring(event)
		#print event
		return event

	def do_parse_payload(self, evt):
		try:
			jevt = json.loads(evt)
			payload = {}
			if not jevt.has_key('Udid'):
				raise ValueError('UDID missing in the event')

			if not jevt.has_key('DeviceId'):
				raise ValueError('DeviceId missing in the event')

			payload_base64 = (base64.encodestring(evt)).replace("\n", '')
			return payload_base64
		except ValueError, e:
			utils.tmslog.log('Event parse error, %s' % e)
			raise ValueError(e)
		pass

#end of class CommonTask

def do_test():
	evt = {
	        "EventId": 178, 
	        "EnrollmentStatus": "Enrolled", 
	        "Udid": "db017f1becbaef5ce7abf464c39b07a3b1d591d6", 
	        "EnrollmentUserName": "scai", 
	        "EnrollmentEmailAddress": "scai@websense.com", 
	        "DeviceId": "965", 
	        "Ownership": "Undefined", 
	        "Model": "iPhone", 
	        "OperatingSystem": "6.1.4"
	}
	evt = json.dumps(evt)
	task = CommonTask()
	task.do_add(account=86, tqname='iosdeploy', creator=3, type=1, evt=evt)
	pass

if __name__=='__main__':
	do_test()
	pass


