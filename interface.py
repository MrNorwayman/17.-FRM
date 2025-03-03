import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.lines as lines
import f_grafics, f_database

## VARIABLES GENERALES INICIO ##
punto_curva = [500, 300]
# Se crea una copia temporal de la base de datos
matriz_vent = f_database.copia_database()
## VARIABLES GENERALES ACABAR ##

## VENTANA DE ELECCION VENTILADOR INICIO ##
class Informacion(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuración")
        self.geometry("400x300")
        self.minsize(400, 300)

        # Se inicializa la matriz de ventiladores, copia de database
        self.matriz_vent = matriz_vent

        # Configurar el grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Crear el Treeview
        self.tree = ttk.Treeview(self, columns=("col1", "col2"), show="headings")
        self.tree.heading("col1", text="BRAND", anchor=tk.W)
        self.tree.heading("col2", text="MODEL", anchor=tk.W)

        # Añadir elementos a la tabla
        for vent in self.matriz_vent:
            self.tree.insert("", tk.END, values=(vent[0], vent[1]))

        # Empaquetar el Treeview
        self.tree.grid(row=0, column=0, columnspan=2, pady=0, padx=0, sticky='wsne')

        # Asociar la función de selección al evento de clic
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Boton Actualizar
        self.b_actualizar = ctk.CTkButton(self, text="Actualizar", command=self.actualizar_copia_database, height=50)
        self.b_actualizar.grid(row=1, column=0, padx=5, pady=5, sticky="wsne")

        # Boton add
        self.b_add_vent = ctk.CTkButton(self, text="Añadir Ventilador", command=self.add_vent, height=50)
        self.b_add_vent.grid(row=1, column=1, padx=5, pady=5, sticky="wsne")

    # Funcion actualizar copia de database
    def actualizar_copia_database(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.matriz_vent = f_database.copia_database()
        for vent in self.matriz_vent:
            self.tree.insert("", tk.END, values=(vent[0], vent[1]))
        print("The database have been actulized")

    #Funcion add ventilador
    def add_vent(self):
        print('pepe')

    # Funcion de seleccion de lista
    def on_select(self, event):
        selected_item = self.tree.selection()
        # Indice de la fila seleccionada
        index = self.tree.index(selected_item)
        # El ventilador seleccionado se pasa a la funcion de actualizar
        vent = self.matriz_vent[index]
        app.actualizar_graficas(vent)
        evento_simulado = f_database.EventoSimulado(xdata= vent[2][1][0]/2, ydata=vent[2][1][1]/2)
        app.on_move(evento_simulado, mode=1)
## VENTANA DE ELECCION VENTILADOR ACABAR ##

## INTERFAZ INICIO ##
class Interfaz(ctk.CTk):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.toplevel_window = None
        # Configurar el tema y la apariencia de customtkinter
        ctk.set_appearance_mode("dark")  # Opciones: "light", "dark"
        ctk.set_default_color_theme("blue")  # Cambia el tema de color

        # Crear la ventana principal
        self.title("FRM-Simulator")
        self.geometry("1200x700")
        self.minsize(700, 300)

        # Configurar el grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=5)
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
        self.b_abrir_conf = ctk.CTkButton(self, text="Configuración", command=self.open_toplevel, height=50)
        self.b_abrir_conf.grid(row=1, column=0, padx=10, pady=0, sticky="wsne")

        self.b_close = ctk.CTkButton(self, text="Cerrar", command=self.close, height=50)
        self.b_close.grid(row=2, column=0, padx=10, pady=10, sticky="wsne")
    ## CREACION DE BOTONES ACABAR ##

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
        self.m_correc = f_grafics.interpolar_factor_correccion(f_grafics.factor_correccion_radial)
        self.q_i, self.ps_i, self.N_i, self.Ws_i = f_grafics.extraer_datos(matriz_vent[0][2])
        self.curva_rpm_max_f, = self.ax.plot(self.q_i, self.ps_i, 'g--', linewidth=1.5, label='RPM maximas fabricante')
        self.curva_consumo_maximo_f, = self.ax_sub.plot(self.q_i, self.Ws_i, 'g--', linewidth=1.5, label='Consumo maximo fabricante')
        
        plt.subplots_adjust(hspace=0.02, top=0.99, bottom=0.05, left=0.05, right=0.99)

        self.q, self.ps = f_grafics.calcular_puntos_intermedios(self.q_i, self.ps_i)
        self.curva_rpm_max, = self.ax.plot(self.q, self.ps, 'r--', linewidth=1, label='RPM maximas interpoladas')
        self.band_1 = 0
        self.ax.set_xlim(0, max(self.q)*1.05)
        self.ax.set_ylim(0, max(self.ps)*1.05)

        self.q, self.Ws = f_grafics.calcular_puntos_intermedios(self.q_i, self.Ws_i)
        self.curva_consumo_maximo, = self.ax_sub.plot(self.q, self.Ws, 'b--', linewidth=1, label='Consumo maximo interpolado')
        self.ax_sub.set_xlim(0, max(self.q)*1.05)
        self.ax_sub.set_ylim(0, max(self.Ws)*1.05)

        self.consumo_disponible_nominal = self.q*self.ps/3600
        self.v_rendimiento_nominal = self.consumo_disponible_nominal / self.Ws * 100
        index_nominal = np.where(self.v_rendimiento_nominal == max(self.v_rendimiento_nominal))
        self.rendimiento_nominal = self.v_rendimiento_nominal[index_nominal]
        self.q_nominal = self.q[index_nominal]
        self.ps_nominal = self.ps[index_nominal]
        self.Ws_nominal = self.Ws[index_nominal]
        
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

    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Informacion(self)  # Crear la ventana si es None o está destruida
        else:
            self.toplevel_window.focus()

    def close(self):
        quit()
## INTERFAZ ACABAR ##

if __name__ == "__main__":
    app = Interfaz()
    app.mainloop()
