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
from notification_server.server_internal_exception import ServerInternalException

class CommonTask(HostedBaseTask):
	'''
	class EnrollmentDicisionTask
		This class implements the task information and operations for enrollment decision task queue

	Attributes:
		None
	
	Notes:
		All sections in the basetask list as follows:
		owner, priority, enqueue_timestamp, account, name, tags, http_last_modified, task_retries, payload_base64

		tags and payload_base64 would be parsed in the subclass.
	'''
	def __init__(self):
		self.tqconn = HostedTaskQueue()
		self.tags = []
		pass

	def do_add(self, tqname=None, account=1, creator=1, type=1, evt=None):
		"""
		To do:
		      Insert one task into task queue by task queue name.
		"""
		jevt = json.loads(evt)
		tags = []
		if tqname == 'usergroup':
			tags.append("reties=0")
			tags.append("type=" + str(type))
			tags.append("creator=" + str(creator))
		else:
			tags.append("creator=" + str(creator))
			tags.append("device=" + jevt['Udid'])
			tags.append("owner=" + jevt['EnrollmentEmailAddress'])
			tags.append("type=" + str(type)) 
			tags.append("status=1")
		
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

	def do_getTask(self, tqname=None, account=1,tags=None, tasknum=10):
		"""
		TODO: 
			Get out one task out from a task queue.	
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			tasknum: Number of the tasks that expected.
			tags: Search conditions.
		Return:
			Instance object of class Task;
			Exception message
		"""
		tasknum = tasknum
		tags = self.tags 
		result = self.tqconn.do_get_multi(tqname=tqname, account=account, tasknum=tasknum, tags=tags)
		self.m_tasks_list = []
		self.m_tasks_num = 0
		self.do_parse(result.content)
		index = self.m_tasks_num - 1
		#print self.m_tasks_list[index]
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

			if not jevt.has_key('EnrollmentEmailAddress'):
				raise ValueError('EnrollmentEmailAddress missing in the event')

			if not jevt.has_key('EnrollmentUserName'):
				raise ValueError('EnrollmentUserName missing in the event')

			payload_base64 = (base64.encodestring(evt)).replace("\n", '')
			return payload_base64
		except ValueError, e:
			utils.tmslog.log('Event parse error, %s' % e)
			raise ValueError(e)
		pass

#end of class CommonTask

def do_test():
	evt = {
			"EventId":148,
			"MACAddress":"System.Byte[]",
			"EventTime":"/Date(1368076195887)/",
			"ComplianceStatus":"Compliant",
			"Udid":"",
			"EventType":"MDMEnrollmentComplete",
			"SerialNumber":"861348SXA4S",
			"CompromisedStatus":"",
			"EnrollmentEmailAddress":"hdu@websense.com",
			"DeviceFriendlyName":"iPhone3,1-42a65c8289b7ddbcc8ab0fd342bb237534ba60c9",
			"PhoneNumber":"+8613426192820",
			"DeviceId":616,
			"EnrollmentStatus":"Enrolled",
			"EnrollmentUserName":"Hang",
			"CompromisedTimeStamp":"/Date(1368076202626)/"
		}
	evt = json.dumps(evt)
	task = CommonTask()
	task.do_add(account=86, tqname='enrollment', creator=3, type=1, evt=evt)
	pass

if __name__=='__main__':
	do_test()
	pass


