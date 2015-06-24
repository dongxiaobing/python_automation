#!/usr/bin/python

"""
automation test for tms-311 ios enrollment push notification
"""

import base64
import unittest
import logging
import ConfigParser
import string
import json
import sys
import os
sys.path.append("../../task-ios")
sys.path.append("../../utils")
import iosdeploy
import dictutils
import common_task

TQ_DATA = "testdata/tq_data.txt"

logging.basicConfig(
                          filename = 'ios-deployment-pushNotification-enrollment.log',                                                                           
                          format = "%(asctime)s - %(name)s - %(levelname)s %(message)s",
                          level = logging.DEBUG
                   )

def parse_result(data):
    if data.content_length > 0:
        if data.content_type == "application/json":
            return json.loads(data.content)
    return data.content

TEST_DATA = ConfigParser.ConfigParser()
TEST_DATA.read(TQ_DATA)

class TestiOSPushNotificationEnrollment(unittest.TestCase):
    """
    test push notification for enrollment task
    """
    def setUp(self):
        """
        The constructor.
        Create a new task queue instance.       
        """
        self.deploy = iosdeploy.IOSDeploy()
        self.account_id = string.atoi(TEST_DATA.get("Account", "account_id"))
        self.error_task_name = 99999999
        self.tasks_list = []
        self.tasks_num = 0
    
    def get_testdata(self, test_file):
	"""
        get test data from json file
	input: json file name
	output: event (dict)
        """
	temp_filepath = 'testdata/'+test_file
        f = file(temp_filepath)
	temp = json.load(f, object_hook=dictutils.decode_dict)
        return temp
    
    def test_001_task_001_enrollment_proper(self):
	"""
        check pushnotification works properly for proper enrollment event
	compare sendNotification methond result
        """
        test_data = self.get_testdata('valid_task.json')
        print(test_data)
        result = self.deploy.sendNotification(self.account_id, test_data)
        self.assertEqual(result, True)
    
    def test_001_task_001_enrollment_invalid(self):
	"""
        check pushnotification works properly for invalid enrollment event
	compare sendNotification methond result
        """
        test_data = self.get_testdata('invalid_task.json')
        print(test_data)
        result = self.deploy.sendNotification(self.account_id, test_data)
        self.assertEqual(result, None)
    
    def test_001_task_002_invalid_OSVersion(self):
	"""
        check pushnotification works properly for enrollment event with not right ios version
	compare sendNotification methond result
        """
        test_data = self.get_testdata('invalid_osVersion_task.json')
        print(test_data)
        result = self.deploy.sendNotification(self.account_id, test_data)
        self.assertEqual(result, None)
        
if __name__ == '__main__':
    #unittest.main(testRunner=xmlrunner.XMLTestRunner(output='/tmp/output/test-reports'))
    unittest.main()
