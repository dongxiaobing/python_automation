#! /usr/bin/python
#FileName: NotificationSimu.py
from BaseModule import BaseSimu 
import urllib
import httplib
import base64
import json
import ConfigParser
TQ_DATA = "testdata/tq_data.txt"
TEST_DATA = ConfigParser.ConfigParser()
TEST_DATA.read(TQ_DATA)

class NotificationSimu(BaseSimu):
    def __init__(self):
        BaseSimu.__init__(self)
#        print "initial Simulator host:%s, userName:%s, password:%s"%(self.host, self.username, self.password)

    def deviceEnrollSimu(self, basicAuth):
        """
            this method is used for simulating air-watch device enroll event
        """
        headers = {"Content-type": "application/json","Accept": "application/json"}
        if basicAuth:
            auth = base64.encodestring(self.username + ':' + self.password)
            headers["Authorization"] = "Basic "+auth
        params= {
            "EventId":int(TEST_DATA.get("Params", "EventId")),
            "MACAddress":TEST_DATA.get("Params", "MACAddress"),
            "EventTime":TEST_DATA.get("Params", "EventTime"),
            "ConplianceStatus":TEST_DATA.get("Params", "ConplianceStatus"),
            "Udid":TEST_DATA.get("Params", "Udid"),
            "EventType":TEST_DATA.get("Params", "EventType"),
            "SerialNumber":TEST_DATA.get("Params", "SerialNumber"),
            "CompromisedStatus":TEST_DATA.get("Params", "CompromisedStatus"),
            "EnrollmentEmailAddress":TEST_DATA.get("Params", "EnrollmentEmailAddress"),
            "DeviceFriendlyName":TEST_DATA.get("Params", "DeviceFriendlyName"),
            "PhoneNumber":TEST_DATA.get("Params", "PhoneNumber"),
            "DeviceId":int(TEST_DATA.get("Params", "DeviceId")),
            "EnrollmentStatus":TEST_DATA.get("Params", "EnrollmentStatus"),
            "EnrollmentUserName":TEST_DATA.get("Params", "EnrollmentUserName"),
            "CompromisedTimeStamp":TEST_DATA.get("Params", "CompromisedTimeStamp")
        }
        conn = httplib.HTTPSConnection(self.host, self.port)
        conn.request("POST", "/cgi-py/ns.py", json.dumps(params), headers)
        response = conn.getresponse()
#        print response.status
#        print response.read().strip()
        return response.status
     
    def invalidEnrollSimu(self, basicAuth):
        """
            this method is used for simulating air-watch devicen invalid enroll event,miss EnrollmentUserName
        """
        headers = {"Content-type": "application/json","Accept": "application/json"}
        if basicAuth:
            auth = base64.encodestring(self.username + ':' + self.password)
            headers["Authorization"] = "Basic "+auth
        params= {
            "EventId":int(TEST_DATA.get("Params", "EventId")),
            "MACAddress":TEST_DATA.get("Params", "MACAddress"),
            "EventTime":TEST_DATA.get("Params", "EventTime"),
            "ConplianceStatus":TEST_DATA.get("Params", "ConplianceStatus"),
            "Udid":TEST_DATA.get("Params", "Udid"),
            "EventType":TEST_DATA.get("Params", "EventType"),
            "SerialNumber":TEST_DATA.get("Params", "SerialNumber"),
            "CompromisedStatus":TEST_DATA.get("Params", "CompromisedStatus"),
            "EnrollmentEmailAddress":TEST_DATA.get("Params", "EnrollmentEmailAddress"),
            "DeviceFriendlyName":TEST_DATA.get("Params", "DeviceFriendlyName"),
            "PhoneNumber":TEST_DATA.get("Params", "PhoneNumber"),
            "DeviceId":int(TEST_DATA.get("Params", "DeviceId")),
            "EnrollmentStatus":TEST_DATA.get("Params", "EnrollmentStatus"),
            "CompromisedTimeStamp":TEST_DATA.get("Params", "CompromisedTimeStamp")
        }
        conn = httplib.HTTPSConnection(self.host, self.port)
        conn.request("POST", "/cgi-py/ns.py", json.dumps(params), headers)
        response = conn.getresponse()
        #print response status
        #print response.read().strip()
        return response.status  
    def deviceUnEnrollSimu(self, basicAuth):
        """
            this method is used for simulating air-watch device un enroll event
        """
        headers = {"Content-type": "application/json","Accept": "application/json"}
        if basicAuth:
            auth = base64.encodestring(self.username + ':' + self.password)
            headers["Authorization"] = "Basic "+auth
        params= {            
            "EventId":int(TEST_DATA.get("Params", "EventIdOther")),
            "MACAddress":TEST_DATA.get("Params", "MACAddress"),
            "EventTime":TEST_DATA.get("Params", "EventTime"),
            "ConplianceStatus":TEST_DATA.get("Params", "ConplianceStatus"),
            "Udid":TEST_DATA.get("Params", "Udid"),
            "EventType":TEST_DATA.get("Params", "EventType"),
            "SerialNumber":TEST_DATA.get("Params", "SerialNumber"),
            "CompromisedStatus":TEST_DATA.get("Params", "CompromisedStatus"),
            "EnrollmentEmailAddress":TEST_DATA.get("Params", "EnrollmentEmailAddress"),
            "DeviceFriendlyName":TEST_DATA.get("Params", "DeviceFriendlyName"),
            "PhoneNumber":TEST_DATA.get("Params", "PhoneNumber"),
            "DeviceId":int(TEST_DATA.get("Params", "DeviceId")),
            "EnrollmentStatus":TEST_DATA.get("Params", "EnrollmentStatus"),
            "EnrollmentUserName":TEST_DATA.get("Params", "EnrollmentUserName"),
            "CompromisedTimeStamp":TEST_DATA.get("Params", "CompromisedTimeStamp")
        }
        conn = httplib.HTTPSConnection(self.host, self.port)
        conn.request("POST", "/cgi-py/ns.py", json.dumps(params), headers)
        response = conn.getresponse()
        return response.status

    def wrongFormatEnrollSimu(self, basicAuth):
        """
            this method is used for simulating air-watch device wrong format enroll event
        """
        headers = {"Content-type": "application/json"}
        if basicAuth:
            auth = base64.encodestring(self.username + ':' + self.password)
            headers["Authorization"] = "Basic "+auth

        params = {            
            "EventId":int(TEST_DATA.get("Params", "EventId")),
            "MACAddress":TEST_DATA.get("Params", "MACAddress"),
            "EventTime":TEST_DATA.get("Params", "EventTime"),
            "ConplianceStatus":TEST_DATA.get("Params", "ConplianceStatus"),
            "Udid":TEST_DATA.get("Params", "Udid"),
            "EventType":TEST_DATA.get("Params", "EventType"),
            "SerialNumber":TEST_DATA.get("Params", "SerialNumber"),
            "CompromisedStatus":TEST_DATA.get("Params", "CompromisedStatus"),
            "EnrollmentEmailAddress":TEST_DATA.get("Params", "EnrollmentEmailAddress"),
            "DeviceFriendlyName":TEST_DATA.get("Params", "DeviceFriendlyName"),
            "PhoneNumber":TEST_DATA.get("Params", "PhoneNumber"),
            "DeviceId":int(TEST_DATA.get("Params", "DeviceId")),
            "EnrollmentStatus":TEST_DATA.get("Params", "EnrollmentStatus"),
            "EnrollmentUserName":TEST_DATA.get("Params", "EnrollmentUserName"),
            "CompromisedTimeStamp":TEST_DATA.get("Params", "CompromisedTimeStamp")
        }        
    
        conn = httplib.HTTPSConnection(self.host, self.port)
        conn.request("POST", "urlxxxxxx", json.dumps(params), headers)
        response = conn.getresponse()
#       print response.status
#       print response.read().strip()
        return response.status

    def deviceWipeSimu(self, basicAuth):
        """
            this method is used for simulating air-watch device wipe event
        """
        if basicAuth:
            auth = base64.encodestring(self.username + ':' + self.password)
            headers["Authorization"] = "Basic "+auth

        params = {
            "EventId":int(TEST_DATA.get("Params", "EventId")),
            "MACAddress":TEST_DATA.get("Params", "MACAddress"),
            "EventTime":TEST_DATA.get("Params", "EventTime"),
            "ConplianceStatus":TEST_DATA.get("Params", "ConplianceStatus"),
            "Udid":TEST_DATA.get("Params", "Udid"),
            "EventType":TEST_DATA.get("Params", "EventType"),
            "SerialNumber":TEST_DATA.get("Params", "SerialNumber"),
            "CompromisedStatus":TEST_DATA.get("Params", "CompromisedStatus"),
            "EnrollmentEmailAddress":TEST_DATA.get("Params", "EnrollmentEmailAddress"),
            "DeviceFriendlyName":TEST_DATA.get("Params", "DeviceFriendlyName"),
            "PhoneNumber":TEST_DATA.get("Params", "PhoneNumber"),
            "DeviceId":int(TEST_DATA.get("Params", "DeviceId")),
            "EnrollmentStatus":TEST_DATA.get("Params", "EnrollmentStatus"),
            "EnrollmentUserName":TEST_DATA.get("Params", "EnrollmentUserName"),
            "CompromisedTimeStamp":TEST_DATA.get("Params", "CompromisedTimeStamp")
        }        
 
        conn = httplib.HTTPSConnection(self.host, self.port)
        conn.request("POST", "urlxxxxxx", json.dumps(params), headers)
        response = conn.getresponse()
        #print response status
        print response.read().strip()
        
        

#if __name__ == '__main__':
#    print "start testing......"
#    dev = NotificationSimu()
#    dev.deviceEnrollSimu(False) 
#    print "testing ended......"
