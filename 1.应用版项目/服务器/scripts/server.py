# coding=utf-8
# 服务器端
import datetime
import os
import socket
import cv2
from PIL import Image
from io import BytesIO
import time
import threading

font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体

# 获取摄像头
cap = cv2.VideoCapture(0)


# 获取本机ip地址
def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()

    return ip

# 保存录像
def saveVideo():
    print("保存视频线程已启动...")
    while True:
        start_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')  # 获取时间，用于视频存储名称
        start = time.time()  # 获取开始时间，为了后面每一个小时存储一次视频文件
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 视频编码格式
        # 视频写入
        out = cv2.VideoWriter('../history/' + start_time + '.avi', fourcc, 20.0, (640, 480))
        while (int(time.time() - start)) < 3600 * 12:
            ret, frame = cap.read()
            if ret is True:
                cv2.putText(frame, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (400, 400), font, 0.55,
                            (255, 255, 255), 1)
                out.write(frame)  # 在视频流中写入该图片
            else:
                break
        with open('../log.txt', 'a+') as f:
            f.write(
                "视频已保存，开始时间：" + start_time + "，结束时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S') + "\n")


# 处理用户请求
def deal():
    print("处理用户请求线程已启动...")
    while True:
        dst, dst_addr = sock.accept()
        print("Destination Connected by", dst_addr)
        response = dst.recv(1024).decode()
        print(response)
        if response == "video":
            start_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')  # 获取时间，用于视频存储名称
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 视频编码格式
            while True:
                ret, img = cap.read()
                img = cv2.resize(img, (640, 480))
                if ret is False:
                    print("can not get this frame")
                    continue
                print(img.shape)
                cv2.putText(img, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (400, 400), font, 0.55,
                            (255, 255, 255), 1)
                pi = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                buf = BytesIO()
                pi.save(buf, format='JPEG')
                jpeg = buf.getvalue()
                buf.close()
                transfer = jpeg.replace(b'\n', b'\-n')
                try:
                    dst.sendall(transfer + b'\n')
                except Exception as ex:
                    break
                except KeyboardInterrupt:
                    print("Interrupted")
                    break
                time.sleep(0.1)

        if response == "history":
            videoList = os.listdir("../history")
            videos = ""
            for video in videoList:
                videos = videos + video + "\n"
            dst.send(videos.encode("utf-8"))
        if "video_name" in response:
            video_name = response[10:]
            video_data = file_deal(video_name)
            if video_data:
                dst.sendall(video_data)
        dst.close()


# 文件处理函数
def file_deal(file_name):
    try:
        # 二进制方式读取
        files = open("../history/" + file_name, "rb")
        mes = files.read()
    except:
        print("没有该文件")
    else:
        files.close()
        return mes


# 清理过时视频（大于7天）
def clear_video():
    print("清理视频线程已启动")
    while True:
        with open('../log.txt', 'a+') as log:
            files = os.listdir("../history")
            if len(files) < 1:
                exit()
            for file in files:
                filename = file  # 临时文件名字
                if 'seen' in file:
                    filename = file.replace('(seen)', '')
                filetime = filename.replace('.avi', '').replace(' ', '-')
                time_list = filetime.split('-')
                for i in range(len(time_list)):
                    time_list[i] = int(time_list[i])
                v_time = datetime.datetime(time_list[0], time_list[1], time_list[2], time_list[3], time_list[4],
                                           time_list[5])
                now = datetime.datetime.now()
                # 历史大于七天的文件会被清除
                if now.timestamp() - v_time.timestamp() > 3600 * 24 * 7:
                    try:
                        os.remove('../history/' + file)
                        log.write("已清除视频：" + file + "，时间：" + now.strftime('%Y-%m-%d %H:%M:%S') + '\n')
                    except:
                        print("清除出现故障")
        time.sleep(3600 * 24)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(get_host_ip())
sock.bind((get_host_ip(), 9999))
sock.listen(20)  # 监听端口
threadLock = threading.Lock()  # 线程锁
thread_saveVideo = threading.Thread(target=saveVideo)  # 该线程用于实时保存视频
thread_deal = threading.Thread(target=deal)  # 该线程用于处理用户操作
thread_clear = threading.Thread(target=clear_video)
thread_saveVideo.start()  # 启动线程
thread_deal.start()
thread_clear.start()
thread_saveVideo.join()  # 主线程等待该线程结束
thread_deal.join()  # 主线程等待该线程结束
thread_clear.join()
sock.close()
