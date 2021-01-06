# coding=utf-8
# 服务器端
import socket
import cv2
from PIL import Image
from io import BytesIO
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 9999))
sock.listen(2)  # 监听端口

# 等待目标端连接
dst, dst_addr = sock.accept()
print("Destination Connected by", dst_addr)
cap = cv2.VideoCapture(0)
cap.set(3, 440)
cap.set(4, 330)

while True:
    ret, img = cap.read()
    if ret is False:
        print("can not get this frame")
        continue
    pi = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    pi.save(buf, format='JPEG')
    jpeg = buf.getvalue()
    buf.close()
    transfer = jpeg.replace(b'\n', b'\-n')
    print(len(transfer), transfer[-1])
    try:
        dst.sendall(transfer+b'\n')
    except Exception as ex:
        dst, dst_addr = sock.accept()
        print("Destination Connected Again by", dst_addr)
    except KeyboardInterrupt:
        print("Interrupted")
        break
    time.sleep(0.1)

dst.close()
sock.close()
