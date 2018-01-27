import cv2 as cv

cap = cv.VideoCapture(0)
face_cascade = cv.CascadeClassifier('/Users/xavilien/.virtualenvs/Hackathon/lib/python3.6/site-packages/cv2/data/'
                                    'haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('/Users/xavilien/.virtualenvs/Hackathon/lib/python3.6/site-packages/cv2/data/'
                                   'haarcascade_eye.xml')


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 1:
        for (x, y, w, h) in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) > 1:
                for (ex, ey, ew, eh) in eyes:
                    cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    # Display the resulting frame
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    print()

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
