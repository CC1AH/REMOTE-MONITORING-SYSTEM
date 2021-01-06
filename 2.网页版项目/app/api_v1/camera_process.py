import numpy as np
from PIL import Image

from app.api_v1.camera_pi import Camera
import cv2
import io
camera = Camera()


class ImageProcessor(object):
    genarator = None

    def __init__(self):
        self.genarator = self.gen()

    def gen(self):
        while True:
            image = camera.get_image()
            # print(image)
            cv_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
            yield cv_image

    def process(self):
        pass

    def streamOut(self):
        for img in self.genarator:
            pi = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            buf = io.BytesIO()
            pi.save(buf, format='JPEG')
            jpeg = buf.getvalue()
            buf.close()
            #transfer = jpeg.replace(b'\n', b'\-n')
            yield jpeg

# if __name__ == '__main__':
#     pro = ImageProcessor()
#     for frame in pro.streamOut():
#         print(frame)

