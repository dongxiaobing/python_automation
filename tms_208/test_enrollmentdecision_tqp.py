#!/usr/bin/env python2.6
#encoding=utf-8
import json
import base64
import os
import sys
if not os.path.join( os.getcwd(), '../..' ) in sys.path:
		sys.path.append(os.path.join( os.getcwd(), '../..' ))
import utils.tmslog
#import utils.dictutils
#from HostedREST.hosted_basetask import HostedBaseTask
#from HostedREST.hosted_taskqueue import HostedTaskQueue
from common_task import CommonTask
from AWREST.aw_device import AWDevice 

class TestEnrollmentDecisionTQP(object):
	"""
	"""
	def __init__(self):
		self.account_id = 86
		self.task = CommonTask()
		pass

	def test_addTask(self, tqname=None, creator=3, type=1, evt=None):
		"""
		To do:
			Simulate to add Enrollment task in enrollment decision task queue by User and Group Sync TQP
		Param:
			creator : 
				1 - Notification Service
				3 - User and Group Sync TQP
				4 - Enrollment Decision TQP
			type : 
				1 - Enrollment task
				2 - De-enrollment task
			Status : 1 - Normal task
		"""
		evt = json.dumps(evt)
		self.task.do_add(account=self.account_id, tqname=tqname, creator=creator, type=type, evt=evt)
		pass

	def test_getEventFromTask(self, tqname=None):
		tk = self.task.do_getTask(account=self.account_id, tqname=tqname)
		print 'Got task name is', tk['name']
		print tk
		event = self.task.do_getEventFromTask(task=tk)
		return event
		pass

	def test_getDeviceInfoFromAW(self, device_id):
		"""
		"""
		device = AWDevice(self.account_id)
		d = device.get(device_id)
		print d
		return d

	def test_EnrollmentDecisionTPQ(self, type=None):
		print type
		evt1 = {
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
		evt2 = {
				"EventId":39,
				"MACAddress":"System.Byte[]",
				"EventTime":"/Date(1368076258271)/",
				"ComplianceStatus":"NotAvailable",
				"Udid":"",
				"EventType":"BreakMDMConfirmed",
				"SerialNumber":"861348SXA4S",
				"CompromisedStatus":"",
				"EnrollmentEmailAddress":"",
				"DeviceFriendlyName":"Hang's iPhone",
				"PhoneNumber":"+8613426192820",
				"DeviceId":616,
				"EnrollmentStatus":"Unenrolled",
				"EnrollmentUserName":"",
				"CompromisedTimeStamp":"/Date(1368076279347)/"
				}
		if type == 1:
			self.test_addTask(tqname='enrollment', creator=3, type=1, evt=evt1)
		else:
			self.test_addTask(tqname='enrollment', creator=1, type=2, evt=evt2)

		event = self.test_getEventFromTask(tqname='enrollment')
		event = eval(event)
		print event
		event_id = event['EventId']
		device_id = event['DeviceId']
		print 'device id :', device_id
		if event_id == 148:
			print 'iOS Enrollment task'
		elif event_id == 39:
			print 'De-enrollment task'

		device = self.test_getDeviceInfoFromAW(device_id)
		os_info = device['OperatingSystem']
		platform = device['Platform']

		print 'device platform is :', platform
		print 'device os version is :', os_info
		os = os_info[0]
		if platform == 'Apple':
			if os > '4':
				print 'Supported OS Version'
				if event_id == 148:
					print 'iOS Enrollment task'
					self.test_addTask(tqname='iosdeploy', creator=4, type=1, evt=evt1)
					event = self.test_getEventFromTask(tqname='iosdeploy')
					print event
				elif event_id == 39:
					print 'De-enrollment task'
					self.test_addTask(tqname='iosdeploy', creator=4, type=2, evt=evt2)
					event = self.test_getEventFromTask(tqname='iosdeploy')
					print event
			else:
				print 'Not supported OS Version'

		pass

if __name__=='__main__':
		ed_tqp = TestEnrollmentDecisionTQP()
		#ed_tqp.test_EnrollmentDecisionTPQ(type=1)
		ed_tqp.test_EnrollmentDecisionTPQ(type=2)

