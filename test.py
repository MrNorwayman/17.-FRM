import tkinter as tk
from PIL import Image, ImageTk

# Crear la ventana principal
root = tk.Tk()

# Cargar y redimensionar la imagen
image_path = "Logo.PNG"
image = Image.open(image_path)
image = image.resize((512, 512), Image.LANCZOS)

# Guardar la imagen redimensionada como .ico
image.save("Carrier_anti.png")

# Establecer el icono de la ventana
root.iconbitmap("Carrier_anti.png")

# Crear un widget de etiqueta para mostrar la imagen (opcional)
photo = ImageTk.PhotoImage(image)
label = tk.Label(root, image=photo)
label.pack(pady=20)

# Ejecutar el bucle principal
root.mainloop()