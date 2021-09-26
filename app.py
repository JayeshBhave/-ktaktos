from flask import Flask, render_template, Response
import cv2
import serial

app = Flask(__name__)

face_cascade= cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# ArduinoSerial=serial.Serial('COM4',9600,timeout=0.1)
fourcc= cv2.VideoWriter_fourcc(*'XVID')
camera = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)
out= cv2.VideoWriter('face detection4.avi',fourcc,20.0,(640,480))

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces= face_cascade.detectMultiScale(gray,1.1,4)
        if not success:
            break
        else:
            for x,y,w,h in faces:
            #sending coordinates to Arduino
                string='X{0:d}Y{1:d}'.format((x+w//2),(y+h//2))
                print(string)
                # ArduinoSerial.write(string.encode('utf-8'))
                
                #plot the roi
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)
                cv2.circle(frame,(x+w//2,y+h//2),2,(0,255,0),2)
                out.write(frame)
                cv2.imshow('img',frame)
                cv2.imwrite('output_img.jpg',frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            
           
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
                
                
@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index(1).html')


if __name__ == '__main__':
   app.run(debug=True)

