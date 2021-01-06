#!/usr/bin/env python

import time
import io
import threading
import picamera
from PIL.Image import Image
from picamera.array import PiRGBArray


class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    image = None  # 代表每一帧的图像
    last_access = 0  # time of last client access to the camera

    def initialize_frame(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize_frame()
        return self.frame

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (640, 480)
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(0.1)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 5:
                    break
        cls.thread = None

    def initialize_image(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._threadImage)
            Camera.thread.start()

            # wait until frames start to be available
            while self.image is None:
                time.sleep(0)

    def get_image(self):
        # 针对cv2进行处理
        Camera.last_access = time.time()
        self.initialize_image()
        return self.image

    @classmethod
    def _threadImage(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (640, 480)
            camera.hflip = True
            camera.vflip = True
            rawCapture = PiRGBArray(camera, size=(640, 480))

            # let camera warm up
            camera.start_preview()
            time.sleep(0.1)


            for foo in camera.capture_continuous(rawCapture, 'rgb',
                                                 use_video_port=True):
                # store frame
                cls.image = foo.array

                rawCapture.truncate(0)
                # 如果访问间隔超过5s就跳出
                if time.time() - cls.last_access > 5:
                    break

        # cls thread清零
        cls.thread = None
