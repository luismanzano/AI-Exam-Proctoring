from flask import Flask, render_template, Response
import cv2
from flask_socketio import SocketIO, send, emit

app = Flask(__name__) #START APP
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/") #MAIN ROUTE
def index():
    return render_template("index.html")

#@socketio.on('message')
#def enviarImg(msg):
#    send(msg, broadcast = True)

@socketio.on('my event')
def miEvento(msg):
    print("mi evento...")

@socketio.on('MensajeCliente')
def clienteMsg(msg):
    print(msg)
    emit('MensajeGlobal', msg, broadcast = True)
    #send(msg, broadcast = True) #enviar a todos los clientes

@socketio.on('dataCliente')
def sendImgWeb(msg):
    #print("-Sistema: Recibida img!")
    emit('dataWeb', msg, broadcast = True)
    #send(msg, broadcast = True) #enviar a todos los clientes

if __name__ == "__main__":
    socketio.run(app)
    #app.run(debug=True)

#cap.release()