# coding=utf-8
from tkinter import *
import tkinter.messagebox as msg
from PIL import Image, ImageTk
import cv2
import time
import os
import socket


# 用于获取图片
def get_image(fp, width, height):
    img = Image.open(fp).resize((width, height))
    return ImageTk.PhotoImage(img)


def runVideo(event):
    os.system('python scripts/video.py')


if __name__ == "__main__":
    app = Tk()
    app.title("树莓派远程监控系统")
    app_width = 1280
    app_height = 760
    app.geometry('%dx%d+%d+%d' % (app_width, app_height,
                                  (app.winfo_screenwidth() - app_width) / 2,
                                  (app.winfo_screenheight() - app_height) / 2 - 20))
    app.resizable(False, False)

    # 读取配置文件，获取服务器ip地址和端口号
    try:
        with open('config.txt', 'r+') as f:
            ip = f.readline().split(':', 2)[1].replace('\n', '')
            port = f.readline().split(':', 2)[1].replace('\n', '')
            port = int(port)
            f.close()
    except FileNotFoundError:
        msg.showerror('错误', '配置文件缺失!')
        exit(0)
    except Exception:
        msg.showerror('错误', '配置文件内容格式错误!')
        exit(0)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.connect((ip, port))
         sock.connect(('127.0.0.1', 9999))
        print("connect successfully.")
        sock.close()
    except Exception:
        msg.showerror('错误', '与远程服务器连接失败！')
        exit(0)

    # 主界面
    main_frame = Frame(app)
    img_bg = get_image('image/night.jpg', app_width, app_height)
    background = Label(main_frame, width=app_width, height=app_height, image=img_bg)
    btn_video = Button(main_frame, text="监控系统", font=('楷体', 13), bg='#44C7D3', fg='white', bd=0)
    btn_video.bind("<Button-1>", runVideo)
    background.pack()
    btn_video.place(relx=0.1, rely=0.1, anchor=CENTER)
    main_frame.pack()
    app.mainloop()
