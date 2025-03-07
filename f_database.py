import ast
import os
import shutil
from tkinter import filedialog, messagebox

def read_text_file():
    with open('database.txt', 'r') as file:
        return file.readlines()

def copia_database():
    content = read_text_file()
    matriz_vent =[] #Crea la matriz de ventiladores
    for line in content:
        if line[0:4] == 'VENT':
            vent = line.split(';')
            vent[3] = ast.literal_eval(vent[3])
            matriz_vent.append(vent[1::])
    return matriz_vent

class EventoSimulado:
    def __init__(self, xdata, ydata):
        self.xdata = xdata
        self.ydata = ydata
        self.button = 1
        self.dragging = True
        self.inaxes = True

def add_vent(vent):
    # Nueva linea de ventilador
    text_ventilador = ('\nVENT;'+vent[0]+';'+vent[1]+';'+str(vent[2]))

    content = read_text_file()  # Lineas database
    ventiladores = []   # Se acumulan todas las lineas de ventiladores para ordenar a posterior
    content_new = []
    duplicado = False
    
    for line in content:    # Lee todas las lineas
        if line[0:4]=='VENT':   # Si la lineas es un ventilador
            vent_db = line.split(';')   # Divide la linea en una lista usando ; como separador
            ventiladores.append(line)
            # Si el mismo ventilador se encuentra significa que esta duplicado
            if vent_db[1]==vent[0] and vent_db[2]==vent[1]:
                duplicado = True
                messagebox.showerror("Adevertencia de duplicado", "El ventilador ya existe.\n Si desea cambiar sus datos es necesario editarlo.")
            
        else:
            content_new.append(line)

    if not duplicado:
        ventiladores.append(text_ventilador)
        ventiladores_ordenados = sorted(ventiladores)
    
    for vent in ventiladores_ordenados:
        content_new.append(vent)

    with open('database.txt', 'w') as file:
        file.writelines(content)
    return

def delete_vent(vent):
    lines = read_text_file()
    content=[]
    for line in lines:
        if line[0:4] == 'VENT':
            vent_db = line.split(';')
            if vent_db[1]==vent[0] and vent_db[2]==vent[1]:
                # Elimina la linea
                continue
        content.append(line)

    with open('database.txt', 'w') as file:
        file.writelines(content)
    return

def edit_vent(vent, edit_vent):
    lines = read_text_file()
    content=[]
    for line in lines:
        if line[0:4] == 'VENT':
            vent_db = line.split(';')
            if vent_db[1]==edit_vent[0] and vent_db[2]==edit_vent[1]:
                line = ('VENT;'+vent[0]+';'+vent[1]+';'+str(vent[2])+'\n')
        content.append(line)
            
    with open('database.txt', 'w') as file:
        file.writelines(content)
    return

def add_pdf(model):
    if model!="":
        ruta_pdf = filedialog.askopenfilename()
        print(ruta_pdf)
        if ruta_pdf!='':
            nuevo_nombre = f"PDF_Database/{model}.pdf"
            os.rename(ruta_pdf, nuevo_nombre)
    return

def change_pdf(model):
    ruta_pdf = filedialog.askopenfilename()
    if ruta_pdf!='':
        nuevo_nombre = f"PDF_Database/{model}.pdf"
        os.remove(f"PDF_Database/{model}.pdf")
        shutil.copy(ruta_pdf, nuevo_nombre)
    return

def delete_pdf(model):
    os.remove(f"PDF_Database/{model}.pdf")
    return
