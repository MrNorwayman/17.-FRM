import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import matplotlib.lines as lines
import f_grafics, f_database
import subprocess
from io import StringIO

# Se crea una copia temporal de la base de datos
punto_curva = [500, 300]

## VENTANA DE SELECCION VENTILADOR INICIO ##
class Add_Vent(ctk.CTkToplevel):
    def __init__(self, parent, edit_vent=[]):
        super().__init__(parent)
        self.title("Configuration")
        self.geometry("500x550")

        self.iconpath = ImageTk.PhotoImage(file='Logo.png')
        self.wm_iconbitmap()
        self.after(300, lambda: self.iconphoto(False, self.iconpath))

        self.matriz_vent, self.vector_marcas = f_database.copia_database()
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)
        self.grid_rowconfigure(7, weight=0)

        row_add_window = 0

        # Entrada de marca y modelo
        self.entry_brand = ctk.CTkEntry(self, placeholder_text="Entry brand...", width=50, height=30)
        self.entry_brand.grid(row=row_add_window, column=0, sticky="nsew", padx=5, pady=5)
        self.entry_model = ctk.CTkEntry(self, placeholder_text="Entry model...", width=50, height=30)
        self.entry_model.grid(row=row_add_window, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)
        row_add_window = row_add_window+1

        values = self.vent_types()
        self.UE_type = values[0]
        self.b_pdf_UE = ctk.CTkButton(self, text="PDF UE", command=self.open_UE, height=30, width=50)
        self.b_pdf_UE.grid(row=row_add_window, column=0, padx=5, pady=5, sticky="wsne")
        self.select_tipo = ctk.CTkOptionMenu(self, values=values, command=self.calculo_N_UE)
        self.select_tipo.grid(row=row_add_window, column=1, columnspan=2, padx=5, pady=5, sticky='nwse')
        row_add_window = row_add_window+1

        self.entry_N_UE = ctk.CTkEntry(self, placeholder_text="Entry N UE...", width=30, height=30)
        self.entry_N_UE.grid(row=row_add_window, column=0, sticky="nsew", padx=5, pady=5)
        self.entry_kW_UE = ctk.CTkEntry(self, placeholder_text="Entry kW UE...", width=30, height=30)
        self.entry_kW_UE.grid(row=row_add_window, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)
        row_add_window = row_add_window+1

        # Tabla de datos
        columns=("col1","col2","col3", "col4")
        self.tabla = ttk.Treeview(self ,columns=columns, show="headings")
        self.tabla.heading("col1", text="Caudal [m^3/h]", anchor='w')
        self.tabla.heading("col2", text="Pressure [Pa]", anchor='w')
        self.tabla.heading("col3", text="Speed [rpm]", anchor='w')
        self.tabla.heading("col4", text="Power [W]", anchor='w')
        for column in columns:
            self.tabla.column(column, width=125)
        self.tabla.grid(row=row_add_window, column=0, columnspan=3, padx=5, sticky="wsne")
        row_add_window = row_add_window+1

        # Entrada de texto copiado en Excel
        self.placeholder_entry="Insert Excel copied data of fan points"
        self.text_entry = tk.Text(self, height=10, width=30)
        self.text_entry.insert("1.0", self.placeholder_entry)
        self.text_entry.config(fg="grey")
        self.text_entry.bind("<FocusIn>", self.on_focus_in)
        self.text_entry.bind("<FocusOut>", self.on_focus_out)
        self.text_entry.grid(row=row_add_window, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')
        row_add_window = row_add_window+1

        # Botones inferiores
        self.b_save = ctk.CTkButton(self, text="Save", command=self.save, height=30)
        self.b_save.grid(row=row_add_window, column=2, padx=5, sticky="wsne")
        self.b_add_pdf = ctk.CTkButton(self, text="Load PDF", command=self.add_pdf, height=30)
        self.b_add_pdf.grid(row=row_add_window, column=0, columnspan=2, padx=5, sticky="wsne")
        row_add_window = row_add_window+1

        self.b_del_vent = ctk.CTkButton(self, text="Delete", command=self.delete, height=30, fg_color="#EB6464")
        self.b_del_vent.grid(row=row_add_window, column=2, padx=5, pady=5, sticky="wsne")
        self.b_del_pdf = ctk.CTkButton(self, text="Change PDF", command=self.change_pdf, height=30)
        self.b_del_pdf.grid(row=row_add_window, column=0, columnspan=2, padx=5, pady=5, sticky="wsne")
        row_add_window = row_add_window+1

        self.edit_vent = edit_vent
        if self.edit_vent!=[]:
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.config(fg="black")     
            self.entry_brand.insert(0, self.edit_vent[0])
            self.entry_model.insert(0, self.edit_vent[1])
            self.entry_N_UE.insert(0, self.edit_vent[3])
            self.entry_kW_UE.insert(0, self.edit_vent[4])
            self.select_tipo.set(self.edit_vent[5])
            for punto in self.edit_vent[2]:
                self.text_entry.insert("0.0", f"{str(punto[0])}\t{punto[1]}\t{punto[2]}\t{punto[3]}\n")
            self.on_focus_out(event=True)

    def load_data(self):
        self.float_matrix = []
        try:
            # Leer datos del widget Text
            data = self.text_entry.get("1.0", tk.END)
            # Convertir los datos en un DataFrame
            df = pd.read_csv(StringIO(data), sep="\t", header=None)
            df.columns = ["Caudal", "Pressure","Speed","Power"]  # Asignar nombres a las columnas
            # Convertir los datos en matriz de listas
            matrix = df.values.tolist()
            for row in matrix:
                float_row = []
                for value in row:
                    if isinstance(value, float):
                        float_row.append(value)
                    elif isinstance(value, int):
                        float_row.append(float(value))
                    else:
                        # Reemplazar comas y puntos según sea necesario
                        value = value.replace(",", ".")
                        float_row.append(float(value))
                self.float_matrix.append(float_row)
            # Limpiar el Treeview
            for i in self.tabla.get_children():
                self.tabla.delete(i)
            # Insertar datos en el Treeview
            for row in self.float_matrix:
                self.tabla.insert("", "end", values=row)
        except Exception as e:
            return

    def on_focus_in(self, event):
        if self.text_entry.get("1.0", tk.END).strip() == self.placeholder_entry:
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.config(fg="black")
        return

    def on_focus_out(self, event):
        if self.text_entry.get("1.0", tk.END).strip() == "":
            self.text_entry.insert("1.0", self.placeholder_entry)
            self.text_entry.config(fg="grey")
        self.load_data()
        return

    def add_pdf(self):
        model = self.entry_model.get()
        f_database.add_pdf(model)
        return

    def change_pdf(self):
        model = self.entry_model.get()
        f_database.change_pdf(model)
        return

    def save(self):
        brand=self.entry_brand.get()
        model=self.entry_model.get()
        N_UE=self.entry_N_UE.get()
        kW_UE=self.entry_kW_UE.get()
        
        if N_UE=="" or kW_UE=="" or self.UE_type=="Selecciona tipo de ventilador UE 2015...":
            N_UE=" "
            kW_UE = " "
            self.UE_type = " "
            respuesta = messagebox.askokcancel("Advertencia datos UE", "No ha introducido todos los datos UE.\n ¿Desea continuar sin calcular la eficiencia UE?.", default=messagebox.CANCEL)
            print(respuesta)
            if respuesta == False:
                return
            
        if brand=="":
            messagebox.showwarning("Error marca", "No ha introducido marca.\n Introduzca una marca.")
            return
        elif model=="":
            messagebox.showwarning("Error modelo", "No ha introducido modelo.\n Introduzca un modelo.")
            return
        else:
            self.load_data()
            if self.float_matrix==[]:
                messagebox.showwarning("Carga de datos",f"Error al cargar los datos.\nEl formato es: cuatro valores por punto separados por tabulaciones")
                return
            else:
                self.new_vent=[brand, model, self.float_matrix, N_UE, kW_UE, self.UE_type]
            
            if self.edit_vent==[]:
                self.add()

            else:
                self.edit()
        return
    
    def edit(self):
        self.matriz_vent, self.vector_marcas = f_database.copia_database()
        print(self.new_vent)
        f_database.edit_vent(self.new_vent, self.edit_vent)
            
        self.matriz_vent, self.vector_marcas = f_database.copia_database()
        messagebox.showinfo("Guardado", "Ventilador editado")
        app.actualizar_copia_database()
        self.destroy()
        return

    def add(self):
        f_database.add_vent(self.new_vent)
        self.matriz_vent, self.vector_marcas = f_database.copia_database()
        messagebox.showinfo("Guardado", "Ventilador añadido")
        app.actualizar_copia_database()
        self.destroy()
        return
           
    def delete(self):
        brand = self.entry_brand.get()
        model = self.entry_model.get()

        if brand!="" and model!="":
            respuesta = messagebox.askokcancel("Advertencia", f"¿Esta seguro de eliminar el ventilador {model} de {brand}?", default=messagebox.CANCEL)
            if respuesta:
                delete_vent=[brand, model]
                f_database.delete_vent(delete_vent)
                try:
                    f_database.delete_pdf(model)
                    self.destroy()
                    app.actualizar_copia_database()
                except:
                    self.destroy()
                    app.actualizar_copia_database()
                    return
        else:
            return
        
    def vent_types(self):
        vent_type = [
            "Selecciona tipo de ventilador UE 2015...",
            "Axial",
            "Centrifugo con palas curvadas hacia delante",
            "Centrifugo con palas radiales",
            "Centrifugo con palas curvadas hacia atras sin carcasa",
            "Mixto con palas curvadas hacia atras con carcasa",
            "Mixto centrifugo helicoidal",
            "Tangencial"
        ]
        return vent_type
    
    def calculo_N_UE(self, opcion):
        self.UE_type = opcion
        return

    def open_UE(self):
        ruta_pdf = "PDF_Database/UE.pdf"
        subprocess.run(["start", ruta_pdf], shell=True)
        return
## VENTANA DE SELECCION VENTILADOR ACABAR ##

## INTERFAZ INICIO ##
class Interfaz(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toplevel_window = None
        # Configurar el tema y la apariencia de customtkinter
        self.appearance = "light"
        color_potencias = "#A9E8B3"
        color_nominal = "#8A8A8A"
        color_curvas = "#EBBC4D"

        self.vent_type = []
        self.rend_UE = 0

        ctk.set_appearance_mode(self.appearance)  # Opciones: "light", "dark"
        ctk.set_default_color_theme("dark-blue")  # Cambia el tema de color

        self.iconpath = ImageTk.PhotoImage(file='Logo.png')
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

        self.matriz_vent, self.vector_marcas = f_database.copia_database()
        self.vent = []

        # Crear la ventana principal
        self.title("FRM-Simulator")
        self.geometry("1200x800")
        self.minsize(1000, 800)

        # Configurar el grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # Crear un Frame para el subgrid
        grid_botones = ctk.CTkFrame(self, corner_radius=10)
        grid_botones.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Configurar el grid dentro del grid_botones
        grid_botones.grid_columnconfigure(0, weight=0)
        for i in range(20):
            grid_botones.grid_rowconfigure(i, weight=0)

        row_grid_botones = 0

        # Imagen de logotipo
        image = Image.open("Logo.png")
        self.ruta_logo = ctk.CTkImage(light_image = image, size=(image.width/1.2, image.height/1.2))
        self.logo = ctk.CTkLabel(grid_botones, image=self.ruta_logo, text="")
        self.logo.grid(row=row_grid_botones, column=0, padx=5, pady=10, sticky='s')
        row_grid_botones = row_grid_botones+1

        # Texto y entrada para el caudal
        subgrid_q = ctk.CTkFrame(grid_botones, fg_color=color_curvas)
        subgrid_q.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_q = ctk.CTkLabel(subgrid_q, text="Caudal [m^3/h]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_q.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")
        self.entry_q = ctk.CTkEntry(subgrid_q, placeholder_text="Establece Caudal [m^3/h]", width=150, height=30)
        self.entry_q.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        row_grid_botones = row_grid_botones+1

        # Texto y entrada para la presión disponible
        subgrid_ps = ctk.CTkFrame(grid_botones, fg_color=color_curvas)
        subgrid_ps.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_ps = ctk.CTkLabel(subgrid_ps, text="Presión disponible [Pa]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_ps.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        self.entry_ps = ctk.CTkEntry(subgrid_ps, placeholder_text="Establece Presión [Pa]", width=150, height=30)
        self.entry_ps.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        row_grid_botones = row_grid_botones+1

        # Texto y entrada para las revoluciones
        subgrid_n = ctk.CTkFrame(grid_botones, fg_color=color_curvas)
        subgrid_n.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_n = ctk.CTkLabel(subgrid_n, text="Revoluciones [rpm]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_n.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Entrada presion disponible y ESP
        subgrid_ESP = ctk.CTkFrame(grid_botones)
        subgrid_ESP.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        subgrid_ESP.columnconfigure(0, weight=0)
        subgrid_ESP.columnconfigure(1, weight=1)
        subgrid_ESP.columnconfigure(2, weight=0)
        subgrid_ESP.columnconfigure(3, weight=1)
        self.label_PDisp = ctk.CTkLabel(subgrid_ESP, text="P.Disp:", font=("Helvetica", 20), width=50, anchor='w')
        self.label_PDisp.grid(row=0, column=0, padx=5, pady=0, sticky="nsw")
        self.entry_PDisp = ctk.CTkEntry(subgrid_ESP, placeholder_text="120 [Pa]", width=100, height=30)
        self.entry_PDisp.grid(row=0, column=1, sticky="nsw", padx=0, pady=2)
        self.label_ESP = ctk.CTkLabel(subgrid_ESP, text="ESP:", font=("Helvetica", 20), width=50, anchor='w')
        self.label_ESP.grid(row=0, column=2, padx=5, pady=2, sticky="nse")
        self.entry_ESP = ctk.CTkEntry(subgrid_ESP, placeholder_text="0 [Pa]", width=100, height=30)
        self.entry_ESP.grid(row=0, column=3, sticky="nse", padx=2, pady=2)
        row_grid_botones = row_grid_botones+1

        # Texto para el rendimiento UE
        subgrid_rend_UE = ctk.CTkFrame(grid_botones)
        subgrid_rend_UE.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_rend_UE = ctk.CTkLabel(subgrid_rend_UE, text="Rendimiento UE [%]: 000.00", font=("Helvetica", 20), width=250, anchor='w')
        self.label_rend_UE.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Texto para el rendimiento
        subgrid_rend = ctk.CTkFrame(grid_botones)
        subgrid_rend.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_rend = ctk.CTkLabel(subgrid_rend, text="Rendimiento [%]: 000.00", font=("Helvetica", 20), width=250, anchor='w')
        self.label_rend.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Texto para la correccion UE
        subgrid_correc_UE = ctk.CTkFrame(grid_botones, fg_color=color_potencias)
        subgrid_correc_UE.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_correc_UE = ctk.CTkLabel(subgrid_correc_UE, text="Corrección UE [W]: 000.00", font=("Helvetica", 20), width=250, anchor='w')
        self.label_correc_UE.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Texto para la potencia consumida
        subgrid_Ws = ctk.CTkFrame(grid_botones, fg_color=color_potencias)
        subgrid_Ws.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_Ws = ctk.CTkLabel(subgrid_Ws, text="Bruta [W]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_Ws.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Texto para la potencia neta
        subgrid_W_neta = ctk.CTkFrame(grid_botones, fg_color=color_potencias)
        subgrid_W_neta.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_W_neta = ctk.CTkLabel(subgrid_W_neta, text="Neta [W]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_W_neta.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Texto para la potencia util
        subgrid_W_mecanica = ctk.CTkFrame(grid_botones, fg_color=color_potencias)
        subgrid_W_mecanica.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_W_mecanica = ctk.CTkLabel(subgrid_W_mecanica, text="Útil [W]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_W_mecanica.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

    ## CREACION DE BOTONES INICIO ##
        self.b_abrir_conf = ctk.CTkButton(self, text="Añadir Ventilador", command=self.open_toplevel, height=50)
        self.b_abrir_conf.grid(row=1, column=0, padx=10, pady=0, sticky="wsne")

        self.b_close = ctk.CTkButton(self, text="Cerrar", command=self.close, height=50, fg_color="#EB6464")
        self.b_close.grid(row=2, column=0, padx=10, pady=10, sticky="wsne")
    ## CREACION DE BOTONES ACABAR ##

    ## PARTE DERECHA DE CONFIG INICIO ##
        grid_config = ctk.CTkFrame(self)
        grid_config.grid(row=0, column=3, rowspan=3, pady=10, sticky="nsew")

        # Configurar el grid
        grid_config.grid_columnconfigure(0, weight=0)
        grid_config.grid_columnconfigure(1, weight=0)
        grid_config.grid_columnconfigure(2, weight=0)
        grid_config.grid_rowconfigure(0, weight=0)
        grid_config.grid_rowconfigure(1, weight=1)
        grid_config.grid_rowconfigure(2, weight=0)

        modelo = tk.StringVar()
        modelo.trace_add('write', self.on_entry_change)
        self.filtro_modelo = ctk.CTkEntry(grid_config, placeholder_text="Modelo...", height=5, textvariable=modelo)
        self.filtro_modelo.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='nwse')

        self.marca = self.vector_marcas[0]
        self.filtro_marca = ctk.CTkOptionMenu(grid_config, values=self.vector_marcas, command=self.f_filtro_marca)
        self.filtro_marca.grid(row=0, column=0, padx=5, pady=5, sticky='nwse')
        self.f_filtro_marca(self.vector_marcas[0])

        # Crear el Treeview
        self.matriz_vent_filtro = self.matriz_vent
        self.tree = ttk.Treeview(grid_config, columns=("col1", "col2"), show="headings")
        self.tree.heading("col1", text="BRAND", anchor=tk.W)
        self.tree.heading("col2", text="MODEL", anchor=tk.W)
        self.tree.column("col1", width=70)
        self.tree.column("col2", width=200)

        # Añadir elementos a la tabla
        for vent in self.matriz_vent_filtro:
            self.tree.insert("", tk.END, values=(vent[0], vent[1]))

        # Empaquetar el Treeview
        self.tree.grid(row=1, column=0, columnspan=3, pady=0, padx=5, sticky='wsne')

        # Asociar la función de selección al evento de clic
        self.tree.bind("<<TreeviewSelect>>", self.on_select_tree)

        # Boton Actualizar
        self.b_actualizar = ctk.CTkButton(grid_config, text="Actualizar", command=self.actualizar_copia_database, height=40, width=60)
        self.b_actualizar.grid(row=2, column=0, padx=5, pady=5, sticky="wsne")

        # Boton editar
        self.b_edit = ctk.CTkButton(grid_config, text="Editar", command=self.edit, height=40, width=60)
        self.b_edit.grid(row=2, column=1, padx=5, pady=5, sticky="wsne")

        # Boton pdf
        self.b_pdf = ctk.CTkButton(grid_config, text="Abrir PDF",command=self.abrir_pdf, height=40, width=60)
        self.b_pdf.grid(row=2, column=2, padx=5, pady=5, sticky="wsne")

    ## PARTE DERECHA DE CONFIG ACABAR ##

    ## CONFIGURACION DE GRAFICA INICIO ##
        # Crear la figura de matplotlib con fondo oscuro
        self.fig, (self.ax, self.ax_sub) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        self.x = [punto_curva[0]]
        self.y = [punto_curva[1]]
        
        # Configuración del subplot principal
        if self.appearance == "dark":
            self.fig.patch.set_facecolor('#242424')  # Fondo de la figura en negro
            self.ax.set_ylabel('Presión disponible [Pa]', color='#F0F0F0')
            self.ax.set_facecolor('#E0E0E0')  # Fondo de los ejes en negros
            self.ax.tick_params(axis='x', colors='#F0F0F0')  # Ticks del eje x en blanco
            self.ax.tick_params(axis='y', colors='#F0F0F0')  # Ticks del eje y en blanco
        else:
            self.fig.patch.set_facecolor('#EBEBEB')  # Fondo de la figura en crema
            self.ax.set_ylabel('Presión disponible [Pa]')
            self.ax.tick_params(axis='x')  # Ticks del eje x en blanco
            self.ax.tick_params(axis='y')  # Ticks del eje y en blanco
        self.ax.locator_params(axis="x", nbins=10)
        self.ax.locator_params(axis="y", nbins=10)
        self.ax.grid(True, linewidth=0.5, alpha=0.5)
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])

        # Configuración del subplot más delgado debajo del principal
        if self.appearance == "dark":
            self.ax_sub.set_facecolor('#E0E0E0')
            self.ax_sub.set_ylabel('Consumo [W]', color='#F0F0F0')
            self.ax_sub.set_xlabel('Caudal [m^3/h]', color='#F0F0F0')
            self.ax_sub.tick_params(axis='x', colors='#F0F0F0')
            self.ax_sub.tick_params(axis='y', colors='#F0F0F0')
        else:
            self.ax_sub.set_ylabel('Consumo [W]')
            self.ax_sub.set_xlabel('Caudal [m^3/h]')
        self.ax_sub.locator_params(axis="x", nbins=10)
        self.ax_sub.locator_params(axis="y", nbins=5)
        self.ax_sub.grid(True, linewidth=0.5, alpha=0.5)

        # Curva de trabajo
        self.sc = self.ax.scatter(self.x, self.y, color='#000000')  # Punto curva trabajo

        qt, pst = f_grafics.calcular_curva_trabajo(punto_curva)
        self.curva_t, = self.ax.plot(qt, pst, 'k-', linewidth=0.5, label='Curva de trabajo')
        # Curva work
        self.vertical_line = lines.Line2D([punto_curva[0], punto_curva[0]], [0, 1], transform=self.ax.get_xaxis_transform(), color='g', linewidth=0.5)
        self.ax.add_line(self.vertical_line)
        self.vertical_line_sub = lines.Line2D([punto_curva[0], punto_curva[0]], [0, 1], transform=self.ax_sub.get_xaxis_transform(), color='g', linewidth=0.5)
        self.ax_sub.add_line(self.vertical_line_sub)
    ## CONFIGURACION DE GRAFICA ACABAR ##

    ## CURVAS DE GRAFICA INICIO ##
        # Curvas del fabricante
        self.m_correc = f_grafics.interpolar_factor_correccion(f_grafics.factor_correccion_radial)
        self.q_i, self.ps_i, self.N_i, self.Ws_i = f_grafics.extraer_datos(self.matriz_vent[0][2])
        self.curva_rpm_max_f, = self.ax.plot(self.q_i, self.ps_i, 'g--', linewidth=1.5, label='rpm maximas fabricante')
        self.curva_consumo_maximo_f, = self.ax_sub.plot(self.q_i, self.Ws_i, 'g--', linewidth=1.5, label='Consumo maximo fabricante')

        # Ajuste de la grafica a los bordes
        plt.subplots_adjust(hspace=0.02, top=0.99, bottom=0.05, left=0.07, right=0.99)

        # Curva caudal/presion maxima interpoladas
        self.q, self.ps = f_grafics.calcular_puntos_intermedios(self.q_i, self.ps_i)
        self.curva_rpm_max, = self.ax.plot(self.q, self.ps, 'r--', linewidth=1, label='rpm maximas interpoladas')
        self.band_1 = 0
        self.ax.set_xlim(0, max(self.q)*1.05)
        self.ax.set_ylim(0, max(self.ps)*1.05)

        # Curva caudal/potencia maxima interpolada
        self.q, self.Ws = f_grafics.calcular_puntos_intermedios(self.q_i, self.Ws_i)
        self.curva_consumo_maximo, = self.ax_sub.plot(self.q, self.Ws, 'b--', linewidth=1, label='Consumo maximo interpolado')
        self.ax_sub.set_xlim(0, max(self.q)*1.05)
        self.ax_sub.set_ylim(0, max(self.Ws)*1.05)

        # Calculo potencia disponible e interseccion
        self.consumo_disponible_nominal = self.q*self.ps/3600
        self.v_rendimiento_nominal = self.consumo_disponible_nominal / self.Ws * 100
        index_nominal = np.where(self.v_rendimiento_nominal == max(self.v_rendimiento_nominal))
        self.rendimiento_nominal = self.v_rendimiento_nominal[index_nominal]
        self.q_nominal = self.q[index_nominal]
        self.ps_nominal = self.ps[index_nominal]
        self.Ws_nominal = self.Ws[index_nominal]
        
        # Graficar punto
        self.p_nominal_ps = self.ax.scatter(self.q_nominal, self.ps_nominal, color='#FF0000' ,marker='^', label='Punto nominal')  # Punto curva trabajo
        self.p_nominal_Ws = self.ax_sub.scatter(self.q_nominal, self.Ws_nominal, color='#0000FF' ,marker='^', label='Consumo nominal')  # Punto curva trabajo
        
        # Texto para el rendimiento nominal
        subgrid_rend_nominal = ctk.CTkFrame(grid_botones, fg_color=color_nominal)
        subgrid_rend_nominal.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_rend_nominal = ctk.CTkLabel(subgrid_rend_nominal, text=f"Rendimiento nominal [%]: {self.rendimiento_nominal[0]:.2f}", font=("Helvetica", 20), width=250, anchor='w')
        self.label_rend_nominal.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        # Texto para el potencia nominal
        subgrid_potencia_nominal = ctk.CTkFrame(grid_botones, fg_color=color_nominal)
        subgrid_potencia_nominal.grid(row=row_grid_botones, column=0, padx=7, pady=2, sticky="nsew")
        self.label_potencia_nominal = ctk.CTkLabel(subgrid_potencia_nominal, text=f"Punto nominal [W]: {self.Ws_nominal[0]:.2f}", font=("Helvetica", 20), width=250, anchor='w')
        self.label_potencia_nominal.grid(row=0, column=0, padx=5, pady=0, sticky="ns")
        row_grid_botones = row_grid_botones+1

        self.q, self.N = f_grafics.calcular_puntos_intermedios(self.q_i, self.N_i)
    ## CURVAS DE GRAFICA ACABAR ##

        # Integrar la figura en el widget de Tkinter con bordes redondeados
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=15)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0, rowspan=3)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=1)

    ## MOVER PUNTO CURVA DE MONTAJE INICIO ##
        # Variables para controlar el estado del clic
        self.dragging = False
        # Conectar los eventos de clic y movimiento del ratón
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)
    
        return

    def actualizar_graficas(self, ventilador):        
        self.rend_UE = self.calc_rend_UE(ventilador)

        self.m_correc = f_grafics.interpolar_factor_correccion(f_grafics.factor_correccion_radial)
        self.q_i, self.ps_i, self.N_i, self.Ws_i = f_grafics.extraer_datos(ventilador[2])
        self.curva_rpm_max_f.set_data(self.q_i, self.ps_i)
        self.curva_consumo_maximo_f.set_data(self.q_i, self.Ws_i)

        self.q, self.ps = f_grafics.calcular_puntos_intermedios(self.q_i, self.ps_i)
        self.curva_rpm_max.set_data(self.q, self.ps)
        self.ax.set_xlim(0, max(self.q)*1.05)
        self.ax.set_ylim(0, max(self.ps)*1.05)

        self.q, self.Ws = f_grafics.calcular_puntos_intermedios(self.q_i, self.Ws_i)
        self.curva_consumo_maximo.set_data(self.q, self.Ws)
        self.ax_sub.set_xlim(0, max(self.q)*1.05)
        self.ax_sub.set_ylim(0, max(self.Ws)*1.05)

        self.consumo_disponible_nominal = self.q*self.ps/3600
        self.v_rendimiento_nominal = self.consumo_disponible_nominal / self.Ws * 100
        index_nominal = np.where(self.v_rendimiento_nominal == max(self.v_rendimiento_nominal))
        self.rendimiento_nominal = self.v_rendimiento_nominal[index_nominal]
        self.q_nominal = self.q[index_nominal]
        self.ps_nominal = self.ps[index_nominal]
        self.Ws_nominal = self.Ws[index_nominal]
        
        self.p_nominal_ps.set_offsets(np.column_stack((self.q_nominal, self.ps_nominal)))  # Punto curva trabajo
        self.p_nominal_Ws.set_offsets(np.column_stack((self.q_nominal, self.Ws_nominal)))  # Punto curva trabajo
        
        # Texto y entrada para el rendimiento nominal y la potencia nominal
        self.label_rend_nominal.configure(text=f"Rendimiento nominal [%]: {self.rendimiento_nominal[0]:.2f}")
        self.label_potencia_nominal.configure(text=f"Potencia punto nominal [W]: {self.Ws_nominal[0]:.2f}")
        self.label_rend_UE.configure(text=f"Rendimiento UE [%]: {self.rend_UE:.2f}")
        self.q, self.N = f_grafics.calcular_puntos_intermedios(self.q_i, self.N_i)
        return

    def on_click(self, event):
        if event.button == 1:
            self.dragging = True
        return

    def on_release(self, event):
        if event.button == 1:  
            self.dragging = False
        return

    def on_move(self, event, mode=0):
        if (self.dragging and event.inaxes) or mode==1:
            q, ps = event.xdata, event.ydata

            if self.entry_q.get() != "":
                q = float(self.entry_q.get())
            if self.entry_ps.get() != "":
                ps = float(self.entry_ps.get())

            self.x[0], self.y[0] = q, ps  # Mover solo el primer punto
            punto_curva[0], punto_curva[1] = q, ps # Mover curva work
            self.sc.set_offsets(np.column_stack((self.x, self.y)))
            qt, pst = f_grafics.calcular_curva_trabajo(punto_curva) # Calcular la curva de trabajo
            self.curva_t.set_data(qt, pst)  # Graficar la nueva curva de trabajo

            # Calcular y graficar el punto de intersección
            intersections = f_grafics.find_intersection(qt, pst, self.q, self.ps)   # Encontrar la intersección

            if intersections:
                f_q = punto_curva[0] / intersections[0][0]  # Factor de escala
                #se calcula el punto si este esta dentro del area de la curva a maximas rpms
                if f_q <= 1:
                    #calculo de las curvas
                    self.q_new, self.ps_new, self.N_new, self.Ws_new = f_grafics.crear_nueva_curva(self.q, self.ps, self.N, self.Ws, f_q, f_q**2, f_q, f_q**3)  # Crear la nueva curva
                    self.q_new_c, self.ps_new_c = f_grafics.calcular_puntos_intermedios(self.q_new, self.ps_new) # Calcular los puntos intermedios
                    self.q_new_Nc, self.N_new_c = f_grafics.calcular_puntos_intermedios(self.q_new, self.N_new) # Calcular los puntos intermedios
                    self.q_new_Wc, self.Ws_new_c = f_grafics.calcular_puntos_intermedios(self.q_new, self.Ws_new) # Calcular los puntos intermedios
                    self.consumo_disponible, self.rendimiento, max_rend, max_consumo_disp = f_grafics.crear_curva_consumo_disponible(self.q_new_c, self.ps_new_c, self.Ws_new_c) # Crear la curva de consumo disponible
                    self.actualizar_texto()

                    #creacion de las curvas en la grafica
                    if self.band_1 == 0:
                        self.curva_n_new, = self.ax.plot(self.q_new_c, self.ps_new_c, 'r-', linewidth=0.5, label='RPM calculada')
                        self.curva_Wn_new, = self.ax_sub.plot(self.q_new_Wc, self.Ws_new_c, 'b-', linewidth=0.5, label='Consumo calculada')
                        self.curva_consumo_disponible, = self.ax_sub.plot(self.q_new_c, self.consumo_disponible, 'y-', linewidth=0.5, label='Potencia mecanica')
                        self.band_1 = 1
                        self.ax.legend(loc='upper right')
                        self.ax_sub.legend(loc='lower right')

                    #actualizacion de las graficas
                    self.curva_n_new.set_data(self.q_new_c, self.ps_new_c)
                    self.curva_Wn_new.set_data(self.q_new_Wc, self.Ws_new_c)
                    self.curva_consumo_disponible.set_data(self.q_new_c, self.consumo_disponible)
                    self.vertical_line.set_xdata([q, q])
                    self.vertical_line_sub.set_xdata([q, q])
                                
                    self.canvas.draw_idle() # Actualizar la gráfica
        return

    def actualizar_texto(self):
        self.label_q.configure(text=f"Caudal [m^3/h]: {punto_curva[0]:.2f}")
        self.label_ps.configure(text=f"Presión disponible [Pa]: {punto_curva[1]:.2f}")
        self.N_corte = np.interp(punto_curva[0], self.q_new_Nc, self.N_new_c)
        self.label_n.configure(text=f"Revoluciones [rpm]: {self.N_corte:.2f}")
        self.Ws_corte = np.interp(punto_curva[0], self.q_new_Nc, self.Ws_new_c) * self.m_correc[int(punto_curva[0]/max(self.q_i)*100)][int(punto_curva[1]/max(self.ps_i)*100)]
        self.label_Ws.configure(text=f"Bruta [W]: {self.Ws_corte:.2f}")

        self.PDisp = 120
        self.ESP = 0
        if self.entry_PDisp.get()!="":
            self.PDisp = float(self.entry_PDisp.get())
        if self.entry_ESP.get()!="":
            self.ESP = float(self.entry_ESP.get())
        self.correc_UE = punto_curva[0]*(self.PDisp-self.ESP)/(self.rend_UE*36)
        self.label_correc_UE.configure(text=f"Correccion UE [W]: {self.correc_UE:.2f}")
        self.label_W_neta.configure(text=f"Neta [W]: {self.Ws_corte-self.correc_UE:.2f}")

        self.W_mecanica = punto_curva[0] * punto_curva[1] / 3600
        self.label_W_mecanica.configure(text=f"Útil [W]: {self.W_mecanica:.2f}")
        self.rend_calculado = self.W_mecanica / self.Ws_corte * 100
        self.label_rend.configure(text=f"Rendimiento [%]: {self.rend_calculado:.2f}")
        return

    def abrir_conf(self):
        self.open_toplevel()
        return

    def edit(self):
        if self.vent!=[]:
            self.open_toplevel(vent=self.vent)
        return

    def open_toplevel(self, vent=[]):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Add_Vent(self, vent)  # Crear la ventana si es None o está destruida
        else:
            self.toplevel_window.focus()
        return

    def close(self):
        quit()

    def actualizar_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for vent in self.matriz_vent_filtro:
            self.tree.insert("", tk.END, values=(vent[0], vent[1]))
        return  

    def actualizar_copia_database(self):
        self.matriz_vent, self.vector_marcas = f_database.copia_database()
        self.f_filtro_marca(self.marca)
        messagebox.showinfo("Actualizada", "Base de datos actualizada")
        return

    def abrir_pdf(self):
        ruta_pdf = f"PDF_Database/{self.vent[1]}.pdf"
        subprocess.run(["start", ruta_pdf], shell=True)
        return

    def on_select_tree(self, event):
        selected_item = self.tree.selection()
        # Indice de la fila seleccionada
        index = self.tree.index(selected_item)
        # El ventilador seleccionado se pasa a la funcion de actualizar
        self.vent = self.matriz_vent_filtro[index]
        app.actualizar_graficas(self.vent)
        evento_simulado = f_database.EventoSimulado(xdata= self.vent[2][1][0]/2, ydata=self.vent[2][1][1]/2)
        app.on_move(evento_simulado, mode=1)

    def f_filtro_marca(self, marca):
        # Si se selecciona la primera opccion "todos", se cargan todos los vents
        self.marca = marca
        if self.marca == self.vector_marcas[0]:
            self.matriz_vent_filtro_marca = self.matriz_vent
        
        else:
            self.matriz_vent_filtro_marca = []
            for ventilador in self.matriz_vent:
                if ventilador[0] == self.marca:
                    self.matriz_vent_filtro_marca.append(ventilador)
        
        self.on_entry_change()
        return
    
    def on_entry_change(self, *args):
        modelo = self.filtro_modelo.get()

        try:
            if modelo != "":
                matriz_vent_modelo = []
                for ventilador in self.matriz_vent_filtro_marca:
                    if ventilador[1][0:len(modelo)] == modelo:
                        matriz_vent_modelo.append(ventilador)
                        
                self.matriz_vent_filtro = matriz_vent_modelo

            else: self.matriz_vent_filtro = self.matriz_vent_filtro_marca

            self.actualizar_tree()
            return
        
        except:
            return
        
    def calc_rend_UE(self, vent):
        rend_UE = 0
        f1, f2 = self.factores_UE(vent[5])
        print(f1)
        if f1!=0:
            rend_UE = f1*np.log(float(vent[4])) - f2 + float(vent[3])
        return rend_UE

    def factores_UE(self, tipo):
        print(tipo)
        self.vent_type = [
            "Selecciona tipo de ventilador UE 2015...",
            "Axial",
            "Centrifugo con palas curvadas hacia delante",
            "Centrifugo con palas radiales",
            "Centrifugo con palas curvadas hacia atras sin carcasa",
            "Mixto con palas curvadas hacia atras con carcasa",
            "Mixto centrifugo helicoidal",
            "Tangencial"
        ]
        
        f1 = 0
        f2 = 0

        if tipo in (self.vent_type[1], self.vent_type[2]):
            f1 = 2.74
            f2 = 6.33
            return f1, f2
        
        elif tipo in (self.vent_type[3], self.vent_type[4], self.vent_type[5]):
            f1 = 4.56
            f2 = 10.5
            return f1, f2
                
        elif tipo == self.vent_type[6]:
            f1 = 1.14
            f2 = 2.6
            return f1, f2

        return f1, f2
## INTERFAZ ACABAR ##

if __name__ == "__main__":
    app = Interfaz()
    app.mainloop()
