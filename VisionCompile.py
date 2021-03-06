import cv2
import mediapipe as mp
import time
from flask import Flask, render_template, Response
import threading

# IMPORT OUR MODELS FOR CV
from FaceDetector import FaceDetector
from EyesAndMouth import EyesAndMouth
from ObjectDetector import ObjectDetector
from FaceRecognizer import FaceRecognizer

app = Flask(__name__)

cap = cv2.VideoCapture(0)

def drawFaces(img, faceNumbers):
    height, width = img.shape[:2]
    supporters = faceNumbers - 1
    cv2.putText(img, f' Acompañantes del estudiante: {supporters}', (20, height - 60), cv2.FONT_HERSHEY_PLAIN, 1,
                (255, 255, 255), 1)


def drawFaceRecognitionRectangles(img, face_locations, face_names):
    if len(face_locations) > 0 and len(face_names) > 0:
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


def drawMouthOpen(img, openMouthRatio):
    height, width = img.shape[:2]

    if openMouthRatio > 0.3:
        cv2.putText(img, "Boca Abierta", (20, height-100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    else:
        cv2.putText(img, "Boca Cerrada", (20, height - 100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)


def drawGazeRatio(img, gazeRatio):
    height, width = img.shape[:2]
    if gazeRatio > 1.99:
        cv2.putText(img, f'Mirando a la Derecha, {gazeRatio}', (20, height - 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        return 2
    elif 0.2 < gazeRatio < 1.99:
        cv2.putText(img, f'En pantalla, {gazeRatio}', (20, height - 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        return 0
    elif gazeRatio < 0.4:
        cv2.putText(img, f'Mirando a la izquierda, {gazeRatio}', (20, height - 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        return 1

def drawObjectsAndPeople(img, numberPeople, phoneDetected, laptopDetected):
    height, width = img.shape[:2]
    cv2.putText(img, f' Numero de Personas: {numberPeople}', (20, height - 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    if phoneDetected:
        cv2.putText(img, f' Telefono Detectado', (20, height - 40), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    if laptopDetected:
        cv2.putText(img, f' Computador Detectado', (20, height - 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

global initTime
initTime = time.time()
gazeDirection = [0, 0]

def gazeTime(gazeDirection):
    global initTime
    currentTime = time.time()
    global passedTime
    passedTime = 0
    if gazeDirection[0] == gazeDirection[1]:
        print("PUTAAAA")
        passedTime = currentTime - initTime
    else:
        initTime = time.time()
        print("NOT PUTAAA")
    print("PASSED TIME", passedTime)




# VARIABLES WE NEED TO TRACK THE STUDENT
numberFaces = 0
phoneDetected = True



def main():
    cap = cv2.VideoCapture(0)
    pTime = 0

    # DECLARING OUR MODELS
    faceDetector = FaceDetector()
    eyesAndMouth = EyesAndMouth()
    objectDetector = ObjectDetector()
    faceRecognizer = FaceRecognizer()


    gazePlace = True
    while True:
        face_locations = []
        face_names = []
        success, img = cap.read()
        img = cv2.flip(img, 1)
        height, width = img.shape[:2]
        cv2.rectangle(img, (20, height - 200), (400, height - 50), (191, 237, 52), 3)

        # HERE WE COUNT THE FACES
        bboxs, numberFaces = faceDetector.findFaces(img)
        drawFaces(img, numberFaces)

        # HERE WE RECOGNIZE THAT THE PERSON IN THE TEST IS WHO THEY CLAIM TO BE
        face_locations, face_names = faceRecognizer.RecognizeFaces(img)
        drawFaceRecognitionRectangles(img, face_locations, face_names)

        # HERE WE DETECT THE FACEMESH AND KNOW IF THE PERSON IN TALKING OR IF ITS LOOKING SOMEWHERE ELSE
        openMouthRatio, gazeRatio = eyesAndMouth.findAttributes(img)
        drawMouthOpen(img, openMouthRatio)
        if gazePlace:
            gazeDirection[0] = drawGazeRatio(img, gazeRatio)
        else:
            gazeDirection[1] = drawGazeRatio(img, gazeRatio)

        # HERE WE DETECT THE OBJECTS IN THE SCENE
        numberPeople, phoneDetected, laptopDetected  = objectDetector.DetectObjects(img)
        drawObjectsAndPeople(img, numberPeople, phoneDetected, laptopDetected)
        # FPS SO WE CAN MEASURE THE PERFORMANCE OF THE APP
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"FPS: {int(fps)}", (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 0), 3)
        global initTime
        gazeTime(gazeDirection)

        # INTEGRATING THE FLASK FRAMEWORK SO WE CAN SHOW THIS ON A WEBPAGE
        if success:
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

        gazePlace = not gazePlace
        # SHOWING THE PROCESSED IMAGE
        # cv2.imshow("Image", img)
        # key = cv2.waitKey(1)
        # if key & 0xFF == 32:
        #     break

cap.release()
cv2.destroyAllWindows()

# FUNCTIONS NEEDED TO DISPLAY THE IMAGE ON THE BROWSER

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(main(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    while True:
        return render_template('index.html', phoneDetected=phoneDetected)


if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == "__main__":
#     main()