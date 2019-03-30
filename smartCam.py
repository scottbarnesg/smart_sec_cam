import numpy as np
import cv2
import time
import os
import datetime


class Camera:
    def __init__(self, capture_delay=0.5, video_length=10.0, show_img=False, camera_port=1, vid_name='capture', vid_type='.avi'):
        self.cap_del = float(capture_delay)
        self.vid_len  = float(video_length)
        self.t = time.time()
        self.cam = cv2.VideoCapture(int(camera_port)) # Machine dependent
        self.fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        self.show_img = show_img
        self.date = datetime.datetime.now()
        self.frame_counter = 0
        made_dir = False
        counter = 0
        while not made_dir:
            self.vid_dir = 'bin/videos' + str(counter)
            # self.vid_dir = '/dev/shm/bin/'
            if os.path.exists(self.vid_dir):
                counter += 1
            else:
                os.makedirs(self.vid_dir)
                made_dir = True
                print('Directory created: ' + self.vid_dir)
        test_img = self.captureImage()
        self.height, self.width = test_img.shape[:2]
        print('Image Size: ' + str(self.width) + 'x' + str(self.height))

    def captureImage(self):
        ret, frame = self.cam.read()
        if not ret:
            raise ValueError('Failed to capture image')
        if self.show_img:
            cv2.imshow("image", frame)
            cv2.waitKey(1000)
            cv2.destroyAllWindows()
        return frame



class MotionDetector():
    def __init__(self, Camera):
        self.camera=Camera
        threshold = 2e6
        self.thresh = threshold

    def compImages(self, new_frame, old_frame):
        diff = cv2.subtract(new_frame,old_frame)
        total_diff = np.sum(diff.flatten())
        is_similar = True
        if total_diff >= self.thresh:
            is_similar = False
        return is_similar

    def recordVideo(self, counter, stream):
        vid_writer = cv2.VideoWriter(self.camera.vid_dir+'/recording'+str(counter)+'.avi', self.camera.fourcc, 25.0, (self.camera.width,self.camera.height))
        start_time = time.time()
        if stream:
            print('Streaming Video')
            while True:
                ret, frame = self.camera.cam.read()
                if not ret:
                    raise ValueError('Unable to Capture Video')
                vid_writer.write(frame)
                self.frame_counter += 1
        else:
            print('Motion Detected: Recording Video')
            while(time.time()-start_time < self.camera.vid_len):
                ret, frame = self.camera.cam.read()
                if not ret:
                    raise ValueError('Unable to Capture Video')
                vid_writer.write(frame)
        vid_writer.release()
        frame = self.camera.captureImage()
        return frame

class Runner:
    def __init__(self, camera, stream):
        self.cam = camera
        self.motionDetector = MotionDetector(camera)
        self.init = True
        self.run_ = True
        self.stream = stream

    def run(self, sftpClient):
        print('Starting Server')
        counter = 0
        while self.run_:
            frame = self.cam.captureImage()
            if self.stream:
                print('Streaming video to file')
                frame = self.motionDetector.recordVideo(counter, self.stream)
            else:
                if self.init == True:
                    self.init = False
                    is_similar = True
                else:
                    is_similar = self.motionDetector.compImages(frame, self.old_frame)
                if not is_similar:
                    frame = self.motionDetector.recordVideo(counter, self.stream)
                    localpath = self.cam.vid_dir + '/recording'+str(counter)+'.avi'
                    date = str(self.cam.date.month) + '-' + str(self.cam.date.day)
                    remotedir = 'videos/' + date
                    remotepath = 'recording'+str(counter)+'.avi'
                    # sftpClient.send(localpath, remotepath, remotedir)
                    print('Recorded video sent to remote server')
                    counter += 1
                self.old_frame = frame
            time.sleep(float(self.cam.cap_del))
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import argparse
    from SFTPClient import Client
    sftpClient = Client()
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--capture_delay', help='Delay between images (s)', default='0.10')
    parser.add_argument('--video_length', help='Length of Each Video (s)', default='10.0')
    parser.add_argument('--show_img', help='Show the captured images', default='False')
    parser.add_argument('--camera_port', help='USB port for webcam', default='0')
    parser.add_argument('--stream', help='Streaming mode?', default='False')
    args = parser.parse_args()
    if args.show_img != 'True':
        args.show_img = False
    if args.stream != 'True':
        args.stream = False
    cam = Camera(capture_delay=args.capture_delay, video_length=args.video_length,
        show_img=args.show_img, camera_port=args.camera_port)
    runner = Runner(cam, args.stream)
    runner.run(sftpClient)
