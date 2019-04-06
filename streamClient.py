import cv2
import time
from queue import Queue
from threading import Thread
import requests
import json
import io
from PIL import Image
import numpy as np

class Client:
	def __init__(self, addr='http://192.168.1.218:50000', api_path='/api/test'):
		self.addr = addr+api_path
		content_type = 'image/jpg'
		self.header = {'content-type', content_type}

	def run(self):
		while True:
			print('Sending request')
			t = time.time()
			response = requests.get(self.addr)
			print('Got response in ' + str(time.time()-t))
			self.img = cv2.imdecode(np.fromstring(response.content, np.uint8), cv2.IMREAD_COLOR)
			cv2.imshow("image", cv2.resize(client.img, (640,480)))
			cv2.waitKey(1)

class Streamer():
	def __init__(self, path, queueSize=256):
		# self.stream = cv2.VideoCapture(path)
		self.client = Client()
		self.Q = Queue(maxsize=queueSize)
		self.delay = 90
		self.sleepTime = 0.01

	def read(self):
		return self.Q.get()

	def QNotEmpty(self):
		return self.Q.qsize() > 0

	def update(self):
		while True:
			# print self.Q.qsize()
			if not self.Q.full():
				# resp =
				ret, frame = self.stream.read()
				if ret:
					self.Q.put(frame)
			else:
				time.sleep(self.sleepTime)

	def dynamicUpdate(self):
		if self.Q.qsize() < 50:
			self.sleepTime += 1e-3
		elif self.Q.qsize() > 50 and self.sleepTime > 0.01:
			self.sleepTime -= 1e-3
		print(self.sleepTime)

	def dynamicFPS(self):
		if self.Q.qsize() > 100 and self.delay > 90:
			self.delay -= 1
		elif self.Q.qsize() < 100:
			self.delay += 1
			self.update()

	def render(self):
		while True:
			# self.dynamicFPS()
			if self.QNotEmpty():
				frame = self.read()
				cv2.imshow("image", frame)
				cv2.waitKey(self.delay)
			else:
				print ('Queue Empty')
				time.sleep(0.1)

	def run(self):
		updaterThread = Thread(target = self.update)
		renderThread = Thread(target = self.render)

		updaterThread.start()
		time.sleep(2)
		renderThread.start()


if __name__ == '__main__':
	client = Client()
	client.run()
	# print(np.shape(response))
	# path = '/home/scott/smart_sec_cam/bin/videos17/recording0.avi'
	# streamer = Streamer(path)
	# streamer.run()
