import NotificationSimu
import time
import base64
import unittest
import hosted_taskqueue
import logging
import ConfigParser
import string
import json
import os
import xmlrunner
import sys

sys.path.append("/opt/mailcontrol/modules/MDMi/HostedREST")
sys.path.append("/opt/mailcontrol/modules/MDMi/utils")
#print sys.path

TQ_DATA = "testdata/tq_data.txt"
TEST_DATA = ConfigParser.ConfigParser()
TEST_DATA.read(TQ_DATA)
logging.basicConfig(
                          filename = 'hosted-restlib-tq.log',                                                                           format = "%(asctime)s - %(name)s - %(levelname)s %(message)s",
                          level = logging.DEBUG
                   )
def parse_result(data):
    if data.content_length > 0:
        if data.content_type == "application/json":
            return json.loads(data.content)
    return data.content

class Test1NotificationServer(unittest.TestCase):
    """
    For TMS-481 As notification service, I want to create a User&Group Sync task upon receiving a successful enrollment notification event (JSON format) from service gateway (no authentication)
    """
    def setUp(self):
        self.notification=NotificationSimu.NotificationSimu()
        self.account_id = string.atoi(TEST_DATA.get("Account", "account_id"))
        self.tq = hosted_taskqueue.HostedTaskQueue()
        self.error_task_name = 99999999
        self.tasks_list = []
        self.tasks_num = 0
#       user_group_sync_task.do_test()
    def tearDown(self):
        del self.tq
        del self.notification
    def test_validEroll(self):
        """
        TODO: 
        Send valid enroll event
        Get a task informantion
        Base64 decode payload
        Compare task schema
        Resource:
            /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-usergroup/task-{TASK}
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
        self.clearusergrouptask(tqname,account)
        status=self.notification.deviceEnrollSimu(False)
        time.sleep(5)
#        self.verifytaskqueue(tqname,account)
        self.verify_payload(status)
    def clearusergrouptask(self,tqname,accountid):  
        """
        Delete usergroup task queue and than build usergroup task
        """           
        os.popen("curl -H Accept:application/json --user 'cn=mailcontrol (admin),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg' -k -X DELETE https://cog01o:8085/tq/v-1/account-%s/namespace-mobile/taskqueue-%s;" % (accountid,tqname))
        os.popen("""curl -H Accept:application/json --user 'cn=mailcontrol (admin),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg' -k https://cog01o:8085/tq/v-1/account-%s/namespace-mobile/taskqueue-%s -X PUT -d '
{
    "description": "unique taskqueue",
    "max_leases": "20"
}'""" % (accountid,tqname))

    def verifytaskqueue(self,tqname,accountid):
        """
        Check whether the usergroup task queue has task or not
        """
        f=os.popen("curl -H Accept:application/json --user 'cn=mailcontrol (admin),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg' -k -X POST 'https://cog01o:8085/tq/v-1/account-%d/namespace-mobile/taskqueue-%s/search? '" % (accountid,tqname))
#        print type(f)
        li=list(f)
        self.assertEqual(len(li),1) 
    def verify_payload(self,status):
        """
        Compare the event schema with task schema
        """
        if status ==200:
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
            task_payload=task['payload_base64']
            task_decod=base64.decodestring(task_payload)
#           print task_decod
            task_dict=eval(task_decod)
#           print task_dict[event][EventId]
#           print type(task_dict)
#           print task_dict['event']
            tttt=eval(task_dict['event'])
#           print type(tttt)
#           print tttt.keys()
#            for key in tttt:
#                print key, tttt[key]
        
            EventId = TEST_DATA.get("Params", "EventId")
            self.assertEqual(int(EventId),tttt['EventId'])
            EnrollmentUserName = TEST_DATA.get("Params", "EnrollmentUserName")
            self.assertEqual(EnrollmentUserName,tttt['EnrollmentUserName'])
            DeviceId = TEST_DATA.get("Params", "DeviceId")
            self.assertEqual(int(DeviceId),tttt['DeviceId'])
            EnrollmentEmailAddress = TEST_DATA.get("Params", "EnrollmentEmailAddress")
            self.assertEqual(EnrollmentEmailAddress,tttt['EnrollmentEmailAddress'])
            EventType = TEST_DATA.get("Params", "EventType")
            self.assertEqual(EventType,tttt['EventType'])
        else:
            logging.debug("the code dont equal 200,there has an error!!!")
            
    def test_invalidEnroll(self):
        """
        TODO: Send the event that miss EnrollmentUserName
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
        accountid = self.account_id
        self.clearusergrouptask(tqname,accountid)
        status=self.notification.invalidEnrollSimu(False)
        time.sleep(5)
        self.assertEqual(status,406)
        self.verifytaskqueue(tqname,accountid)
    def test_wrongFormatEnroll(self):
        """
        TODO: 
        Send wrong format event,like miss headers in event
        Resource:
            /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-usergroup/addtasks
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
        accountid = self.account_id
        self.clearusergrouptask(tqname,accountid)
        status=self.notification.wrongFormatEnrollSimu(False)
        time.sleep(5)
        self.assertEqual(status,400)
        self.verifytaskqueue(tqname,accountid)
    def test_deviceUnEnroll(self):
        """
        TODO: 
        Send invalid enroll event,like this is a uneroll event
        Resource:
            /tq/v-1/account-{ACCOUNT}/namespace-{NAMESPACE}/taskqueue-usergroup/addtasks
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
        accountid = self.account_id
        self.clearusergrouptask(tqname,accountid)
        status=self.notification.deviceUnEnrollSimu(False)
        time.sleep(5)
        self.assertEqual(status,500)
        self.verifytaskqueue(tqname,accountid)
    
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

if __name__=='__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='/tmp/output/test-reports'))
