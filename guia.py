from tkinter import *
from tkinter import messagebox

# ------------------------Detalle Inicial Interfaz Grafica-------------------------


ventana = Tk()

canva = Canvas(ventana, width=850, height=550)

ventana.geometry("850x550")

#canva.create_oval(x0, y0, x1, y1, fill=color)

# -------------------------------Dibujando el grafo--------------------------------


# Color para grafos comunes

color = "#B7950B"

# Color grafo Javier

colorJavier = "#2471A3"

# Color Andreina

colorAndreina = "#CD6155"

# color Bar

colorBar = "#1E8449"

# color Discoteca

colorDiscoteca = "#A04000"

# color Cerveceria

colorCerveceria = "#5B2C6F"


# --------------------------Dibujando Aristas del grafo----------------------------

#Filas (Calles)

canva.create_line(30, 30, 470, 30, fill="black", width=2)  # Fila 1

canva.create_line(30, 110, 470, 110, fill="black", width=2)  # Fila 2

canva.create_line(30, 190, 470, 190, fill="black", width=2)  # Fila 3

canva.create_line(30, 270, 470, 270, fill="black", width=2)  # Fila 4

canva.create_line(30, 350, 470, 350, fill="black", width=2)  # Fila 5

canva.create_line(30, 430, 470, 430, fill="black", width=2)  # Fila 6


# Identificaciones a la izquierda

canva.create_text(520, 30, fill="black",

                  font="Times 20 italic bold", text="Calle 55")  # Fila1

canva.create_text(520, 110, fill="black",

                  font="Times 20 italic bold", text="Calle 54")  # Fila2

canva.create_text(520, 190, fill="black",

                  font="Times 20 italic bold", text="Calle 53")  # Fila3

canva.create_text(520, 270, fill="black",

                  font="Times 20 italic bold", text="Calle 52")  # Fila4

canva.create_text(520, 350, fill="black",

                  font="Times 20 italic bold", text="Calle 51")  # Fila5

canva.create_text(520, 430, fill="black",

                  font="Times 20 italic bold", text="Calle 50")  # Fila6


#Columnas (Carreras)

canva.create_line(30, 30, 30, 470, fill="black", width=2)  # Columna 1

canva.create_line(110, 30, 110, 470, fill="black", width=2)  # Columna 2

canva.create_line(190, 30, 190, 470, fill="black", width=2)  # Columna 3

canva.create_line(270, 30, 270, 470, fill="black", width=2)  # Columna 4

canva.create_line(350, 30, 350, 470, fill="black", width=2)  # Columna 5

canva.create_line(430, 30, 430, 470, fill="black", width=2)  # Columna 6


# Identificaciones abajo

canva.create_text(30, 490, fill="black",

                  font="Times 20 italic bold", text="C.15")  # Col1

canva.create_text(110, 490, fill="black",

                  font="Times 20 italic bold", text="C.14")  # Col2

canva.create_text(190, 490, fill="black",

                  font="Times 20 italic bold", text="C.13")  # Col3

canva.create_text(270, 490, fill="black",

                  font="Times 20 italic bold", text="C.12")  # Col4

canva.create_text(350, 490, fill="black",

                  font="Times 20 italic bold", text="C.11")  # Col5

canva.create_text(430, 490, fill="black",

                  font="Times 20 italic bold", text="C.10")  # Col6


# -------------------------Dibujando cada fila del grafo---------------------------

for i in range(6):  # Fila1

    canva.create_oval(10 + (80*i), 10, 50 + (80*i), 50, fill=color)

    canva.create_text(30 + (80*i), 30, fill="white", font="Times 20 italic bold",

                      text=str(i))


for i in range(6):  # Fila2, aqui vive Javier

    if i != 1 and i != 4:

        canva.create_oval(10 + (80*i), 90, 50 + (80*i), 130, fill=color)

        canva.create_text(30 + (80*i), 110, fill="white", font="Times 20 italic bold",

                          text=str(i+6))

    else:

        if i != 4:  # El Vertice donde vive Javier es de otro color

            canva.create_oval(10 + (80*i), 90, 50 + (80*i),

                              130, fill=colorJavier)

            canva.create_text(30 + (80*i), 110, fill="white", font="Times 20 italic bold",

                              text=str(i+6))

        else:  # El Vertice del Bar es de otro color

            canva.create_oval(10 + (80*i), 90, 50 + (80*i), 130, fill=colorBar)

            canva.create_text(30 + (80*i), 110, fill="white", font="Times 20 italic bold",

                              text=str(i+6))


for i in range(6):  # Fila3

    canva.create_oval(10 + (80*i), 170, 50 + (80*i), 210, fill=color)

    canva.create_text(30 + (80*i), 190, fill="white", font="Times 20 italic bold",

                      text=str(i+12))


for i in range(6):  # Fila4

    if i != 2:

        canva.create_oval(10 + (80*i), 250, 50 + (80*i), 290, fill=color)

        canva.create_text(30 + (80*i), 270, fill="white", font="Times 20 italic bold",

                          text=str(i+18))

    else:  # El Vertice donde vive Andreina es de otro color

        canva.create_oval(10 + (80*i), 250, 50 + (80*i),

                          290, fill=colorAndreina)

        canva.create_text(30 + (80*i), 270, fill="white", font="Times 20 italic bold",

                          text=str(i+18))


for i in range(6):  # Fila5

    canva.create_oval(10 + (80*i), 330, 50 + (80*i), 370, fill=color)

    canva.create_text(30 + (80*i), 350, fill="white", font="Times 20 italic bold",

                      text=str(i+24))


for i in range(6):  # Fila6

    if i != 1 and i != 3:

        canva.create_oval(10 + (80*i), 410, 50 + (80*i), 450, fill=color)

        canva.create_text(30 + (80*i), 430, fill="white", font="Times 20 italic bold",

                          text=str(i+30))

    else:

        if i != 3:  # El color de la discoteca

            canva.create_oval(10 + (80*i), 410, 50 + (80*i),

                              450, fill=colorDiscoteca)

            canva.create_text(30 + (80*i), 430, fill="white", font="Times 20 italic bold",

                              text=str(i+30))

        else:  # El color de la cerveceria

            canva.create_oval(10 + (80*i), 410, 50 + (80*i),

                              450, fill=colorCerveceria)

            canva.create_text(30 + (80*i), 430, fill="white", font="Times 20 italic bold",

                              text=str(i+30))


canva.place(x=0, y=0)


#Texto Derecha Superior
canva.create_text(720, 50, fill="#2C3E50", font="Times 16 italic bold",
                text="Cáculo de rutas mínimas:")

# Boton Discoteca
Button(ventana, text="Ruta mín. Discoteca", command=rutaDisco,
       font=("italic bold", 14), width=20).place(x=600, y=90)

# Boton Bar
Button(ventana, text="Ruta mín. Bar", command=rutaBar,
       font=("italic bold", 14), width=20).place(x=600, y=150)

# Boton Cerveceria
Button(ventana, text="Ruta mín. Cerveceria", command=rutaCerveceria,
       font=("italic bold", 14), width=20).place(x=600, y=210)

#Leyenda
#Texto Derecha Inferior
canva.create_text(720, 300, fill="#2C3E50", font="Times 16 italic bold",
                text="Leyenda:")

canva.create_oval(610, 320, 630, 340, fill="#2471A3")
canva.create_text(695, 330, fill="#2C3E50", font="Times 14 italic bold",
                text="Casa de Javier")
canva.create_oval(610, 350, 630, 370, fill="#CD6155")
canva.create_text(710, 360, fill="#2C3E50", font="Times 14 italic bold",
                text="Casa de Andreina")
canva.create_oval(610, 380, 630, 400, fill="#A04000")
canva.create_text(730, 390, fill="#2C3E50", font="Times 14 italic bold",
                text="Discoteca The Darkness")
canva.create_oval(610, 410, 630, 430, fill="#1E8449")
canva.create_text(695, 420, fill="#2C3E50", font="Times 14 italic bold",
                text="Bar La Pasión")                
canva.create_oval(610, 440, 630, 460, fill="#5B2C6F")
canva.create_text(720, 450, fill="#2C3E50", font="Times 14 italic bold",
                text="Cervecería Mi Rolita")

ventana.mainloop()
