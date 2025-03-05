import tkinter as tk
from tkinter import ttk
import pandas as pd
from io import StringIO

def load_data():
    try:
        # Leer datos del widget Text
        data = text_widget.get("1.0", tk.END)
        # Convertir los datos en un DataFrame
        df = pd.read_csv(StringIO(data), sep="\t", header=None)
        df.columns = ["Value1", "Value2", "Value3"]  # Asignar nombres a las columnas
        # Convertir el DataFrame en una matriz (lista de listas) y convertir los valores a float
        matrix = df.values.tolist()
        float_matrix = []
        for row in matrix:
            float_row = []
            for value in row:
                if isinstance(value, float):
                    float_row.append(value)
                else:
                    # Reemplazar comas y puntos según sea necesario
                    value = value.replace(",", ".")
                    float_row.append(float(value))
            float_matrix.append(float_row)
        # Limpiar el Treeview
        for i in tree.get_children():
            tree.delete(i)
        # Insertar datos en el Treeview
        for row in float_matrix:
            tree.insert("", "end", values=row)
        print("Matriz de datos:", float_matrix)  # Imprimir la matriz para verificar
    except Exception as e:
        print(f"Error al cargar los datos: {e}")

def on_focus_in(event):
    if text_widget.get("1.0", tk.END).strip() == placeholder:
        text_widget.delete("1.0", tk.END)
        text_widget.config(fg="black")

def on_focus_out(event):
    if text_widget.get("1.0", tk.END).strip() == "":
        text_widget.insert("1.0", placeholder)
        text_widget.config(fg="grey")

def update_line_numbers(event=None):
    text = text_widget.get("1.0", tk.END)
    lines = text.split("\n")
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)
    for i, line in enumerate(lines, start=1):
        line_numbers.insert(tk.END, f"{i}\n")
    line_numbers.config(state="disabled")

root = tk.Tk()
grid_config = tk.Frame(root)
grid_config.grid(row=0, column=0, padx=10, pady=10)

tree = ttk.Treeview(grid_config, columns=("col1", "col2", "col3"), show="headings")
tree.heading("col1", text="Value1", anchor=tk.W)
tree.heading("col2", text="Value2", anchor=tk.W)
tree.heading("col3", text="Value3", anchor=tk.W)

tree.column("col1", width=150)
tree.column("col2", width=150)
tree.column("col3", width=150)

tree.grid(row=0, column=0, padx=10, pady=10)

# Crear el widget Text para pegar los datos
placeholder = "Pega aquí los datos copiados desde Excel"
text_widget = tk.Text(root, height=10, width=50, fg="grey")
text_widget.insert("1.0", placeholder)
text_widget.bind("<FocusIn>", on_focus_in)
text_widget.bind("<FocusOut>", on_focus_out)
text_widget.bind("<KeyRelease>", update_line_numbers)
text_widget.grid(row=20, column=1, padx=10, pady=10)

# Crear el widget Text para mostrar los números de línea
line_numbers = tk.Text(root, width=4, height=10, state="disabled", bg="lightgrey")
line_numbers.grid(row=20, column=0, padx=10, pady=10)

# Botón para cargar datos desde el widget Text
load_button = tk.Button(root, text="Cargar datos desde el texto", command=load_data)
load_button.grid(row=21, column=1, padx=10, pady=10)

root.mainloop()