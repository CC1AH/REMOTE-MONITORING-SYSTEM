# coding=utf-8
import win32gui, win32ui, win32con
from tkinter import *
from PIL import Image, ImageTk
import cv2
import socket
from io import BytesIO
import numpy as np
import tkinter.messagebox as msg
import os
import datetime
import threading


# 设置ip地址和端口号
ip = ""
port = ""

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


# 用于获取图片
def get_image(fp, width, height):
    img = Image.open(fp).resize((width, height))
    return ImageTk.PhotoImage(img)


# 获取监控视频信息
def runVideo():
   try:
       # 连接到服务器
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       sock.connect((ip, port))
       print("Video connect successfully.")
       input_data = "video"
       sock.send(input_data.encode("utf-8"))
       f = sock.makefile(mode='rb')

       winname = 'camera'
       # 全局变量img
       global img

       while True:
           # 从服务器读取数据，一行的结尾是'\n'，注意我们前面已经将每一帧数据的'\n'替换成'\-n'，而结尾就是'\n'
           msg = f.readline()
           if not msg:
               break
           # 将'\-n'换回来成'\n'
           jpeg = msg.replace("\-n".encode('utf8'), "\n".encode('utf8'))
           buf = BytesIO(jpeg[0:-1])  # 缓存数据
           buf.seek(0)  # 将流指针指向0位置
           pi = Image.open(buf)  # 使用PIL读取jpeg图像数据
           img = cv2.cvtColor(np.asarray(pi), cv2.COLOR_RGB2BGR)  # 从PIL的图像转成opencv支持的图像
           buf.close()
           img = cv2.resize(img, (640, 480))
           cv2.resizeWindow(winname, 640, 480)
           cv2.imshow("camera", img)  # 实时显示
           if cv2.waitKey(10) == 27 or cv2.getWindowProperty(winname, cv2.WND_PROP_AUTOSIZE) < 1:
               cv2.destroyAllWindows()
               sock.close()
               return
   except:
       import tkinter.messagebox as msg
       msg.showinfo("提示","与服务器断开连接...")
       os._exit(0)


# 开始获取监控视频线程
def start_thread_runVideo(event):
    threading.Thread(target=runVideo).start()


# 查看监控历史记录
def videoHistory(event):
    import tkinter.messagebox as msg
    camera_exsit = win32gui.FindWindow(None, "camera")
    if camera_exsit != 0:
        print("0")
        msg.showinfo("提示","请先关闭实时监控窗口(camera)")
        return
    try:
        # 连接到服务器
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        print("History connect successfully.")
        input_data = "history"
        sock.send(input_data.encode("utf-8"))
        history = ""
        while True:
            temp = sock.recv(4096).decode()
            if not temp: break
            history += temp
        history = history.split('\n')
        history.remove('')
        history_level = Toplevel(main_frame)
        history_level.title("监控历史(双击下载)")
        history_level.maxsize(290, 600)
        history_level.minsize(290, 400)
        sb = Scrollbar(history_level)
        sb.pack(side=RIGHT, fill=Y)
        history_list = Listbox(history_level, yscrollcommand=sb.set, width=40)
        history_list.pack(side=LEFT, fill=BOTH)
        history_list.bind("<Double-Button-1>", lambda event: getVideoByName(history_list))
        sb.config(command=history_list.yview)
        for i in history:
            history_list.insert(0, i)
        history_list.delete(history_list.size()-1)
        history_level.mainloop()
        sock.close()
    except Exception as e:
        msg.showinfo("错误", "与服务器断开连接...")
        os._exit(0)


# 开始获取监控历史线程
def start_thread_videoHistory(event):
    threading.Thread(target=videoHistory).start()


# 定义listbox响应函数
def getVideoByName(history_list):
    if history_list.size() < 1:
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((id, port))
    video_name = "video_name" + history_list.get(history_list.curselection())
    sock.send(video_name.encode("utf-8"))
    bytesCount = 0  # 用于计算文件字节数
    new_file = open("./下载/" + video_name[10:], "wb")
    while True:
        mes = sock.recv(4096)
        if mes:
            new_file.write(mes)
            bytesCount += len(mes)
        else:
            # 如果字节数为空即未收到内容
            if bytesCount == 0:
                # 关闭文件
                new_file.close()
                # 删除刚刚创建的文件
                os.remove("./下载/" + video_name[10:])
                msg.showinfo("提示", "没有您要下载的文件")
            else:
                # 如过time有值时name文件传输完成
                msg.showinfo("提示", "视频已下载到本地")
            break
    sock.close()


# 实时截图
def screenShot(event):
    try:
        # 获取后台窗口的句柄，注意后台窗口不能最小化
        hWnd = win32gui.FindWindow(None, "camera")  # 窗口的类名可以用Visual Studio的SPY++工具获取
        # 获取句柄窗口的大小信息
        left, top, right, bot = win32gui.GetWindowRect(hWnd)
        width = right - left
        height = bot - top
        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hWndDC = win32gui.GetWindowDC(hWnd)
        # 创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        # 创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 为bitmap开辟存储空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        # 将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)
        # 保存bitmap到内存设备描述表
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        ###获取位图信息
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        ###生成图像
        im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        # 内存释放
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hWnd, hWndDC)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        path = './截图/' + time + '.jpg'
        ###PrintWindow成功,保存到文件,显示到屏幕
        im_PIL.save(path)  # 保存
        im_PIL.show()  # 显示
    except:
        msg.showinfo("提示","请先打开监控系统！")


# 退出系统
def app_destroy():
    os._exit(0)


if __name__ == "__main__":
    # 声明一个全局变量，用于截图
    img = ''
    app = Tk()
    app.wm_protocol("WM_DELETE_WINDOW", app_destroy)        #当用户点击右上角X时退出程序
    app.title("树莓派远程监控系统")
    app_width = 800
    app_height = 600
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
        sock.connect((ip, port))
        print("connect successfully.")
        sock.close()
    except Exception:
        msg.showerror('错误', '与远程服务器连接失败！')
        os._exit(0)

    # 主界面
    main_frame = Frame(app)
    img_bg = get_image('image/night.jpg', app_width, app_height)
    background = Label(main_frame, width=app_width, height=app_height, image=img_bg)
    btn_video = Button(main_frame, text="监控系统", font=('楷体', 13), bg='#44C7D3', fg='white', bd=0)
    btn_history = Button(main_frame, text="监控历史", font=('楷体', 13), bg='#44C7D3', fg='white', bd=0)
    btn_screenShot = Button(main_frame, text="实时截图", font=('楷体', 13), bg='#44C7D3', fg='white', bd=0)
    btn_exit = Button(main_frame, text="退出系统", font=('楷体', 13), bg='#44C7D3', fg='white', bd=0,command=app.destroy)
    btn_video.bind("<Button-1>", start_thread_runVideo)
    btn_history.bind("<Button-1>", videoHistory)
    btn_screenShot.bind("<Button-1>", screenShot)
    background.pack()
    btn_video.place(relx=0.48, rely=0.35, anchor=CENTER)
    btn_history.place(relx=0.48, rely=0.45, anchor=CENTER)
    btn_screenShot.place(relx=0.48, rely=0.55, anchor=CENTER)
    btn_exit.place(relx=0.48, rely=0.65, anchor=CENTER)
    main_frame.pack()
    btn_group = [btn_video, btn_history, btn_screenShot]

    app.mainloop()

