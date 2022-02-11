from flask import Flask, render_template, Response, request, session
import cv2
from flask_socketio import SocketIO, send, emit, rooms, join_room
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)  # START APP
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_IMAGE'] = './Faces'  # Ruta para guardar imagenes de Rostros
app.config['UPLOAD_USER'] = './Users'  # Ruta para guardar data de los usuarios
global socketio
socketio = SocketIO(app)
global identificadorWeb
identificadorWeb = 0
global idsWeb
idsWeb = {}

@app.route("/")  # MAIN ROUTE
def index():
    return render_template("index.html")


@app.route("/pagina")
def pag():
    return render_template("upload.html")


@app.route("/registro", methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':

        # Obtener Imagen del Alumno
        archivo = request.files['imagen']
        filename = secure_filename(archivo.filename)

        # Obtener Datos del Alumno
        carnetAlumno = request.form.get('carnet')
        nombreAlumno = request.form.get('nombre')
        apellidoAlumno = request.form.get('apellido')

        # Guardamos la imagen en la carpeta "Faces"
        archivo.save(os.path.join(
            app.config['UPLOAD_IMAGE'], str(carnetAlumno) + ".jpg"))

        # Guardamos los datos del alumno en el JSON
        with open('./Users/students.json') as studentReadJSON:
            data = json.load(studentReadJSON)
            studentReadJSON.close()
        
        with open('./Users/students.json', 'w') as studentWriteJSON:

            data['students'].append({
                'carnet': carnetAlumno,
                'nombre': nombreAlumno,
                'apellido': apellidoAlumno
            })
            json.dump(data, studentWriteJSON)
            print(data)
            studentWriteJSON.close()            

        # Retornamos una respuesta satisfactoria
        return "<h1>Registro concluido exitosamente</h1>"

    if request.method == 'GET':
        return render_template("upload.html")


@ socketio.on('MensajeCliente')
def clienteMsg(msg):
    print(msg)
    emit('MensajeGlobal', msg, broadcast=True)
    # send(msg, broadcast = True) #enviar a todos los clientes


@ socketio.on('dataCliente')
def sendImgWeb(msg):
    global identificadorWeb
    #emit('dataWeb', msg, room='room')
    #SocketIO.broadcast.to(identificadorWeb).emit('dataWeb', msg)
    emit('dataWeb', msg, broadcast=True) #enviar a todos los clientes

@ socketio.on('idWeb')
def getIdWeb(msg):
    global identificadorWeb
    identificadorWeb = msg
    #room = session.get('room')
    #join_room(room)


if __name__ == "__main__":
    socketio.run(app)
    # app.run(debug=True)

# cap.release()
