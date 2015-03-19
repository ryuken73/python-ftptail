# -*-coding: utf-8 -*-
'''
thanks to https://github.com/johntdyer/ftptail/blob/master/ftptail
Usage :
'''
import logging
import ftplib
import time
import sys


class FtpLog():

	def init(self, host, id, passwd, fname):
		self.host    = host
		self.id      = id
		self.passwd  = passwd
		self.fname   = fname
		self.size    = 0
		self.osSep   = '\n' # need to change os.linesep but, how to know remote system's line seperator?
		self.remain  = ''

	def connect(self):
		try :
			self.ftpSession = ftplib.FTP(self.host, self.id, self.passwd)
			self.ftpSession.sendcmd('TYPE i')
		except :
			logging.error('[+]ftp connect error. check your connect infomation')
			sys.exit(1)

	def tail(self) :
		self.addSize(self.ftpSession.size(self.fname))
		while True :
			self.ftpSession.retrbinary('RETR ' + self.fname, self.callback, 1024, self.getSize())
			time.sleep(1)

	def cat(self):
		self.ftpSession.retrbinary('RETR ' + self.fname, self.callback, 1024)


	def callback(self, rawData):
		# Data can be below
		#    am a boy \n (line sep) you are a girl \n (line sep) he is a
		# Need make like this
		#    I am a boy \n (line sep) you are a girl

		outList = self.mkCompleteLine(rawData)
		for line in outList :
			print line
			#pass

		self.addSize(len(rawData))

	def mkCompleteLine(self, ftpRawData):
		# input  : string  ftpRawData
		# output : list    complete lines

		# first : add previously remained data
		logging.debug("%s", '*'*100)
		logging.debug("self.remain 1 : %s", self.remain)
		logging.debug("ftpRawData 1 : %s", '----'+ftpRawData+'----')
		datafrontAdded = self.remain + ftpRawData

		# second : make complete line

		if datafrontAdded.count(self.osSep) == 0 :
			logging.debug("still not line")
			# datafrontAdded is still not even 1 line!!
			# so, save remain and return []
			self.remain = datafrontAdded
			return []

		else :
			logging.debug("contain at least 1 line")
			# datafrontAdded has at least 1 line

			if datafrontAdded[-1:] != self.osSep :

				# datafrontAdded has extra data after last line separator, so save remains
				indexLastLineSep = datafrontAdded.rindex(self.osSep)
				self.remain =  datafrontAdded[indexLastLineSep + 1:]

				# cut off remaining data and return result list
				dataComplete = datafrontAdded[:indexLastLineSep]
				logging.debug("has more data after last line sep")
				logging.debug("self.remain 2 : %s", self.remain)
				logging.debug("dataComplete 2 : %s", '++++' + dataComplete + '++++')

			else :
				logging.debug("already complete line")
				# datafrontAdded has no more data after line separator
				# so return whole data ( reset remain data )
				self.remain  = ''
				dataComplete = datafrontAdded[:-1] # remove last os separator
				logging.debug("dataComplete 3 : %s", '$$$$' + dataComplete + '$$$$')

			return dataComplete.split(self.osSep)


	def addSize(self, currentSize):
		self.size += currentSize

	def getSize(self):
		return self.size




if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
	logfile = FtpLog()
	logfile.init('ftp server address', 'ftp account', 'ftp passwd', 'file path to tail')
	logfile.connect()
	logfile.tail()
