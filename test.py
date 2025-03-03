import tkinter as tk
from tkinter import ttk
import pyperclip

# Función para cargar datos desde el portapapeles
def cargar_datos_portapapeles():
    datos = pyperclip.paste()
    lineas = datos.split('\n')
    matriz_datos = [linea.split('\t') for linea in lineas if linea]
    return matriz_datos

# Función para mostrar los datos en un Treeview de tkinter
def mostrar_datos_en_treeview(tree, matriz_datos):
    # Limpiar el Treeview actual
    for item in tree.get_children():
        tree.delete(item)
    
    # Configurar las columnas del Treeview
    columnas = matriz_datos[0]
    tree["columns"] = columnas
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.W)
    
    # Añadir los datos al Treeview
    for fila in matriz_datos[1:]:
        tree.insert("", tk.END, values=fila)

# Configuración de la ventana principal
root = tk.Tk()
root.geometry("800x600")

root.title("Datos del Portapapeles en Tkinter")

# Crear el Treeview
tree = ttk.Treeview(root, show="headings")
tree.pack(expand=True, fill='both')

# Botón para cargar datos desde el portapapeles
boton_cargar = tk.Button(root, text="Cargar Datos desde el Portapapeles", command=lambda: mostrar_datos_en_treeview(tree, cargar_datos_portapapeles()))
boton_cargar.pack(pady=10)

# Ejecutar la aplicación
root.mainloop()