import cv2
import time
from threading import Thread
import requests
import json
import io
import numpy as np

# Make this compatible across versions
try:
	from queue import Queue
except:
	from Queue import Queue

class Client:
	def __init__(self, addr='http://security-server:50000', api_path='/api/test', queueSize=256):
		# Request info
		self.addr = addr+api_path
		content_type = 'image/jpg'
		self.header = {'content-type', content_type}
		# Queue info
		self.responseQ = Queue(maxsize=queueSize)
		self.decodeQ = Queue(maxsize=queueSize)
		# Timing
		self.delay = 0.1
		self.timeout = 5

	def requestor(self):
		while True:
			print('Sending request')
			t = time.time()
			response = requests.get(self.addr, timeout=self.timeout)
			print('Got response in ' + str(time.time()-t))
			if not self.responseQ.full():
				self.responseQ.put(response.content)

	def decode(self):
		while True:
			if self.responseQ.qsize() > 0:
				t = time.time()
				img = cv2.imdecode(np.fromstring(self.responseQ.get(), np.uint8), cv2.IMREAD_COLOR)
				if not self.decodeQ.full():
					self.decodeQ.put(img)
				print('Decoded image in ' + str(time.time()-t))
			time.sleep(self.delay)

	def render(self):
		while True:
			if self.decodeQ.qsize() > 0:
				t = time.time()
				cv2.imshow("image", cv2.resize(self.decodeQ.get(), (640,480)))
				cv2.waitKey(1)
				print('Displayed new frame in ' + str(time.time()-t))


if __name__ == '__main__':
	client = Client()

	requestThread = Thread(target = client.requestor)
	decodeThread = Thread(target = client.decode)
	renderThread = Thread(target = client.render)

	requestThread.start()
	time.sleep(0.3)
	decodeThread.start()
	renderThread.start()
