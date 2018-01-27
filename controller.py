import cv2 as cv
import threading

cap = cv.VideoCapture(0)
face_cascade = cv.CascadeClassifier('/Users/xavilien/.virtualenvs/Hackathon/lib/python3.6/site-packages/cv2/data/'
                                    'haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('/Users/xavilien/.virtualenvs/Hackathon/lib/python3.6/site-packages/cv2/data/'
                                   'haarcascade_eye.xml')


class FacialRecognition:
    def __init__(self):
        self.face_x = 0
        self.face_y = 0

    def capture(self):
        # Capture frame-by-frame
        ret, frame = cap.read()
        width = cap.get(3)  # float
        height = cap.get(4)  # float

        # Our operations on the frame come here
        processed = self.face_recognition(frame)

        if processed:
            self.face_x = processed[1]/width
            self.face_y = processed[2]/height

        # Display the resulting frame
        cv.imshow('Capture', frame)

    @staticmethod
    def face_recognition(frame):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=3, minNeighbors=5)

            if len(eyes) > 1:
                for (ex, ey, ew, eh) in eyes:
                        cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            return frame, x, y

        return False


FacialRecognition().capture()

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
