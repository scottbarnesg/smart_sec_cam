import cv2
import time
from queue import Queue

class Streamer():
	def __init__(self, path, queueSize=256):
		self.stream = cv2.VideoCapture(path)
		self.Q = Queue(maxsize=queueSize)
		self.delay = 100

	def read(self):
		return self.Q.get()

	def QNotEmpty(self):
		return self.Q.qsize() > 0

	def update(self):
		if not self.Q.full():
			(grabbed, frame) = self.stream.read()
			if grabbed:
				self.Q.put(frame)
			else:
				print('Failed to get frame')

	def dynamicFPS(self):
		if self.Q.qsize() > 100:
			self.delay -= 5
		elif self.Q.qsize() < 100:
			self.delay += 10
			self.update()

	def run(self):
		for i in range(100):
			self.update()
		while True:
			self.update()
			# self.dynamicFPS()
			# print('Q Size' + str(self.Q.qsize()))
			# print('Delay' + str(self.delay))
			if self.QNotEmpty():
				frame = self.read()
				cv2.imshow("image", frame)
				cv2.waitKey(self.delay)
				# cv2.destroyAllWindows()
			else:
				print ('Queue Empty')
				time.sleep(0.1)


if __name__ == '__main__':
	path = '/home/scott/smart_sec_cam/bin/videos5/recording0.avi'
	streamer = Streamer(path)
	streamer.run()
