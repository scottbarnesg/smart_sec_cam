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
	def __init__(self, username, password, addr='https://security-server:50000', api_path='/api/stream_video', auth_required='True', queueSize=256, delay=0.05, timeout=10, fps=10, vid_len=3600):
		# Request info
		self.addr = addr
		self.api_addr = addr+api_path
		content_type = 'image/jpg'
		self.header = {'content-type', content_type}
		# Queue info
		self.responseQ = Queue(maxsize=queueSize)
		self.decodeQ = Queue(maxsize=queueSize)
		# Timing
		self.delay = delay
		self.timeout = timeout
		# Video
		self.fps = fps
		self.vid_len = vid_len
		# Authentication
		self.username = username
		self.password = password
		self.token = '0'
		self.auth_required = True
		if auth_required == 'False': # Convert to bool
			self.auth_required = False
		if self.auth_required:
			print('Authenticating')
			print(auth_required)
			print(self.auth_required)
			self.authenticate()
		else:
			print('Authentication not required')
		time.sleep(1)

	def authenticate(self):
		response = requests.post(self.addr+'/api/auth', json={'username':self.username, 'password':self.password}, verify=False)
		print(response.content)
		self.token = response.content

	def requestor(self):
		while True:
			print('Sending request')
			t = time.time()
			response = requests.get(self.api_addr, json={'username':self.username, 'token':self.token}, timeout=self.timeout, verify=False)
			print('Got response in ' + str(time.time()-t))
			if "Authentication error" in response.content and self.auth_required:
				print('Attempting to re-authenticate')
				self.authenticate()
			elif not self.responseQ.full():
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
		self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
		while True:
			date = datetime.datetime.now()
			path = "bin/videos/" + str(date.month) + '-' + str(date.day) + '-' + str(date.year)
			if not os.path.exists(path):
				os.makedirs(path)
			print('Videos will be saved to: ' + path)
			vid_writer = cv2.VideoWriter(path+'/'+str(date.hour)+'-'+str(date.minute)+'.avi', self.fourcc, self.fps, (640,480))
			t = time.time()
			while (time.time()-t < self.vid_len):
				print(self.vid_len-(time.time()-t))
				if self.decodeQ.qsize() > 0:
					print('Queue size: ' + str(self.decodeQ.qsize()))
					frame = cv2.resize(self.decodeQ.get(), (640,480))
					vid_writer.write(frame)
				time.sleep(self.delay/2.0)
			print('Exited inner loop')
			vid_writer.release()


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--capture_delay', help='Delay between images (s)', default='0.05')
	parser.add_argument('--video_length', help='Length of Each Video (s)', default='3600') # Not yet implemented
	parser.add_argument('--render', help='Render the video stream', default='True')
	parser.add_argument('--write', help='Save video locally', default='False')
	parser.add_argument('--addr', help='Server address', default='security-server')
	parser.add_argument('--fps', help='Frame rate', default=10)
	parser.add_argument('--qSize', help='Queue size', default=256)
	parser.add_argument('--server', help='Server IP Address/Hostname and Port', default='https://security-server:50000')
	parser.add_argument('--username', help='Username for authentication', default='user')
	parser.add_argument('--password', help='Password for authentication', default='password')
	parser.add_argument('--auth_required', help='Attempt to authenticate with server?', default='True')
	parser.add_argument('--suppress_ssl_warning', help='Disables ssl warning for self-signed certificates', default='True')
	args = parser.parse_args()

	if args.write == 'True' and args.render == 'True':
		raise ValueError('You cannot write and render in a single client. Please use two client instances')

	if args.suppress_ssl_warning == 'True':
		import urllib3
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

	client = Client(args.username, args.password, addr=args.server, auth_required=args.auth_required, queueSize=int(args.qSize), delay=float(args.capture_delay), fps=float(args.fps), vid_len=int(args.video_length))

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
