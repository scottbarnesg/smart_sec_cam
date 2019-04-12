import cv2
import time
from threading import Thread
import flask
from flask import Flask, Response, request
import json
import numpy as np
import io
import os

from authentication import serverAuth, revokeSession, Authorized


error = False

class Streamer:
	def __init__(self, capture_delay=0.05, camera_port=0, img_dims=[280,200]):
		self.cap_delay = capture_delay
		self.cam_port=camera_port
		self.cam = cv2.VideoCapture(int(self.cam_port)) # Machine dependent
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
	def __init__(self, api_path='/api/stream_video', auth_path='/api/auth', require_auth=True):
		self.api_path = api_path
		self.auth_path = auth_path
		self.require_auth = True
		if require_auth == 'False':
			self.require_auth = False
		self.authorized = Authorized()

# Start server
import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--require_auth', help='Require authentication?', default='True')
args = parser.parse_args()

streamer = Streamer()
server = Server(require_auth=args.require_auth)

app = Flask(__name__)
@app.route(server.api_path, methods=['GET'])
def serve_image():
	print('Request recieved')
	if error:
		print('Exiting flask server thread')
		shutdown_server = request.environ.get('werkzeug.server.shutdown')
		shutdown_server()
	data = request.get_json()
	authenticated = server.authorized.verify_token(data["username"], data["token"])
	if authenticated or not server.require_auth:
		revoked = server.authorized.revoke(data["token"])
		if not revoked or not server.require_auth:
			return Response(response=streamer.data, status=200, mimetype="application/json")
	return Response(response="Authentication error", status=403, mimetype="application/json")

@app.route(server.auth_path, methods=['POST'])
def authenticate():
	print('Authentication request recieved')
	data = request.get_json()
	print(data["username"])
	user_exists, correct_hashed_password = server.authorized.get_password(str(data["username"]))
	if not user_exists:
		return Response(response="Authentication error", status=403, mimetype="application/json")
	token, revoke_time, authenticated = serverAuth(data["username"], data["password"], correct_hashed_password)
	print(token)
	print(revoke_time)
	print(authenticated)
	if authenticated:
		server.authorized.new_login(data["username"], token, revoke_time)
		return Response(response=token, status=200, mimetype="application/json")
	else:
		return Response(response="Authentication error", status=403, mimetype="application/json")


def run_flask():
	addr = '0.0.0.0'
	port = 50000
	home_dir = os.path.expanduser("~")
	app.run(host=addr, port=port, debug=False, threaded=True, ssl_context=(home_dir+'/smart_sec_cam/auth/cert.pem', home_dir+'/smart_sec_cam/auth/key.pem'))


if __name__ == "__main__":
	streamThread = Thread(target = streamer.run)
	serverThread = Thread(target = run_flask)
	encoderThread = Thread(target = streamer.encode)

	streamThread.start()
	serverThread.start()
	encoderThread.start()
