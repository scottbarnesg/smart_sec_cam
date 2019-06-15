import cv2
import time
from threading import Thread
import flask
from flask import Flask, Response, request
import json
import numpy as np
import datetime
import io
import os

from authentication import serverAuth, revokeSession, Authorized


error = False
active_connection = False
connection_time = 0

class Streamer:
    def __init__(self, capture_delay=0.05, camera_port=0, compression_ratio=1.0):
        self.cap_delay = capture_delay
        self.cam_port=camera_port
        self.cam = cv2.VideoCapture(int(self.cam_port)) # Machine dependent
        self.image = self.captureImage()
        print('Source video resolution: ' + str(self.image.shape))
        self.compression(compression_ratio)
        self.image = self.captureImage()
        print('Compressed video resolution: ' + str(self.image.shape))

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

    def compression(self, compression_ratio):
        width = compression_ratio * self.image.shape[0]
        height = compression_ratio * self.image.shape[1]
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


    def run(self):
        print('Starting image capture')
        global active_connection
        while True:
            if active_connection:
                 self.image = self.captureImage()
                 time.sleep(self.cap_delay) # Prevents capture from eating cpu time
            else:
                time.sleep(0.5)

    def encode(self):
        print('Starting encoding')
        global error
        global active_connection
        while not error:
            if active_connection:
                self.data = (cv2.imencode('.jpeg', streamer.image)[1]).tostring()
                time.sleep(self.cap_delay) # Prevents encoding from eating cpu time
            else:
                time.sleep(0.5)
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

class Logger:
    def __init__(self):
        date = datetime.datetime.now()
        path = "logs/"
        if not os.path.exists(path):
            os.makedirs(path)
        self.filepath = path + str(date.month) + '-' + str(date.day) + '-' + str(date.year)
        logfile = open(self.filepath,"w+")
        logfile.close()
        print('Logs will be saved to: ' + self.filepath)

    def log(self, message):
        logfile = open(self.filepath,"a")
        logfile.write(message + "\n")
        logfile.close()

def connectionManager():
    global connection_time
    global active_connection
    connection_time = time.time()
    timeout = 10.0
    while not error:
        if time.time() - connection_time >= timeout and active_connection == True:
            active_connection = False
            print("No recent connection requests - halting video capture")
        time.sleep(1)




# Start server
import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--require_auth', help='Require authentication?', default='True')
parser.add_argument('--comp_ratio', help='Video compression ratio - float between 0 and 1', default='1.0')
parser.add_argument('--port', help='Port for server to listen on', default='50000')
args = parser.parse_args()

streamer = Streamer(compression_ratio=float(args.comp_ratio))
server = Server(require_auth=args.require_auth)
logger = Logger()

app = Flask(__name__)
@app.route(server.api_path, methods=['GET'])
def serve_image():
    global active_connection, connection_time
    active_connection = True
    connection_time = time.time()
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
    global active_connection, connection_time
    active_connection = True
    connection_time = time.time()
    data = request.get_json()
    print(data["username"])
    logger.log("Authentication Request from IP " + str(request.remote_addr) + " for user " + str(data["username"]))
    user_exists, correct_hashed_password = server.authorized.get_password(str(data["username"]))
    if not user_exists:
        return Response(response="Authentication error", status=403, mimetype="application/json")
        logger.log("Failed authentication Request from IP " + str(request.remote_addr) + " for user " + str(data["username"]) + " - Non-existent user")
    token, revoke_time, authenticated = serverAuth(data["username"], data["password"], correct_hashed_password)
    print(token)
    print(revoke_time)
    print(authenticated)
    if authenticated:
        server.authorized.new_login(data["username"], token, revoke_time)
        logger.log("Successful authentication Request from IP " + str(request.remote_addr) + " for user " + str(data["username"]))
        return Response(response=token, status=200, mimetype="application/json")
    else:
        logger.log("Failed authentication Request from IP " + str(request.remote_addr) + " for user " + str(data["username"]) + " - Incorrect password")
        return Response(response="Authentication error", status=403, mimetype="application/json")


def run_flask():
    addr = '0.0.0.0'
    home_dir = os.path.expanduser("~")
    app.run(host=addr, port=args.port, debug=False, threaded=True, ssl_context=(home_dir+'/smart_sec_cam/auth/cert.pem', home_dir+'/smart_sec_cam/auth/key.pem'))


if __name__ == "__main__":
    streamThread = Thread(target = streamer.run)
    serverThread = Thread(target = run_flask)
    encoderThread = Thread(target = streamer.encode)
    managerThread = Thread(target = connectionManager)

    streamThread.start()
    serverThread.start()
    encoderThread.start()
    managerThread.start()
