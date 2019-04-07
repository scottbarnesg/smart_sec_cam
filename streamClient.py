import cv2
import time
import datetime
from threading import Thread
import requests
import json
import io
import os
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
		self.delay = 0.05
		self.timeout = 5

	def requestor(self):
		while True:
			print('Sending request')
			t = time.time()
			response = requests.get(self.addr, timeout=self.timeout)
			print('Got response in ' + str(time.time()-t))
			if not self.responseQ.full():
				self.responseQ.put(response.content)
			time.sleep(self.delay)

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

	def write(self):
		self.fourcc = cv2.VideoWriter_fourcc(*'MPEG')
		date = datetime.datetime.now()
		path = "bin/videos/" + str(date.month) + '-' + str(date.day) + '-' + str(date.year)
		if not os.path.exists(path):
			os.makedirs(path)
		print('Videos will be saved to: ' + path)
		vid_writer = cv2.VideoWriter(path+'/'+str(date.hour)+'-'+str(date.minute)+'.avi', self.fourcc, 10, (640,480))
		while True:
			if self.decodeQ.qsize() > 0:
				t = time.time()
				print('Queue size: ' + str(self.decodeQ.qsize()))
				frame = cv2.resize(self.decodeQ.get(), (640,480))
				vid_writer.write(frame)
				print('Wrote new frame in: ' + str(time.time()-t))
			time.sleep(0.05)
		vid_writer.release()


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--capture_delay', help='Delay between images (s)', default='0.05')
	parser.add_argument('--video_length', help='Length of Each Video (s)', default='3600')
	parser.add_argument('--camera_port', help='USB port for webcam', default='0')
	parser.add_argument('--render', help='Render the video stream', default='True')
	parser.add_argument('--write', help='Save video locally', default='False')
	parser.add_argument('--addr', help='Server address', default='security-server')
	args = parser.parse_args()

	if args.write == 'True' and args.render == 'True':
		raise ValueError('You cannot write and render in a single client. Please use two client instances')

	client = Client()

	requestThread = Thread(target = client.requestor)
	decodeThread = Thread(target = client.decode)
	if args.render == 'True':
		renderThread = Thread(target = client.render)
	if args.write == 'True':
	 	writeThread = Thread(target = client.write)

	requestThread.start()
	time.sleep(0.3)
	decodeThread.start()
	if args.render == 'True':
 		renderThread.start()
	if args.write == 'True':
		writeThread.start()
