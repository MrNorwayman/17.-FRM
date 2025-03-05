import tkinter as tk
from tkinter import filedialog

# Crear una ventana raíz oculta
root = tk.Tk()
root.withdraw()

# Abrir el cuadro de diálogo para seleccionar un archivo
ruta_archivo = filedialog.askopenfilename()

print(f'Archivo seleccionado: {ruta_archivo}')