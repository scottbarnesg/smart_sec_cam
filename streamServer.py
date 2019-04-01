import cv2
import time
from threading import Thread
import flask
from flask import Flask, Response, make_response, jsonify
import json
import numpy as np
import io

class Streamer:
	def __init__(self, capture_delay=0.1, camera_port=0, img_dims=[210,160]):
		self.cap_delay = capture_delay
		self.cam_port=camera_port
		self.cam = cv2.VideoCapture(int(camera_port)) # Machine dependent
		self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, img_dims[0])
		self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, img_dims[1])
		self.image = self.captureImage()
		print(self.image.shape)

	def captureImage(self):
		ret, frame = self.cam.read()
		if not ret:
			raise ValueError('Failed to capture image - check port value')
		return frame

	def run(self):
		print('Starting image capture')
		while True:
			self.image = self.captureImage()
			time.sleep(self.cap_delay) # Prevents capture from eating cpu time

	def encode(self):
		print('Starting encoding')
		while True:
			self.data = json.dumps(streamer.image.tolist())
			time.sleep(self.cap_delay) # Prevents encoding from eating cpu time


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
	return Response(response=streamer.data, status=200, mimetype="application/json")

def run_flask():
	addr = '0.0.0.0'
	port = 50000
	app.run(host=addr, port=port, debug=False)


if __name__ == "__main__":
	streamThread = Thread(target = streamer.run)
	serverThread = Thread(target = run_flask)
	encoderThread = Thread(target = streamer.encode)

	streamThread.start()
	serverThread.start()
	encoderThread.start()
