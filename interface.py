import tkinter as tk
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
        self.matriz_vent = f_database.copia_database()
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        # Tabla de datos
        columns=("col1","col2","col3", "col4")
        self.tabla = ttk.Treeview(self ,columns=columns, show="headings")
        self.tabla.heading("col1", text="Caudal [m^3/h]", anchor='w')
        self.tabla.heading("col2", text="Pressure [Pa]", anchor='w')
        self.tabla.heading("col3", text="Speed [rpm]", anchor='w')
        self.tabla.heading("col4", text="Power [W]", anchor='w')
        for column in columns:
            self.tabla.column(column, width=125)
        self.tabla.grid(row=1, column=0, columnspan=3, padx=5, sticky="wsne")

        # Entrada de texto copiado en Excel
        self.placeholder_entry="Insert Excel copied data of fan points"
        self.text_entry = tk.Text(self, height=10, width=30)
        self.text_entry.insert("1.0", self.placeholder_entry)
        self.text_entry.config(fg="grey")
        self.text_entry.bind("<FocusIn>", self.on_focus_in)
        self.text_entry.bind("<FocusOut>", self.on_focus_out)
        self.text_entry.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky='nswe')

        # Botones inferiores
        self.b_save = ctk.CTkButton(self, text="Save", command=self.save, height=30)
        self.b_save.grid(row=3, column=2, padx=5, sticky="wsne")
        self.b_add_pdf = ctk.CTkButton(self, text="Load PDF", command=self.add_pdf, height=30)
        self.b_add_pdf.grid(row=3, column=0, columnspan=2, padx=5, sticky="wsne")
        self.b_del_vent = ctk.CTkButton(self, text="Delete", command=self.delete, height=30)
        self.b_del_vent.grid(row=4, column=2, padx=5, pady=5, sticky="wsne")
        self.b_del_pdf = ctk.CTkButton(self, text="Change PDF", command=self.change_pdf, height=30)
        self.b_del_pdf.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="wsne")

        # Entrada de marca y modelo
        self.entry_brand = ctk.CTkEntry(self, placeholder_text="Entry brand...", width=50, height=30)
        self.entry_brand.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.entry_model = ctk.CTkEntry(self, placeholder_text="Entry model...", width=50, height=30)
        self.entry_model.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.edit_vent = edit_vent
        if self.edit_vent!=[]:
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.config(fg="black")     
            self.entry_brand.insert(0, self.edit_vent[0])
            self.entry_model.insert(0, self.edit_vent[1])
            for punto in self.edit_vent[2]:
                self.text_entry.insert("0.0", f"{str(punto[0])}\t{punto[1]}\t{punto[2]}\t{punto[3]}\n")
            self.on_focus_out(event=True)

    def load_data(self):
        try:
            # Leer datos del widget Text
            data = self.text_entry.get("1.0", tk.END)
            # Convertir los datos en un DataFrame
            df = pd.read_csv(StringIO(data), sep="\t", header=None)
            df.columns = ["Caudal", "Pressure","Speed","Power"]  # Asignar nombres a las columnas
            # Convertir los datos en matriz de listas
            matrix = df.values.tolist()
            self.float_matrix = []
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
            messagebox.showwarning("Carga de datos",f"Error al cargar los datos: {e}\n introduzca los datos correctamente")
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
        if brand=="":
            messagebox.showwarning("Error marca", "No ha introducido marca.\n Introduzca una marca.")
            return
        elif model=="":
            messagebox.showwarning("Error modelo", "No ha introducido modelo.\n Introduzca un modelo.")
            return
        else:
            self.load_data()
            if self.float_matrix==[]:
                messagebox.showwarning("Carga de datos",f"Error al cargar los datos.\n introduzca los datos correctamente.")
                return
            else:
                self.new_vent=[brand, model, self.float_matrix]
            
            if self.edit_vent==[]:
                self.add()

            else:
                self.edit()
        return
    
    def edit(self):
        self.matriz_vent = f_database.copia_database()
        print(self.new_vent)
        f_database.edit_vent(self.new_vent, self.edit_vent)
            
        self.matriz_vent = f_database.copia_database()
        messagebox.showinfo("Guardado", "Ventilador editado")
        app.actualizar_copia_database()
        self.destroy()
        return

    def add(self):
        f_database.add_vent(self.new_vent)
        self.matriz_vent = f_database.copia_database()
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
## VENTANA DE SELECCION VENTILADOR ACABAR ##

## INTERFAZ INICIO ##
class Interfaz(ctk.CTk):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.toplevel_window = None
        # Configurar el tema y la apariencia de customtkinter
        ctk.set_appearance_mode("dark")  # Opciones: "light", "dark"
        ctk.set_default_color_theme("blue")  # Cambia el tema de color

        self.matriz_vent = f_database.copia_database()
        self.vent = []

        # Crear la ventana principal
        self.title("FRM-Simulator")
        self.geometry("1200x700")
        self.minsize(700, 300)

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
        for i in range(8):
            grid_botones.grid_rowconfigure(i, weight=0)

        # Texto y entrada para el caudal
        subgrid_q = ctk.CTkFrame(grid_botones)
        subgrid_q.grid(row=0, column=0, padx=7, pady=7, sticky="nsew")
        self.label_q = ctk.CTkLabel(subgrid_q, text="Caudal [m^3/h]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_q.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.entry_q = ctk.CTkEntry(subgrid_q, placeholder_text="Establece Caudal [m^3/h]", width=150, height=30)
        self.entry_q.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Texto y entrada para la presión disponible
        subgrid_ps = ctk.CTkFrame(grid_botones)
        subgrid_ps.grid(row=1, column=0, padx=7, pady=7, sticky="nsew")
        self.label_ps = ctk.CTkLabel(subgrid_ps, text="Presión disponible [Pa]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_ps.grid(row=0, column=0, padx=0, pady=0, sticky="ns")
        self.entry_ps = ctk.CTkEntry(subgrid_ps, placeholder_text="Establece Presión [Pa]", width=150, height=30)
        self.entry_ps.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Texto y entrada para las revoluciones
        subgrid_n = ctk.CTkFrame(grid_botones)
        subgrid_n.grid(row=2, column=0, padx=7, pady=7, sticky="nsew")
        self.label_n = ctk.CTkLabel(subgrid_n, text="Revoluciones [rpm]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_n.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el consumo
        subgrid_Ws = ctk.CTkFrame(grid_botones)
        subgrid_Ws.grid(row=3, column=0, padx=7, pady=7, sticky="nsew")
        self.label_Ws = ctk.CTkLabel(subgrid_Ws, text="Consumo [W]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_Ws.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el consumo disponible
        subgrid_W_mecanica = ctk.CTkFrame(grid_botones)
        subgrid_W_mecanica.grid(row=4, column=0, padx=7, pady=7, sticky="nsew")
        self.label_W_mecanica = ctk.CTkLabel(subgrid_W_mecanica, text="Potencia Mecánica [W]: 00000.00", font=("Helvetica", 20), width=350, anchor='w')
        self.label_W_mecanica.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el rendimiento
        subgrid_rend = ctk.CTkFrame(grid_botones)
        subgrid_rend.grid(row=5, column=0, padx=7, pady=7, sticky="nsew")
        self.label_rend = ctk.CTkLabel(subgrid_rend, text="Rendimiento [%]: 000.00", font=("Helvetica", 20), width=250, anchor='w')
        self.label_rend.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

    ## CREACION DE BOTONES INICIO ##
        self.b_abrir_conf = ctk.CTkButton(self, text="Añadir Ventilador", command=self.open_toplevel, height=50)
        self.b_abrir_conf.grid(row=1, column=0, padx=10, pady=0, sticky="wsne")

        self.b_close = ctk.CTkButton(self, text="Cerrar", command=self.close, height=50)
        self.b_close.grid(row=2, column=0, padx=10, pady=10, sticky="wsne")
    ## CREACION DE BOTONES ACABAR ##

    ## PARTE DERECHA DE CONFIG INICIO ##
        grid_config = ctk.CTkFrame(self)
        grid_config.grid(row=0, column=3, rowspan=3, pady=10, sticky="nsew")

        # Configurar el grid
        grid_config.grid_columnconfigure(0, weight=1)
        grid_config.grid_columnconfigure(1, weight=1)
        grid_config.grid_columnconfigure(2, weight=1)
        grid_config.grid_rowconfigure(0, weight=1)
        grid_config.grid_rowconfigure(1, weight=0)

        # Crear el Treeview
        self.tree = ttk.Treeview(grid_config, columns=("col1", "col2"), show="headings")
        self.tree.heading("col1", text="BRAND", anchor=tk.W)
        self.tree.heading("col2", text="MODEL", anchor=tk.W)
        self.tree.column("col1", width=70)
        self.tree.column("col2", width=200)

        # Añadir elementos a la tabla
        for vent in self.matriz_vent:
            self.tree.insert("", tk.END, values=(vent[0], vent[1]))

        # Empaquetar el Treeview
        self.tree.grid(row=0, column=0, columnspan=3, pady=0, padx=0, sticky='wsne')

        # Asociar la función de selección al evento de clic
        self.tree.bind("<<TreeviewSelect>>", self.on_select_tree)

        # Boton Actualizar
        self.b_actualizar = ctk.CTkButton(grid_config, text="Actualizar", command=self.actualizar_copia_database, height=40, width=60)
        self.b_actualizar.grid(row=1, column=0, padx=5, pady=5, sticky="wsne")

        # Boton editar
        self.b_edit = ctk.CTkButton(grid_config, text="Editar", command=self.edit, height=40, width=60)
        self.b_edit.grid(row=1, column=1, padx=5, pady=5, sticky="wsne")

        # Boton pdf
        self.b_pdf = ctk.CTkButton(grid_config, text="Abrir PDF",command=self.abrir_pdf, height=40, width=60)
        self.b_pdf.grid(row=1, column=2, padx=5, pady=5, sticky="wsne")

    ## PARTE DERECHA DE CONFIG ACABAR ##

    ## CONFIGURACION DE GRAFICA INICIO ##
        # Crear la figura de matplotlib con fondo oscuro
        self.fig, (self.ax, self.ax_sub) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        self.x = [punto_curva[0]]
        self.y = [punto_curva[1]]
        
        # Configuración del subplot principal
        self.fig.patch.set_facecolor('#242424')  # Fondo de la figura en negro
        self.ax.set_ylabel('Presión disponible [Pa]', color='#F0F0F0')
        self.ax.set_facecolor('#E0E0E0')  # Fondo de los ejes en negros
        self.ax.tick_params(axis='x', colors='#F0F0F0')  # Ticks del eje x en blanco
        self.ax.tick_params(axis='y', colors='#F0F0F0')  # Ticks del eje y en blanco
        self.ax.locator_params(axis="x", nbins=10)
        self.ax.locator_params(axis="y", nbins=10)
        self.ax.grid(True, linewidth=0.5, alpha=0.5)
        self.ax.set_xticks([])
        self.ax.set_xticklabels([])

        # Configuración del subplot más delgado debajo del principal
        self.ax_sub.set_facecolor('#E0E0E0')
        self.ax_sub.set_ylabel('Consumo [W]', color='#F0F0F0')
        self.ax_sub.set_xlabel('Caudal [m^3/h]', color='#F0F0F0')
        self.ax_sub.tick_params(axis='x', colors='#F0F0F0')
        self.ax_sub.tick_params(axis='y', colors='#F0F0F0')
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
        
        # Texto y entrada para el rendimiento nominal
        subgrid_rend_nominal = ctk.CTkFrame(grid_botones)
        subgrid_rend_nominal.grid(row=6, column=0, padx=7, pady=7, sticky="nsew")
        self.label_rend_nominal = ctk.CTkLabel(subgrid_rend_nominal, text=f"Rendimiento nominal: {self.rendimiento_nominal[0]:.2f}[%]", font=("Helvetica", 20), width=250, anchor='w')
        self.label_rend_nominal.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el potencia nominal
        subgrid_potencia_nominal = ctk.CTkFrame(grid_botones)
        subgrid_potencia_nominal.grid(row=7, column=0, padx=7, pady=7, sticky="nsew")
        self.label_potencia_nominal = ctk.CTkLabel(subgrid_potencia_nominal, text=f"Potencia punto nominal: {self.Ws_nominal[0]:.2f}[W]", font=("Helvetica", 20), width=250, anchor='w')
        self.label_potencia_nominal.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

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

    def actualizar_graficas(self, ventilador):
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
        self.label_rend_nominal.configure(text=f"Rendimiento nominal: {self.rendimiento_nominal[0]:.2f}[%]")
        self.label_potencia_nominal.configure(text=f"Potencia punto nominal: {self.Ws_nominal[0]:.2f}[W]")
        self.q, self.N = f_grafics.calcular_puntos_intermedios(self.q_i, self.N_i)

    def on_click(self, event):
        if event.button == 1:
            self.dragging = True

    def on_release(self, event):
        if event.button == 1:  
            self.dragging = False

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

    def actualizar_texto(self):
        self.label_q.configure(text=f"Caudal [m^3/h]: {punto_curva[0]:.2f}")
        self.label_ps.configure(text=f"Presión disponible [Pa]: {punto_curva[1]:.2f}")
        self.N_corte = np.interp(punto_curva[0], self.q_new_Nc, self.N_new_c)
        self.label_n.configure(text=f"Revoluciones [rpm]: {self.N_corte:.2f}")
        self.Ws_corte = np.interp(punto_curva[0], self.q_new_Nc, self.Ws_new_c) * self.m_correc[int(punto_curva[0]/max(self.q_i)*100)][int(punto_curva[1]/max(self.ps_i)*100)]
        self.label_Ws.configure(text=f"Consumo [W]: {self.Ws_corte:.2f}")

        self.W_mecanica = punto_curva[0] * punto_curva[1] / 3600
        self.label_W_mecanica.configure(text=f"Potencia Mecánica [W]: {self.W_mecanica:.2f}")
        self.rend_calculado = self.W_mecanica / self.Ws_corte * 100
        self.label_rend.configure(text=f"Rendimiento [%]: {self.rend_calculado:.2f}")

    def abrir_conf(self):
        self.open_toplevel()

    def edit(self):
        if self.vent!=[]:
            self.open_toplevel(vent=self.vent)

    def open_toplevel(self, vent=[]):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Add_Vent(self, vent)  # Crear la ventana si es None o está destruida
        else:
            self.toplevel_window.focus()

    def close(self):
        quit()

    def actualizar_copia_database(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.matriz_vent = f_database.copia_database()
        for vent in self.matriz_vent:
            self.tree.insert("", tk.END, values=(vent[0], vent[1]))  
        messagebox.showinfo("Actualizada", "Base de datos actualizada")

    def abrir_pdf(self):
        ruta_pdf = f"PDF_Database/{self.vent[1]}.pdf"
        subprocess.run(["start", ruta_pdf], shell=True)

    def on_select_tree(self, event):
        selected_item = self.tree.selection()
        # Indice de la fila seleccionada
        index = self.tree.index(selected_item)
        # El ventilador seleccionado se pasa a la funcion de actualizar
        self.vent = self.matriz_vent[index]
        app.actualizar_graficas(self.vent)
        evento_simulado = f_database.EventoSimulado(xdata= self.vent[2][1][0]/2, ydata=self.vent[2][1][1]/2)
        app.on_move(evento_simulado, mode=1)
## INTERFAZ ACABAR ##

if __name__ == "__main__":
    app = Interfaz()
    app.mainloop()
