#! /usr/bin/python
#FileName: BaseModule.py
import ConfigParser
TQ_DATA = "testdata/tq_data.txt"
TEST_DATA = ConfigParser.ConfigParser()
TEST_DATA.read(TQ_DATA)
class BaseSimu:
    def __init__(self):
        """
            initialize server configuration, username and password are used for access authentication
        """
        self.host = TEST_DATA.get("Connection", "Host")
        self.port = TEST_DATA.get("Connection", "Port")
        self.username = TEST_DATA.get("Connection", "Username")
        self.password = TEST_DATA.get("Connection", "Password")
