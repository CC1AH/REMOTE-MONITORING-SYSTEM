#!/usr/bin/env python
from flask import Flask, render_template, Response,current_app

# Raspberry Pi camera module (requires picamera package)
from app.api_v1.camera_pi import Camera
from app.api_v1.camera_process import ImageProcessor
from app.api_v1 import api


# @auth.login_required

@api.route('/video')
def index():
    """Video streaming home page."""
    current_app.logger.debug('video')
    return render_template('main.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        #print(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_img():
    imageProcessor = ImageProcessor()
    for frame in imageProcessor.streamOut():
        #print(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@api.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_img(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/record_video',methods=['POST'])
def record_video():
    cam = ImageProcessor()
    cam.startRecord()
    time.sleep(10)
    ImageProcessor.isRecord = False
    return render_template('record_video.html')

    
@app.route('/download_app',methods=['GET'])
def download_app():
    return send_from_directory("/home/pi/Desktop/midTerm/site","PieApp.apk",as_attachment=True)


if __name__ == '__main__':
    app.run(host='192.168.43.116', port =8083, debug=True, threaded=True)



