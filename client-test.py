import sys
from datetime import datetime
import pyautogui
import numpy
import tkinter as tk
from tkinter import messagebox
from tkinter import *
import os

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


def destroyWindow():
    global carnet
    global txtCarnet
    carnet = txtCarnet.get("1.0", "end-1c")
    global nombre
    global txtNombre
    nombre = txtNombre.get("1.0", "end-1c")
    existe = os.path.exists(f'Faces/{carnet}.jpg')
    if (existe):
        global ventana
        ventana.destroy()
    else:
        messagebox.showinfo("UNIMET Proctor - Alerta", "El carnet indicado no existe en los datos guardados del sistema, ponte en contacto con tu profesor o verifica el carnet introducido.")

# ----------INITIAL DATA RECOLLECTION:--------------

global carnet
global nombre
#print("Sistema: Introduce numero de carnet:")
#carnet = input()
#print("Sistema: Introduce Nombre y Apellido del estudiante:")
#nombre = input()

#INTERFAZ

global ventana
ventana = tk.Tk()
ventana.title("UNIMET Proctor - Estudiante")
canva = tk.Canvas(ventana, width=460, height=300, bg="#003b5a", bd=0, highlightthickness=0, relief='ridge')
ventana.geometry("460x300")
ventana['background']='#856ff8'
canva.place(x=0, y=0)

# Navbar
navbar = canva.create_rectangle(-20, -20, 480, 80, fill="#fdbb2d")
canva.create_text(220, 50, text="UNIMET Proctor - Estudiante", font=("italic bold", 22))

# Labels and TextBoxs Creation
lblCarnet = tk.Label(canva, text="Carnet:", font=("italic bold", 14), width = 8, height = 1,
                     bg="#003b5a", fg="#ffffff", justify= LEFT).place(x=86, y=120)

lblNombre = tk.Label(canva, text="Nombre:", font=("italic bold", 14), width = 8, height = 1,
                     bg="#003b5a", fg="#ffffff", bd=0, justify= LEFT).place(x=90, y=150)

global txtCarnet
txtCarnet = tk.Text(canva, font=("italic bold", 14), width = 20, height = 1, highlightthickness=0)
txtCarnet.place(x=170, y=120)

global txtNombre
txtNombre = tk.Text(canva, font=("italic bold", 14), width = 20, height = 1, highlightthickness=0)
txtNombre.place(x=170, y=150)

tk.Button(canva, text="Conectar al servidor", font=("italic bold", 14), width=26, bd=0,
          bg="#fdbb2d", highlightthickness=0, relief='ridge',
          command=destroyWindow).place(x=92, y=190)



ventana.mainloop()

#ALERTA FINAL
messagebox.showinfo("UNIMET Proctor - Alerta", "A partir de ahora comenzarás a compartir tu pantalla con el docente. Para dejar de compartir pulsa la tecla ESC.")

#CONECCTION WITH DE SERVER
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
    #print("USURPACION DE INDENTIDAD", identityTheft)
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
    helpersAlert.append(helpers)
    #print("HELPERS TO THE STUDENT", helpersAlert)
    counter = 0
    for alert in helpersAlert:
        if alert == helpers and helpers >= 1:
            counter += 1
    if counter != 10:
        return False
    return True

# -- GAZE OUTSIDE THE SCREEN


def gazeAlert(gazeTime, gazeRatio):
    message = ""
    if gazeRatio > 1.99:
        message = "Derecha"
    elif gazeRatio < 0.4:
        message = "Izquierda"
    else:
        message = "Centro"

    if gazeTime >= 1:
        # ACA ESTAMOS RETORNANDO UN ARREGLO QUE MANDA LA DIRECCION DE LA MIRADA Y EL TIEMPO QUE LA PERSONA LLEVA MIRANDO EN LA DIRECCION
        print("MIRADA ", message, gazeTime)
        return [message, gazeTime]

    return False

def userInSceneAlert(numberFaces):
    global checkNumberFaces
    global counterCheckNumberFaces
    if(numberFaces == 0):
        counterCheckNumberFaces = counterCheckNumberFaces + 1

        if(counterCheckNumberFaces >= 10):
            checkNumberFaces = True
            return True

    else:
        counterCheckNumberFaces = 0
        checkNumberFaces = False
        return False
    
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


def checkAlerts(numberPeople, sendPhoneAlert, sendLaptopAlert, sendNumberPeopleAlert, sendMouthMovementAlert, sendHelpersAlert, sendGazeAlert, sendIdentityTheftAlert, img):
###########FALTA EL GAZEEEEEE

    fechahora = str(datetime.now())

    global checkNumberFaces
    global counterCheckNumberFaces

    miradaAlerta = False

    if (sendGazeAlert != False):

        miradaDireccion = sendGazeAlert[0]
        tiempoDireccion = sendGazeAlert[1]

        if (miradaDireccion == "Derecha" and tiempoDireccion >= 0.8):
            miradaAlerta = True

        if (miradaDireccion == "Izquierda" and tiempoDireccion >= 0.8):
            miradaAlerta = True

    text = fechahora + "\n"
    messages = {}
    condition = False

    if(sendPhoneAlert):
        text = text + "\nSe detectó un teléfono"
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

    #if(sendNumberPeopleAlert):
        #text = text + "\nHabitación concurrida por personas"
    #    messages['sendNumberPeopleAlert']: True #ARREGLAAAAAAAAAAAAAAAAAAAAR
        #condition = True
    #else:
    #    messages['sendNumberPeopleAlert']: False

    if(sendMouthMovementAlert):
        text = text + "\nLabios en movimiento"
        messages['sendMouthMovementAlert']: True
        condition = True
    else:
        messages['sendMouthMovementAlert']: False

    if(sendHelpersAlert):
        text = text + "\nSe detectaron posibles ayudantes cerca"
        messages['sendHelpersAlert']: True
        condition = True
    else:
        messages['sendHelpersAlert']: False

    if(sendNumberPeopleAlert and numberPeople>=1):
        text = text + "\nSe detectó una habitación concurrida por personas"
        messages['sendNumberPeopleAlert']: True
        condition = True
    else:
        messages['sendNumberPeopleAlert']: False

    if(checkNumberFaces):
        text = text + "\nNo se detectó al estudiante en la habitación o cerca del computador"
        messages['checkNumberFaces']: True
        condition = True
        checkNumberFaces = False
        counterCheckNumberFaces = 0
    else:
        messages['checkNumberFaces']: False

    if(sendIdentityTheftAlert):
        text = text + "\nPotencial suplantación de identidad (No se reconoció al estudiante)"
        messages['sendIdentityTheftAlert']: True
        condition = True
    else:
        messages['sendIdentityTheftAlert']: False

    if(miradaAlerta):
        condition = True
        text = text + f"\nEstudiante mirando a la dirección {miradaDireccion} por {str(round(tiempoDireccion, 2))} seg."
        messages['sendGazeAlert']: True
    else:
        messages['sendGazeAlert']: False

    print(text)

    return miradaAlerta, text, messages, condition, fechahora

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
window_name = "UNIMET Proctor - Estudiante"
cap = cv2.VideoCapture(0)  # Abrir la camara para recibir video
# VARIABLES
img = None
imgOriginal = None
i = 0.0
pTime = 0
numberFaces = 0
phoneDetected = True
global checkNumberFaces
checkNumberFaces = False
global counterCheckNumberFaces
counterCheckNumberFaces = 0

initTime = time.time()
gazeDirection = [0, 0]
gazePlace = True
# DECLARING OUR MODELS
faceDetector = FaceDetector()
eyesAndMouth = EyesAndMouth()
objectDetector = ObjectDetector()
faceRecognizer = FaceRecognizer(carnet)

validationCycle = True
#cv2.startWindowThread()
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
while validationCycle:
    face_locations = []
    face_names = []
    success, img = cap.read()
    if img is not None:  # IF EXISTS FRAME
        imgOriginal = img
        imgMostrarEstudiante = img
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

        #Revisar si hay personas en la escena
        userInSceneReport = userInSceneAlert(numberFaces)

        miradaVerification, alertText, messages, alertVerification, fechahora = checkAlerts(numberPeople, sendPhoneAlert, sendLaptopAlert, sendNumberPeopleAlert, sendMouthMovementAlert,
                                               sendHelpersAlert, sendGazeAlert, sendIdentityTheftAlert, img)

        print("Posterior al check:", miradaVerification)

        # sendAlertToSystem(sendPhoneAlert, sendLaptopAlert, sendNumberPeopleAlert, sendMouthMovementAlert,
        #                  sendHelpersAlert, sendGazeAlert, sendIdentityTheftAlert, img)

        screen = None
        if(alertVerification == True):
            screen = numpy.asarray(pyautogui.screenshot().convert("RGB"))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        
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

        #VALIDATION GAZE AND VALIDATION DIRECTION TIME
        #alertaGaze = False
        #if(sendGazeAlert != False):
        #    alertaGaze = True

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

            imgPlus = convert_image_to_jpeg(img)
            capture = convert_image_to_jpeg(screen)

           # print(fechahora)
            sio.emit('dataAlert', {
                'carnet': carnet,
                'alert': alertText,
                'img': imgOriginal,
                'capture': capture,
                'alertPhone': int(sendPhoneAlert),
                'alertLaptop': int(sendLaptopAlert),
                'alertNumberPeople': int(sendNumberPeopleAlert),
                'alertMounth': int(sendMouthMovementAlert),
                'alertHelpers': int(sendHelpersAlert),
                'alertUserInScene': int(userInSceneReport),
                'alertIdentity': int(sendIdentityTheftAlert),
                'alertGaze': int(miradaVerification),
                'time': str(fechahora)
            })

            # Capturar pantalla.
            
            # Guardar imagen.
            # screenshot.save("screenshot.png")
            #capture = numpy.asarray(screenshot)
            #print("screenshot: --")
            #print(frame)
            #print("img:")
            #print(img)
            #break

        # print("2-------sio.emit")

        # GAZE PLACE SETTING
        gazePlace = not gazePlace
        # SHOWING THE PROCESSED IMAGE

        cv2.imshow(window_name, img)
        #cv2.destroyWindow(window_name)
        #key = cv2.waitKey(1) & 0xFF
        #print(key)
        #if key == 27:
        #    print("No estoy claro que carajo esta pasando")
        #    break
        key = cv2.waitKey(1) & 0xFF
        print(key)
        if key == 27:
            #print("No estoy claro que carajo esta pasando")
            #cv2.destroyAllWindows()
            validationCycle = False
            cv2.destroyWindow(window_name)
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            break

    i = i + 1

print("me sali")
cap.release()
print("Post release")
cv2.destroyAllWindows()
print("Post CV2")
sys.exit(1)