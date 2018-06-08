import numpy as np
import cv2
import time

# Install Instructions for OpenCV
# conda install -c conda-forge ffmpeg
# conda install -c conda-forge opencv

class Camera():
    def __init__(self, capture_delay=1, video_length=10, show_img=False, vid_name='capture', vid_type='.avi'):
        self.cap_del = capture_delay
        self.vid_len  = video_length
        self.t = time.time()
        self.cam = cv2.VideoCapture(1)
        self.show_img = show_img
        threshold = 1000000
        self.thresh = threshold

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
        print('Recording Video')
        return 0

class Runner():
    def __init__(self, camera):
        self.cam = camera
        self.init = True
        self.run_ = True

    def run(self):
        while self.run_:
            frame = cam.captureImage()
            if self.init == True:
                self.init = False
                is_similar = True
            else:
                is_similar = cam.compImages(frame, self.old_frame)
            self.old_frame = frame
            if not is_similar:
                cam.recordVideo(0)
            time.sleep(float(self.cam.cap_del))
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--capture_delay', help='Delay between images (s)', default='0.1')
    parser.add_argument('--video_length', help='Length of Each Video (s)', default='10')
    parser.add_argument('--show_img', help='Show the captured images', default='False')
    args = parser.parse_args()
    cam = Camera(capture_delay=args.capture_delay, video_length=args.video_length, show_img=True)
    runner = Runner(cam)
    runner.run()
