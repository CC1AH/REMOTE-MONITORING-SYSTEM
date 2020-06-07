# coding=utf-8
# 客户端
import cv2
import socket
from PIL import Image
from io import BytesIO
import numpy as np
import tkinter.messagebox as msg

# 获取TCP连接外网地址和端口号
try:
    with open('config.txt', 'r+') as f:
        ip = f.readline().split(':', 2)[1].replace('\n', '')
        port = f.readline().split(':', 2)[1].replace('\n', '')
        port = int(port)
        print(ip, port)
except FileNotFoundError:
    msg.showerror('错误', '配置文件缺失!')
    exit(0)
except Exception:
    msg.showerror('错误', '配置文件内容格式错误!')
    exit(0)

# 连接到服务器
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((ip, port))
sock.connect(('127.0.0.1', 9999))
print("connect successfully.")
f = sock.makefile(mode='rb')

winname='camera'

while True:
    # 从服务器读取数据，一行的结尾是'\n'，注意我们前面已经将每一帧数据的'\n'替换成'\-n'，而结尾就是'\n'
    msg = f.readline()
    if not msg:
        break
    print(len(msg), msg[-2])
    # 将'\-n'换回来成'\n'
    jpeg = msg.replace("\-n".encode('utf8'), "\n".encode('utf8'))
    buf = BytesIO(jpeg[0:-1])  # 缓存数据
    buf.seek(0)
    pi = Image.open(buf)  # 使用PIL读取jpeg图像数据
    img = cv2.cvtColor(np.asarray(pi), cv2.COLOR_RGB2BGR)  # 从PIL的图像转成opencv支持的图像
    buf.close()
    img = cv2.resize(img, (800, 720))
    cv2.resizeWindow(winname, 800, 720)
    cv2.imshow("camera", img)  # 实时显示
    if cv2.waitKey(10) == 27:
        break
    if cv2.getWindowProperty(winname, cv2.WND_PROP_AUTOSIZE) < 1:
        break

sock.close()
cv2.destroyAllWindows()
