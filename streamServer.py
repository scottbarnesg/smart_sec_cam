import cv2
import time
from threading import Thread
import flask
from flask import Flask, Response, request
import json
import numpy as np
import io

error = False

class Streamer:
	def __init__(self, capture_delay=0.05, camera_port=0, img_dims=[280,200]):
		self.cap_delay = capture_delay
		self.cam_port=camera_port
		self.cam = cv2.VideoCapture(int(self.cam_port)) # Machine dependent
		self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, img_dims[0])
		self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, img_dims[1])
		self.image = self.captureImage()
		print('Image dimentions: ' + str(self.image.shape))

	def captureImage(self, init=False):
		global error
		ret, frame = self.cam.read()
		if not ret:
			if init:
				raise ValueError('Failed to capture image - check camera port value')
			else:
				error = True
				print('Exiting capture thread')
				exit()
		return frame

	def run(self):
		print('Starting image capture')
		while True:
 			self.image = self.captureImage()
			time.sleep(self.cap_delay) # Prevents capture from eating cpu time

	def encode(self):
		print('Starting encoding')
		global error
		while not error:
			self.data = (cv2.imencode('.jpeg', streamer.image)[1]).tostring()
			time.sleep(self.cap_delay) # Prevents encoding from eating cpu time
		print('Exiting encoder thread')

	def reset_vidcap(self):
		self.cam.release()
		self.cam = cv2.VideoCapture(int(self.cam_port)) # Machine dependent
		self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, img_dims[0])
		self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, img_dims[1])
		self.image = self.captureImage()


class Server:
	def __init__(self, api_path='/api/test'):
		self.api_path = api_path

# Start server
streamer = Streamer()
server = Server()
app = Flask(__name__)
@app.route(server.api_path, methods=['GET'])
def serve_image():
	print('Request recieved')
	if error:
		print('Exiting flask server thread')
		shutdown_server = request.environ.get('werkzeug.server.shutdown')
		shutdown_server()
	return Response(response=streamer.data, status=200, mimetype="application/json")

def run_flask():
	addr = '0.0.0.0'
	port = 50000
	app.run(host=addr, port=port, debug=False, threaded=True)


if __name__ == "__main__":
	streamThread = Thread(target = streamer.run)
	serverThread = Thread(target = run_flask)
	encoderThread = Thread(target = streamer.encode)

	streamThread.start()
	serverThread.start()
	encoderThread.start()
