import cv2
import time
from threading import Thread
import flask
from flask import Flask, Response, make_response, jsonify
import json
import numpy as np
import io

class Streamer:
	def __init__(self, capture_delay=0.05, camera_port=0):
		self.cap_delay = capture_delay
		self.cam_port=camera_port
		self.cam = cv2.VideoCapture(int(camera_port)) # Machine dependent
		self.image = self.captureImage()

	def captureImage(self):
		ret, frame = self.cam.read()
		if not ret:
			raise ValueError('Failed to capture image')
		return frame

	def run(self):
		print('Starting image capture')
		while True:
			self.image = self.captureImage()
			time.sleep(self.cap_delay) # Artificial delay added for testing - will remove

	def encode(self):
		print('Starting encoding')
	 	while True:
	 		self.data = json.dumps(streamer.image.tolist())
			time.sleep(self.cap_delay) # Artificial delay added for testing - will remove


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
	# print(streamer.image)
	# _, enc_image = cv2.imencode('.jpg', streamer.image)
	# start = time.time()
	# list = streamer.image.tolist()
	# print('List time ' + str(time.time()-start))
	# ret = jsonify(list)# , mimetype='application.json') #, mimetype='image/jpg') #, as_attachment=True, attachment_filename='img.jpg')
	# data = json.dumps(list)
	# print('Total time ' + str(time.time()-start))
	# data = json.dumps(streamer.image.tolist())
	return Response(response=streamer.data, status=200, mimetype="application/json")
	# response = make_response(enc_image.tobyes())
	# return response

def run_flask():
	addr = '0.0.0.0'
	port = 50000
	app.run(host=addr, port=port, debug=False)


if __name__ == "__main__":
	# app.run(host=addr, port=port, threaded=True)
	streamThread = Thread(target = streamer.run)
	serverThread = Thread(target = run_flask)
	encoderThread = Thread(target = streamer.encode)
	# time.sleep(2)
	# serverThread = Thread(target = app.run(host=addr, port=port))
	streamThread.start()
	serverThread.start()
	encoderThread.start()
