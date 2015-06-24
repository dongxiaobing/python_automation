import plistlib
import sys

def save_file(filename, content):
	if filename and content:
		fd = open(filename, 'w')
		fd.write(content)
		fd.close()

class ParsePayloadFile(object):
	def __init__(self):
		#self.payloadfile_name = 'airwatch.mobileconfig'
		self.payloadfile_name = sys.argv[1]
		self.pacfile_name = 'pacfile'
		self.passinfile_name = 'passin'
		self.p12file_name ='user.p12'

	def __del__(self):
		pass

	def parse_payloadfile(self):
		fd = open(self.payloadfile_name, 'r')
		#fd = open(sys.argv[1], "r")
		text = fd.readlines()
		fd.close()
	
     		content = ''
		for item in text:
			if item.find('<?xml') >= 0:
				start_pos = item.find('<?xml')
				end_pos = item.find('?>') + 3
				content = item[start_pos:end_pos]
				continue
	
			if item.find('</plist>') == -1:
				content = content + item
			else:
				content = content + item
				break
	#	save_file('content.txt', content)
	#	print content	
		if content:
			pl = plistlib.readPlistFromString(content)		
			if pl:
				#print pl
				pl_content = pl['PayloadContent']
				for item in pl_content:
					#print item
					if item.has_key('Proxies'):
						save_file(self.pacfile_name, item['Proxies']['ProxyAutoConfigURLString'])
					if item.has_key('Password'):
						save_file(self.passinfile_name, item['Password'])
						#save_file('user.b64', item['PayloadContent'].data)
						save_file(self.p12file_name, item['PayloadContent'].data)
	
if __name__ == '__main__':
	pp = ParsePayloadFile()
	pp.parse_payloadfile()
