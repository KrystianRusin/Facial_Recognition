import cv2
import pickle
import xlwt
import csv
from datetime import datetime
import pandas as pd

row = 0
col = 0
nameList = []
f = open('Attendance.csv', "w+")
f.writelines('Name , Date')


faceCascade = cv2.CascadeClassifier('Cascades/data/haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

labels = {}
with open('labels.pickle', 'rb') as f:
    original_labels = pickle.load(f)
    labels = {v:k for k,v in original_labels.items()}

video_capture = cv2.VideoCapture(0)

def markAttendance(name):
     with open('Attendance.csv', 'a') as f:
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        f.writelines(f'\n{name},{dtString}')

while True:
    returnCode, camera = video_capture.read()

    grayScale = cv2.cvtColor(camera, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        grayScale,
        scaleFactor=1.5,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        roi_gray = grayScale[y:y+h, x:x+w]

        id_, confidendence = recognizer.predict(roi_gray)

        if confidendence<=85:
            font = cv2.FONT_HERSHEY_SIMPLEX
            name = labels[id_]
            color =  (255,255,255)
            stroke = 2
            if name not in nameList:
                nameList.append(name)
                markAttendance(name)
            cv2.putText(camera, name, (x,y), font, 1, color, stroke, cv2.LINE_AA)
        elif confidendence>85:
            font = cv2.FONT_HERSHEY_SIMPLEX
            name = labels[id_]
            color =  (255,255,255)
            stroke = 2
            cv2.putText(camera, "Not Recognized", (x,y), font, 1, color, stroke, cv2.LINE_AA)


        cv2.rectangle(camera, (x, y), (x+w, y+h), (153,50,204), 2)

    cv2.imshow('Video', camera)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Read csv file
        df_new = pd.read_csv('Attendance.csv')
        now = datetime.now() 
        date = now.strftime("%b%dth")
        hour = now.strftime("%I%p")
        df_new.to_excel('Attendance_' + date + '_' + hour+ '.xlsx', sheet_name= 'hour-' + hour , index = False)
        break



video_capture.release()
cv2.destroyAllWindows()
