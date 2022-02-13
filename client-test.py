import socketio
import cv2
from PIL import Image
import base64
import mediapipe as mp
import time
import threading
import atexit
import os
import shutil

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
sio.connect('http://127.0.0.1:5000')
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
            cv2.rectangle(img, (left, bottom - 35),
                          (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, name, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)


def drawMouthOpen(img, openMouthRatio):
    height, width = img.shape[:2]

    if openMouthRatio > 0.3:
        cv2.putText(img, "Boca Abierta", (20, height-100),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    else:
        cv2.putText(img, "Boca Cerrada", (20, height - 100),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)


def drawGazeRatio(img, gazeRatio):
    height, width = img.shape[:2]
    if gazeRatio > 1.99:
        cv2.putText(img, f'Mirando a la Derecha, {gazeRatio}', (
            20, height - 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        return 2
    elif 0.2 < gazeRatio < 1.99:
        cv2.putText(img, f'En pantalla, {gazeRatio}', (20, height - 70),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        return 0
    elif gazeRatio < 0.4:
        cv2.putText(img, f'Mirando a la izquierda, {gazeRatio}', (
            20, height - 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        return 1


def drawObjectsAndPeople(img, numberPeople, phoneDetected, laptopDetected):
    height, width = img.shape[:2]
    cv2.putText(img, f' Numero de Personas: {numberPeople}', (
        20, height - 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    if phoneDetected:
        cv2.putText(img, f' Telefono Detectado', (20, height - 40),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    if laptopDetected:
        cv2.putText(img, f' Computador Detectado', (20, height - 50),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)


global initTime
initTime = time.time()
gazeDirection = [0, 0]


def gazeTime(gazeDirection):
    global initTime
    currentTime = time.time()
    global passedTime
    passedTime = 0
    if gazeDirection[0] == gazeDirection[1]:
        passedTime = currentTime - initTime
    else:
        initTime = time.time()
    return passedTime


# ALERTS FOR THE TEACHER
# ---IDENTITY THEFT ALERT
global identityTheft
identityTheft = [False]


def identityTheftMethod(faceNames):
    if len(faceNames) > 1:
        return False

    if len(identityTheft) == 10:
        identityTheft.pop(0)
    if "CARA DESCONOCIDA" in faceNames:
        identityTheft.append(True)
    else:
        identityTheft.append(False)
    print("USURPACION DE INDENTIDAD", identityTheft)
    counter = 0
    for alert in identityTheft:
        if alert:
            counter += 1
    if counter != 10:
        return False
    return True


# ---PHONE DETECTED ALERT
global phoneAlert
phoneAlert = [False]


def phoneAlertMethod(phoneDetected):
    if len(phoneAlert) == 10:
        phoneAlert.pop(0)
    phoneAlert.append(phoneDetected)
    counter = 0
    for alert in phoneAlert:
        if alert:
            counter += 1
    if counter != 10:
        return False
    return True


# ---LAPTOP DETECTED ALERT
global laptopAlert
laptopAlert = [False]


def laptopAlertMethod(laptopDetected):
    if len(laptopAlert) == 10:
        laptopAlert.pop(0)
    laptopAlert.append(laptopDetected)
    counter = 0
    for alert in laptopAlert:
        if alert:
            counter += 1
    if counter != 10:
        return False
    return True


# ---NUMBER OF PEOPLE DETECTED ALERT
global numberPeopleAlert
numberPeopleAlert = [0]


def numberPeopleAlertMethod(numberPeople):
    if len(numberPeopleAlert) == 10:
        numberPeopleAlert.pop(0)
    numberPeopleAlert.append(numberPeople)
    counter = 0
    for alert in numberPeopleAlert:
        if alert == numberPeople:
            counter += 1
    if counter != 10 or numberPeople == 1:
        return False
    return True


# ---MOUTH MOVEMENT DETECTED ALERT
global mouthOpenAlert
mouthOpenAlert = [0]


def mouthMovementAlertMethod(mouthOpen):
    if len(mouthOpenAlert) == 10:
        mouthOpenAlert.pop(0)
    mouthOpenAlert.append(mouthOpen)
    counter = 0
    for alert in mouthOpenAlert:
        if alert >= 0.3:
            counter += 1
    if counter < 5:
        return False
    return True


# ---HELPERS TO THE STUDENT DETECTED
global helpersAlert
helpersAlert = [0]


def helpersAlertMethod(numberFaces):
    helpers = 0 if numberFaces == 1 else numberFaces - 1

    if len(helpersAlert) == 10:
        helpersAlert.pop(0)
    helpersAlert.append(numberPeople)
    print("HELPERS TO THE STUDENT", helpersAlert)
    counter = 0
    for alert in helpersAlert:
        if alert-1 == helpers:
            counter += 1
    if counter != 10:
        return False
    return True

# -- GAZE OUTSIDE THE SCREEN


def gazeAlert(gazeTime, gazeRatio):
    message = ""
    if gazeRatio > 1.99:
        message = "Derecha"
    else:
        if gazeRatio < 0.4:
            message = "Izquierda"
        else:
            message = "Centro"

    if gazeTime >= 1:
        # ACA ESTAMOS RETORNANDO UN ARREGLO QUE MANDA LA DIRECCION DE LA MIRADA Y EL TIEMPO QUE LA PERSONA LLEVA MIRANDO EN LA DIRECCION
        return [message, gazeTime]

    return False

# END OF ALERTS FOR THE TEACHER


# SENDING ALERTS TO THE SYSTEM
global alertsArray
alertsArray = []


def sendAlertToSystem(phoneAlert, laptopAlert, numberPeopleAlert,
                      mouthMovementAlert, helpersAlert, gazeAlert, identityTheftAlert, img):
    timeStamp = time.time()
    messages = []
    if phoneAlert:
        messages.append("Telefono")
    if laptopAlert:
        messages.append("Computador")
    if numberPeopleAlert:
        messages.append("Habitacion Concurrida")
    if mouthMovementAlert:
        messages.append("Labios en Movimiento")
    if helpersAlert:
        messages.append("El estudiante tiene potenciales ayudantes")
    if gazeAlert != False:
        messages.append(f"Mirando a la {gazeAlert[0]}, por {gazeAlert[1]}")
    if identityTheftAlert:
        messages.append(
            "Potencial robo de identidad en proceso (NO SE HA RECONOCIDO LA CARA DEL ESTUDIANTE)")

    cv2.imwrite(f"Alerts/{timeStamp}.jpg", img)
    path = f"Alerts/{timeStamp}.jpg"

    alert = [messages, path]

    alertsArray.append(alert)
# -- END SENDING ALERTS TO THE SYSTEM


def checkAlerts(sendPhoneAlert, sendLaptopAlert, sendNumberPeopleAlert, sendMouthMovementAlert, sendHelpersAlert, sendGazeAlert, sendIdentityTheftAlert, img):

    text = ""
    messages = {}
    condition = False

    if(sendPhoneAlert):
        text = "\nSe detectó un teléfono"
        messages['sendPhoneAlert']: True
        condition = True
    else:
        messages['sendPhoneAlert']: False

    if(sendLaptopAlert):
        text = text + "\nSe detectó un computador"
        messages['sendLaptopAlert']: True
        condition = True
    else:
        messages['sendLaptopAlert']: False

    if(sendNumberPeopleAlert):
        #text = text + "\nHabitación concurrida por personas"
        messages['sendNumberPeopleAlert']: False #ARREGLAAAAAAAAAAAAAAAAAAAAR
        #condition = True
    else:
        messages['sendNumberPeopleAlert']: False

    if(sendMouthMovementAlert):
        text = text + "\nLabios en movimiento"
        messages['sendMouthMovementAlert']: True
        condition = True
    else:
        messages['sendMouthMovementAlert']: False

    if(sendHelpersAlert):
        text = text + "\nSe detectaron posibles ayudantes"
        messages['sendHelpersAlert']: True
        condition = True
    else:
        messages['sendHelpersAlert']: False

    if(sendIdentityTheftAlert):
        text = text + "\nPotencial suplantación de identidad (No se reconoció al estudiante)"
        messages['sendIdentityTheftAlert']: True
        condition = True
    else:
        messages['sendIdentityTheftAlert']: False

    return text, messages, condition


def buildTextAlert(messages):

    text = ""

    if( messages['sendPhoneAlert'] ):
        text = "\nSe detectó un teléfono"

    if(messages['sendLaptopAlert']):
        text = text + "\nSe detectó un computador"

    if(messages['sendNumberPeopleAlert']):
        text = text + "\nHabitación concurrida por personas"

    if(messages['sendMouthMovementAlert']):
        text = text + "\nLabios en movimiento"

    if(messages['sendHelpersAlert']):
        text = text + "\nSe detectaron posibles ayudantes"

    if(messages['sendIdentityTheftAlert']):
        text = text + "\nPotencial suplantación de identidad (No se reconoció al estudiante)"

    return text

# REMOVE PICTURES FROM THE FOLDER AT EXIT


def deleteImagesInAlerts():
    folder = '/Alerts'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

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


# -------INITIAL SETTINGS --------
# VIDEO-CAPTURE
cap = cv2.VideoCapture('videotest.avi')  # Abrir la camara para recibir video
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
    if img is not None:  # IF EXISTS FRAME
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
        numberPeople, phoneDetected, laptopDetected = objectDetector.DetectObjects(
            img)

        # ALERTAS QUE VAS A ENVIAR AL CUADRO TIEMPO REAL
        sendPhoneAlert = phoneAlertMethod(phoneDetected)
        sendLaptopAlert = laptopAlertMethod(laptopDetected)
        sendNumberPeopleAlert = numberPeopleAlertMethod(numberPeople)
        sendMouthMovementAlert = mouthMovementAlertMethod(openMouthRatio)
        sendHelpersAlert = helpersAlertMethod(numberFaces)
        sendGazeAlert = gazeAlert(gazeTime(gazeDirection), gazeRatio)
        sendIdentityTheftAlert = identityTheftMethod(face_names)

        alertText, alert, alertVerification = checkAlerts(sendPhoneAlert, sendLaptopAlert, sendNumberPeopleAlert, sendMouthMovementAlert,
                                               sendHelpersAlert, sendGazeAlert, sendIdentityTheftAlert, img)

        # sendAlertToSystem(sendPhoneAlert, sendLaptopAlert, sendNumberPeopleAlert, sendMouthMovementAlert,
        #                  sendHelpersAlert, sendGazeAlert, sendIdentityTheftAlert, img)

        drawObjectsAndPeople(img, numberPeople, phoneDetected, laptopDetected)

        # FIN ALERTAS QUE VAS A ENVIAR AL CUADRO DE TIEMPO REAL

        # FPS SO WE CAN MEASURE THE PERFORMANCE OF THE APP
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"FPS: {int(fps)}", (20, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 0), 3)
        gazeTime(gazeDirection)

        # SEND IMG TO SERVER
        imgOriginal = convert_image_to_jpeg(imgOriginal)
        # if (i % 3 == 0.0):
        # print("1-------sio.emit")
        # sio.emit('dataCliente', {'id': str(
        #        sio.sid), 'carnet': carnet, 'nombre': nombre,
        #        'img': imgOriginal, 'numberPeople': int(numberPeople),
        #        'numberFaces': int(numberFaces), 'phoneDetected': int(phoneDetected),
        #        'laptopDetected': int(laptopDetected)})

        sio.emit('dataCliente', {
            'id': str(sio.sid),
            'carnet': carnet,
            'nombre': nombre,
            'img': imgOriginal,
            'numberPeople': int(numberPeople),
            'numberFaces': int(numberFaces),
            'alertNumber': int(sendNumberPeopleAlert),
            'identity': int(sendIdentityTheftAlert),
            'mounthMovement': int(sendMouthMovementAlert),
            'helpers': int(sendHelpersAlert),
            'phoneDetected': int(sendPhoneAlert),
            'laptopDetected': int(sendLaptopAlert),
            'gaze': sendGazeAlert
        })

        if(alertVerification):
            print(
                "-------------------------------------COSAS EXTRAÑAS----------------------------------------")
            sio.emit('dataAlert', {
                'carnet': carnet,
                'alert': alertText,
                'img': imgOriginal
            })

        # print("2-------sio.emit")

        # GAZE PLACE SETTING
        gazePlace = not gazePlace
        # SHOWING THE PROCESSED IMAGE

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key & 0xFF == 32:
            break

    i = i + 1

# atexit.register(deleteImagesInAlerts)