#!/usr/bin/python

"""
Hosted Task Queue API Test
Documentation for this module.

please update tqname in the testdata/tq_data.txt for different task queue test:
1. usergroup - user group sync Task Queue
2. enrollment - for Enrollment Decision Task Queue
3. iosdeploy - for iOS deployment Task Queue
4. android - for Android deployment Task Queue
"""

import unittest, xmlrunner
import logging
import ConfigParser
import string
import json
if not os.path.join( os.getcwd(), '../..' ) in sys.path:
	sys.path.append(os.path.join( os.getcwd(), '../..' ))
import HostedREST.hosted_taskqueue

TQ_DATA = "testdata/tq_data.txt"

logging.basicConfig(
		                  filename = 'hosted-restlib-tq.log',									                                        format = "%(asctime)s - %(name)s - %(levelname)s %(message)s",
						  level = logging.DEBUG
				   )

def parse_result(data):
	if data.content_length > 0:
		if data.content_type == "application/json":
			return json.loads(data.content)
	return data.content

TEST_DATA = ConfigParser.ConfigParser()
TEST_DATA.read(TQ_DATA)

class Test1TaskQueue(unittest.TestCase):
	"""
	Provides access to Task Queues.
	"""
	def setUp(self):
		"""
		The constructor.
		Create a new task queue instance.		
		"""
		self.account_id = string.atoi(TEST_DATA.get("Account", "account_id"))
		self.tq = hosted_taskqueue.HostedTaskQueue()
		self.error_task_name = 99999999
		self.tasks_list = []
		self.tasks_num = 0

	def tearDown(self):
		del self.tq
	
	def do_parse(self, datastr):
		"""
		TODO: Parses data string into base task struct dict.
		Params:
			datastr: Task struct string.
		Return:
			LIST of the task struct dict.
			Number of the tasks
			Exception message.
		"""
		try:
			jsonobj = json.loads(datastr, encoding="utf-8")
			self.tasks_num = len(jsonobj)
			idx = 0
			while idx < self.tasks_num:
				item = {
						'owner' : jsonobj[idx]['owner'],
						'priority' : jsonobj[idx]['priority'],
						'enqueue_timestamp' : jsonobj[idx]['enqueue_timestamp'],
						'account' : int(jsonobj[idx]['account']),
						'name' : int(jsonobj[idx]['name']),
						'tags' : jsonobj[idx]['tags'],
						'http_last_modified' : jsonobj[idx]['http_last_modified'],
						'task_retries' : int(jsonobj[idx]['task_retries']),
						'payload_base64' : jsonobj[idx]['payload_base64'],
						}
				self.tasks_list.append(item)
				idx = idx + 1
			if len(self.tasks_list) is not self.tasks_num:
				logging.debug('Parse task error!')
				raise Exception('Parse task error!')
			return self.tasks_list, self.tasks_num
		except Exception, e:
			logging.debug(e)
			raise Exception('Invalid input! %s' % e)
		pass

	def test_add(self):
		"""
		TODO: Add one task
		Resource:
			/tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/addtasks
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			payload: Base64 encode string.
		    tags: Tags in the task.
			priority: Priority of the task.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		payload = TEST_DATA.get("Task Queue", "payload")
		tags = eval(TEST_DATA.get("Task Queue", "tags"))
		priority = TEST_DATA.get("Task Queue", "priority")
		
		result = self.tq.do_add(tqname=tqname, account=account, payload=payload, tags=tags, priority=priority)
		logging.debug("Insert new task in to task queue: %s, the http return code is: %d", tqname, result.code)
		self.assertEqual(result.code, 201)

	def test_add_error(self):
		"""
		TODO: Negative test for Add one task
        Resource:
        	/tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/addtasks
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			payload: Base64 encode string.
		    tags: Tags in the task.
			priority: Priority of the task.
		"""
		tqname = TEST_DATA.get("Task Queue", "error_tqname")
		account = self.account_id
		payload = TEST_DATA.get("Task Queue", "payload")
		tags = eval(TEST_DATA.get("Task Queue", "tags"))
		priority = TEST_DATA.get("Task Queue", "priority")
		
		result = self.tq.do_add(tqname=tqname, account=account, payload=payload, tags=tags, priority=priority)
		logging.debug("Insert new task in to task queue: %s, the http return code is: %d", tqname, result.code)
		self.assertEqual(result.code, 500)

	def non_test_get(self):
		"""
		TODO: Get one task information.
		Resource:
			/tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/task-{TASK}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			taskname: Name of the specific task.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		#taskname = TEST_DATA.get("Task Queue", "search_taskname")
		task = self.get_task()
		taskname = task['name']
		result = self.tq.do_get(tqname=tqname, account=account, taskname=taskname)
		u = parse_result(result)
		logging.debug(u)
		self.assertEqual(result.code, 200)
		self.assertEqual(u['name'], str(taskname))
	
	def non_test_delete(self):
		"""
		TODO: Delete task
		Resourece: 
			/tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/task-{TASK}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			taskname: Name of the specific task.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		#taskname = TEST_DATA.get("Task Queue", "search_taskname")
		task = self.get_task()
		taskname = task['name']
		result = self.tq.do_delete(tqname=tqname, account=account, taskname=taskname)
		u = parse_result(result)
		logging.debug(u)
		self.assertEqual(result.code, 204)
	
	def non_test_delete_error(self):
		"""
		TODO: Negative test for Delete task
		Resourece: 
			/tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/task-{TASK}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			taskname: Name of the specific task.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		#task = self.get_task()
		taskname = self.error_task_name
		result = self.tq.do_delete(tqname=tqname, account=account, taskname=taskname)
		u = parse_result(result)
		logging.debug(u)
		self.assertEqual(result.code, 204)
	
	def non_test_update(self):
		"""
		TODO: Update task
		Resource:
			PUT /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/task-{TASK}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			taskname: Name of the specific task.
			payload: Base64 encode string.
			tags: Tags in the task.
			priority: Priority of the task.
			enqueuetime: Last modify time.
		Return:
			Instance object of class RestResult;			
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		#taskname = TEST_DATA.get("Task Queue", "search_taskname")
		task = self.get_task()
		taskname = task['name']
		enqueuetime = task['http_last_modified']
		payload = TEST_DATA.get("Task Queue", "payload")
		tags = eval(TEST_DATA.get("Task Queue", "tags"))
		result = self.tq.do_update(tqname=tqname, account=account, taskname=taskname, payload=payload, tags=tags, enqueuetime=enqueuetime)
		u = parse_result(result)
		logging.debug(u)
		self.assertEqual(result.code, 204)
		#self.assertEqual(u['name'], str(taskname))
	
	def non_test_update_error(self):
		"""
		TODO: Negative test for Update task
		Resource:
			PUT /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/task-{TASK}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			taskname: Name of the specific task.
			payload: Base64 encode string.
			tags: Tags in the task.
			priority: Priority of the task.
			enqueuetime: Last modify time.
		Return:
			Instance object of class RestResult;			
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		task = self.get_task()
		taskname = self.error_task_name
		enqueuetime = task['http_last_modified']
		payload = TEST_DATA.get("Task Queue", "payload")
		tags = eval(TEST_DATA.get("Task Queue", "tags"))
		result = self.tq.do_update(tqname=tqname, account=account, taskname=taskname, payload=payload, tags=tags, enqueuetime=enqueuetime)
		u = parse_result(result)
		logging.debug(u)
		self.assertEqual(result.code, 412)

	def non_test_get_error(self):
		"""
		TODO: Negative test for Get one task information.
		Resource:
			/tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/task-{TASK}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			taskname: Name of the specific task.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		taskname = self.error_task_name
		result = self.tq.do_get(tqname=tqname, account=account, taskname=taskname)
		u = parse_result(result)
		logging.debug(u)
		self.assertEqual(result.code, 404)

	def non_test_get_multi(self):
		"""
		TODO: Get tasks' information.
		Resource:
			POST /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/search?{QUERY_PARAMS}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			tasknum: Number of the tasks that expected.
			tags: Search conditions.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		tasknum = TEST_DATA.get("Task Queue", "tasknum")
		tags = eval(TEST_DATA.get("Task Queue", "search_tags"))
		result = self.tq.do_get_multi(tqname=tqname, account=account, tasknum=tasknum, tags=tags)
		jsonobj = json.loads(result.content, encoding="utf-8")
		self.assertEqual(str(len(jsonobj)), tasknum)
		self.assertEqual(result.code, 200)
	
	def non_test_get_multi_error(self):
		"""
		TODO: Negative Test for Get tasks' information.
		Resource:
			POST /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/search?{QUERY_PARAMS}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			tasknum: Number of the tasks that expected.
			tags: Search conditions.
		Return:
			Instance object of class RestResult;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		tasknum = TEST_DATA.get("Task Queue", "tasknum")
		tags = eval(TEST_DATA.get("Task Queue", "error_search_tags"))
		result = self.tq.do_get_multi(tqname=tqname, account=account, tasknum=tasknum, tags=tags)
		jsonobj = json.loads(result.content, encoding="utf-8")
		self.assertEqual(len(jsonobj), 0)
		self.assertEqual(result.code, 200)

	def get_task(self):
		"""
		TODO: Get out one task out from a task queue.		
		Resource:
			POST /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-{TASKQUEUE}/search?{QUERY_PARAMS}
		Params:
			tqname: Name of task queue.
			namespace: Namespace of the task queue.
			account: Account ID.
			version: Version of the resource, default value 1.
			tasknum: Number of the tasks that expected.
			tags: Search conditions.
		Return:
			Instance object of class Task;
			Exception message
		"""
		tqname = TEST_DATA.get("Task Queue", "tqname")
		account = self.account_id
		#Tasknum = TEST_DATA.get("Task Queue", "tasknum")
		tasknum = 1
		tags = eval(TEST_DATA.get("Task Queue", "search_tags"))
		result = self.tq.do_get_multi(tqname=tqname, account=account, tasknum=tasknum, tags=tags)
		self.tasks_list = []
		self.tasks_num = 0
		self.do_parse(result.content)
		return self.tasks_list[0]

if __name__ == '__main__':
	    #unittest.main(testRunner=xmlrunner.XMLTestRunner(output='/tmp/output/test-reports'))
	    unittest.main()
