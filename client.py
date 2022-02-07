import socketio
import cv2
from PIL import Image
import base64
import mediapipe as mp
import time
import threading

# IMPORT OUR MODELS FOR CV
from FaceDetector import FaceDetector
from EyesAndMouth import EyesAndMouth
from ObjectDetector import ObjectDetector
from FaceRecognizer import FaceRecognizer

# ----------INITIAL DATA RECOLLECTION:--------------

print("Sistema: Introduce numero de carnet:")
carnet = input()
print("Sistema: Introduce Nombre y Apellido del estudiante:")
nombre = input()
sio = socketio.Client()
sio.connect('http://localhost:5000')
print('Mi identificador es: ', sio.sid)

# NECESSARY AND AUXILIARY METHODS:

def convert_image_to_jpeg(image):
    # Encode frame as jpeg
    frame = cv2.imencode('.jpg', image)[1].tobytes()
    # Encode frame in base64 representation and remove
    # utf-8 encoding
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)

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

# CONNECTION EVENTS - SOCKETIO

@sio.event
def connect():
    print("I'm connected!")


@sio.event
def connect_error(data):
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


#-------INITIAL SETTINGS --------
# VIDEO-CAPTURE
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Abrir la camara para recibir video
# VARIABLES
img = None
imgOriginal = None
i = 0.0
pTime = 0
numberFaces = 0
phoneDetected = True

initTime = time.time()
gazeDirection = [0, 0]
gazePlace = True
# DECLARING OUR MODELS
faceDetector = FaceDetector()
eyesAndMouth = EyesAndMouth()
objectDetector = ObjectDetector()
faceRecognizer = FaceRecognizer()

while True:

    face_locations = []
    face_names = []

    success, img = cap.read()

    if img is not None: #IF EXISTS FRAME

        imgOriginal = img
        img = cv2.flip(img, 1)
        height, width = img.shape[:2]
        cv2.rectangle(img, (20, height - 200),
                      (400, height - 50), (191, 237, 52), 3)

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
        initTime = time.time()
        gazeTime(gazeDirection)

        # SEND IMG TO SERVER
        imgOriginal = convert_image_to_jpeg(imgOriginal)
        #if (i % 3 == 0.0):
        sio.emit('dataCliente', {'id': str(
                sio.sid), 'carnet': carnet, 'nombre': nombre, 
                'img': imgOriginal, 'numberPeople': int(numberPeople),
                'numberFaces': int(numberFaces), 'phoneDetected': int(phoneDetected),
                'laptopDetected': int(laptopDetected)})

        # GazePlace setting
        gazePlace = not gazePlace
        #print("----------")
        #print(numberPeople)
        #print("-------------------<<<<<<<<<<<<<<<<<<----------------")
        # SHOWING THE PROCESSED IMAGE
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key & 0xFF == 32:
            break
    
    i = i + 1