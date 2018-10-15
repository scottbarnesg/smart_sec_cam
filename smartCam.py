import numpy as np
import cv2
import time
import os


class Camera():
    def __init__(self, capture_delay=1.0, video_length=10.0, show_img=False, camera_port=1, vid_name='capture', vid_type='.avi'):
        self.cap_del = float(capture_delay)
        self.vid_len  = float(video_length)
        self.t = time.time()
        self.cam = cv2.VideoCapture(int(camera_port)) # Machine dependent
        self.fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        self.show_img = show_img
        threshold = 2e6
        self.thresh = threshold
        made_dir = False
        counter = 0
        while not made_dir:
            self.vid_dir = 'bin/videos' + str(counter)
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

    def compImages(self, new_frame, old_frame):
        diff = cv2.subtract(new_frame,old_frame)
        total_diff = np.sum(diff.flatten())
        is_similar = True
        if total_diff >= self.thresh:
            is_similar = False
        return is_similar

    def recordVideo(self, counter):
        print('Motion Detected: Recording Video')
        vid_writer = cv2.VideoWriter(self.vid_dir+'/recording'+str(counter)+'.avi', self.fourcc, 25.0, (self.width,self.height))
        start_time = time.time()
        while(time.time()-start_time < self.vid_len):
            ret, frame = self.cam.read()
            if not ret:
                raise ValueError('Unable to Capture Video')
            vid_writer.write(frame)
        vid_writer.release()
        frame = self.captureImage()
        return frame

class Runner():
    def __init__(self, camera):
        self.cam = camera
        self.init = True
        self.run_ = True

    def run(self, sftpClient):
        print('Starting Motion Detection')
        counter = 0
        while self.run_:
            frame = cam.captureImage()
            if self.init == True:
                self.init = False
                is_similar = True
            else:
                is_similar = cam.compImages(frame, self.old_frame)
            if not is_similar:
                frame = cam.recordVideo(counter)
                # client.send("bin/videos7/recording0.avi", "videos/recording0.avi")
                localpath = self.cam.vid_dir + '/recording'+str(counter)+'.avi'
                remotepath = 'videos' + '/recording'+str(counter)+'.avi'
                sftpClient.send(localpath, remotepath)
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
    parser.add_argument('--capture_delay', help='Delay between images (s)', default='0.1')
    parser.add_argument('--video_length', help='Length of Each Video (s)', default='5.0')
    parser.add_argument('--show_img', help='Show the captured images', default='False')
    parser.add_argument('--camera_port', help='USB port for webcam', default='1')
    args = parser.parse_args()
    if args.show_img != 'True':
        args.show_img = False
    cam = Camera(capture_delay=args.capture_delay, video_length=args.video_length,
        show_img=args.show_img, camera_port=args.camera_port)
    runner = Runner(cam)
    runner.run(sftpClient)
