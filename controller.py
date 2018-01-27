import cv2 as cv


class FacialRecognition:
    def __init__(self):
        self.face_x = 0

        self.cap = cv.VideoCapture(0)
        self.face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

    def capture(self, dt):
        # Capture frame-by-frame
        ret, frame = self.cap.read()
        width = self.cap.get(3)  # float
        height = self.cap.get(4)  # float

        # Our operations on the frame come here
        processed = self.face_recognition(frame)

        if processed:
            (x, y, w, h) = processed[1:]
            self.face_x = x/width
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            print(self.face_x)

        # Display the resulting frame
        cv.imshow('Capture', frame)

    def face_recognition(self, frame):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            return frame, x, y, w, h

        return False

    def stop(self):
        print(True)
        self.cap.release()
        cv.destroyAllWindows()


if __name__ == '__main__':
    fr = FacialRecognition()
