import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.lines as lines
import f_grafics

## VARIABLES GENERALES INICIO ##
punto_curva = [500, 300]
curva_rpm_max = np.array([
    [104.52, 1210.18, 1800, 1073.45], 
    [1687.54, 1167.32, 1800, 1685.65], 
    [3231.27, 1135.05, 1800, 2243.06],
    [4823, 1083.77, 1800, 2640.73],
    [6400.31, 1003.43, 1800, 2938.24],
    [7765.3, 877.02, 1800, 3040.93],
    [9292.04, 670.09, 1800, 2914.37],
    [10419.25, 469.44, 1800, 2888.45], 
    [11441.17, 244.1, 1800, 2564.21],
    [12392.44, 0, 1800, 2149.38]
])
curva_rpm_max_2 = np.array([
    [10605.45, 340.28, 1105, 3666.27],
    [11812.19, 296.56, 1105, 3332.06],
    [14336.78, 281.58, 1105, 3342.18],
    [16981.32, 255.66, 1105, 2870.25],
    [18970.7, 226.26, 1105, 2792.89],
    [21131.28, 190.16, 1105, 2695.64],
    [23405.1, 141.18, 1105, 2541.19],
    [26188.91, 70.68, 1105, 2315.32],
    [28911.25, 0, 1105, 2042.91]
])

curva_simulada = []
## VARIABLES GENERALES ACABAR ##

## INTERFAZ INICIO ##
class Interfaz(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el tema y la apariencia de customtkinter
        ctk.set_appearance_mode("dark")  # Opciones: "light", "dark"
        ctk.set_default_color_theme("blue")  # Cambia el tema de color

        # Crear la ventana principal
        self.title("FRM-Simulator")
        self.geometry("1200x700")
        self.minsize(700, 300)

        # Configurar el grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)

        # Crear un Frame para el subgrid
        grid_botones = ctk.CTkFrame(self, corner_radius=20)
        grid_botones.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Configurar el grid dentro del grid_botones
        grid_botones.grid_columnconfigure(0, weight=1)
        for i in range(6):
            grid_botones.grid_rowconfigure(i, weight=1)

        # Texto y entrada para el caudal
        subgrid_q = ctk.CTkFrame(grid_botones, corner_radius=17)
        subgrid_q.grid(row=0, column=0, padx=7, pady=7, sticky="nsew")
        self.label_q = ctk.CTkLabel(subgrid_q, text="Caudal [m^3/h]", font=("Helvetica", 20), corner_radius=10)
        self.label_q.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.entry_q = ctk.CTkEntry(subgrid_q, placeholder_text="Establece Caudal", width=150, height=50, corner_radius=15)
        self.entry_q.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Texto y entrada para la presión disponible
        subgrid_ps = ctk.CTkFrame(grid_botones, corner_radius=17)
        subgrid_ps.grid(row=1, column=0, padx=7, pady=7, sticky="nsew")
        self.label_ps = ctk.CTkLabel(subgrid_ps, text="Presión disponible", font=("Helvetica", 20), corner_radius=10)
        self.label_ps.grid(row=0, column=0, padx=0, pady=0, sticky="ns")
        self.entry_ps = ctk.CTkEntry(subgrid_ps, placeholder_text="Establece Presión", width=150, height=50, corner_radius=15)
        self.entry_ps.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Texto y entrada para las revoluciones
        subgrid_n = ctk.CTkFrame(grid_botones, corner_radius=17)
        subgrid_n.grid(row=2, column=0, padx=7, pady=7, sticky="nsew")
        self.label_n = ctk.CTkLabel(subgrid_n, text="Revoluciones", font=("Helvetica", 20), corner_radius=10)
        self.label_n.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el consumo
        subgrid_Ws = ctk.CTkFrame(grid_botones, corner_radius=17)
        subgrid_Ws.grid(row=3, column=0, padx=7, pady=7, sticky="nsew")
        self.label_Ws = ctk.CTkLabel(subgrid_Ws, text="Consumo", font=("Helvetica", 20), corner_radius=10)
        self.label_Ws.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el consumo disponible
        subgrid_W_mecanica = ctk.CTkFrame(grid_botones, corner_radius=17)
        subgrid_W_mecanica.grid(row=4, column=0, padx=7, pady=7, sticky="nsew")
        self.label_W_mecanica = ctk.CTkLabel(subgrid_W_mecanica, text="Potencia Mecánica [W]", font=("Helvetica", 20), corner_radius=10)
        self.label_W_mecanica.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

        # Texto y entrada para el rendimiento
        subgrid_rend = ctk.CTkFrame(grid_botones, corner_radius=17)
        subgrid_rend.grid(row=5, column=0, padx=7, pady=7, sticky="nsew")
        self.label_rend = ctk.CTkLabel(subgrid_rend, text="Rendimiento [%]", font=("Helvetica", 20), corner_radius=10)
        self.label_rend.grid(row=0, column=0, padx=0, pady=0, sticky="ns")

    ## CONFIGURACION DE GRAFICA INICIO ##
        # Crear la figura de matplotlib con fondo oscuro
        self.fig, (self.ax, self.ax_sub) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        self.x = [punto_curva[0]]
        self.y = [punto_curva[1]]
        
        # Configuración del subplot principal
        self.fig.patch.set_facecolor('#242424')  # Fondo de la figura en negro
        self.ax.set_ylabel('Presión disponible [Pa]', color='#F0F0F0')
        self.ax.set_facecolor('#E0E0E0')  # Fondo de los ejes en negro
        self.sc = self.ax.scatter(self.x, self.y, color='#000000')  # Puntos en blanco
        self.ax.tick_params(axis='x', colors='#F0F0F0')  # Ticks del eje x en blanco
        self.ax.tick_params(axis='y', colors='#F0F0F0')  # Ticks del eje y en blanco
        self.ax.locator_params(axis="x", nbins=10)
        self.ax.locator_params(axis="y", nbins=10)
        self.ax.grid(True, linewidth=0.5, alpha=0.5)

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
        qt, pst = f_grafics.calcular_curva_trabajo(punto_curva)
        self.curva_t, = self.ax.plot(qt, pst, 'k-', linewidth=0.5)
        # Curva work
        self.vertical_line = lines.Line2D([punto_curva[0], punto_curva[0]], [0, 1], transform=self.ax.get_xaxis_transform(), color='g', linewidth=0.5)
        self.ax.add_line(self.vertical_line)
        self.vertical_line_sub = lines.Line2D([punto_curva[0], punto_curva[0]], [0, 1], transform=self.ax_sub.get_xaxis_transform(), color='g', linewidth=0.5)
        self.ax_sub.add_line(self.vertical_line_sub)
    ## CONFIGURACION DE GRAFICA ACABAR ##

    ## CURVAS DE GRAFICA INICIO ##
        self.m_correc = f_grafics.interpolar_factor_correccion(f_grafics.factor_correccion_radial)
        self.q_i, self.ps_i, self.N_i, self.Ws_i = f_grafics.extraer_datos(curva_rpm_max)
        self.ax.plot(self.q_i, self.ps_i, 'g-', linewidth=1.5)
        self.ax_sub.plot(self.q_i, self.Ws_i, 'g-', linewidth=1.5)

        self.q, self.ps = f_grafics.calcular_puntos_intermedios(self.q_i, self.ps_i)
        self.curva_n, = self.ax.plot(self.q, self.ps, 'r-', linewidth=1)
        self.band_1 = 0
        self.ax.set_xlim(0, max(self.q)*1.05)
        self.ax.set_ylim(0, max(self.ps)*1.05)

        self.q, self.Ws = f_grafics.calcular_puntos_intermedios(self.q_i, self.Ws_i)
        self.ax_sub.plot(self.q, self.Ws, 'b-', linewidth=1)
        self.ax_sub.set_xlim(0, max(self.q)*1.05)
        self.ax_sub.set_ylim(0, max(self.Ws)*1.05)

        self.q, self.N = f_grafics.calcular_puntos_intermedios(self.q_i, self.N_i)
    ## CURVAS DE GRAFICA ACABAR ##

        # Integrar la figura en el widget de Tkinter con bordes redondeados
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=15)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=1)

        # Añadir un cuadro de texto debajo de la gráfica con bordes redondeados
        self.text_box = ctk.CTkTextbox(self, width=1200, height=100, corner_radius=15)
        self.text_box.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    ## MOVER PUNTO CURVA DE MONTAJE INICIO ##
    
        # Variables para controlar el estado del clic
        self.dragging = False
        # Conectar los eventos de clic y movimiento del ratón
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)

    def on_click(self, event):
        if event.button == 1:  
            self.dragging = True

    def on_release(self, event):
        if event.button == 1:  
            self.dragging = False

    def on_move(self, event):
        if self.dragging and event.inaxes:
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
                if f_q <= 1:
                    self.q_new, self.ps_new, self.N_new, self.Ws_new = f_grafics.crear_nueva_curva(self.q, self.ps, self.N, self.Ws, f_q, f_q**2, f_q, f_q**3)  # Crear la nueva curva
                    self.q_new_c, self.ps_new_c = f_grafics.calcular_puntos_intermedios(self.q_new, self.ps_new) # Calcular los puntos intermedios
                    self.q_new_Nc, self.N_new_c = f_grafics.calcular_puntos_intermedios(self.q_new, self.N_new) # Calcular los puntos intermedios
                    self.q_new_Wc, self.Ws_new_c = f_grafics.calcular_puntos_intermedios(self.q_new, self.Ws_new) # Calcular los puntos intermedios
                    self.actualizar_texto()
                    if self.band_1 == 0:
                        self.curva_n_new, = self.ax.plot(self.q_new_c, self.ps_new_c, 'r-', linewidth=0.5)
                        self.curva_Wn_new, = self.ax_sub.plot(self.q_new_Wc, self.Ws_new_c, 'b-', linewidth=0.5)
                        self.band_1 = 1
                    self.curva_n_new.set_data(self.q_new_c, self.ps_new_c)
                    self.curva_Wn_new.set_data(self.q_new_Wc, self.Ws_new_c)
                    self.vertical_line.set_xdata([q, q])
                    self.vertical_line_sub.set_xdata([q, q])
                                
                    self.canvas.draw_idle() # Actualizar la gráfica     
                    
    def actualizar_texto(self):
        self.label_q.configure(text=f"Caudal [m^3/h]: {punto_curva[0]:.2f}")
        self.label_ps.configure(text=f"Presión disponible [Pa]: {punto_curva[1]:.2f}")
        self.N_corte = np.interp(punto_curva[0], self.q_new_Nc, self.N_new_c)
        self.label_n.configure(text=f"Revoluciones [rpm]: {self.N_corte:.2f}")
        print(int(punto_curva[0]/max(self.q_i)*100), int(punto_curva[1]/max(self.ps_i)*100))
        print(self.m_correc[int(punto_curva[0]/max(self.q_i)*100)][int(punto_curva[1]/max(self.ps_i)*100)])
        self.Ws_corte = np.interp(punto_curva[0], self.q_new_Nc, self.Ws_new_c) * self.m_correc[int(punto_curva[0]/max(self.q_i)*100)][int(punto_curva[1]/max(self.ps_i)*100)]
        self.label_Ws.configure(text=f"Consumo [W]: {self.Ws_corte:.2f}")

        self.W_mecanica = punto_curva[0] * punto_curva[1] / 3600
        self.label_W_mecanica.configure(text=f"Potencia Mecánica [W]: {self.W_mecanica:.2f}")
        self.rend_calculado = self.W_mecanica / self.Ws_corte * 100
        self.label_rend.configure(text=f"Rendimiento [%]: {self.rend_calculado:.2f}")

if __name__ == "__main__":
    app = Interfaz()
    app.mainloop()
## INTERFAZ ACABAR ##
