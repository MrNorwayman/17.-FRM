import tkinter as tk
from tkinter import ttk

# Configuración de la ventana principal
root = tk.Tk()
root.geometry("600x400")
root.title("Tabla en Tkinter")

# Crear el Treeview
tree = ttk.Treeview(root, columns=("col1", "col2", ), show="headings")
tree.heading("col1", text="Columna 1")
tree.heading("col2", text="Columna 2")

# Añadir datos a la tabla
data = [(f"Fila {i+1}, Col 1", f"Fila {i+1}, Col 2", f"Fila {i+1}, Col 3") for i in range(50)]

for row in data:
    tree.insert("", tk.END, values=row)

# Función para manejar la selección de una fila
def on_select(event):
    selected_item = tree.selection()[0]
    item = tree.item(selected_item)
    print(f"Seleccionaste: {item['values']}")

# Asociar la función de selección al evento de clic
tree.bind("<<TreeviewSelect>>", on_select)

# Empaquetar el Treeview
tree.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()