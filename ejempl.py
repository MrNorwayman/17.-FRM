from tkinter import filedialog, messagebox
import customtkinter as ctk
import openpyxl as oxl
import warnings

############################################################################################################
class Informacion(ctk.CTkToplevel):
    #Ventana de informacion
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("100x850")
        self.minsize(900, 850)

        #Texto de informacion
        with open("Ayuda.txt") as f:
            lineas = f.read().strip()

        self.label = ctk.CTkLabel(self, text=lineas)
        self.label.pack(padx=20, pady=20)

class Ventana_Principal(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el tema y la apariencia de customtkinter
        ctk.set_appearance_mode("dark")  # Opciones: "light", "dark"
        ctk.set_default_color_theme("blue")  # Cambia el tema de color

        # Crear la ventana principal
        self.title("Conversor de paremetros Cabling a EXCEL")
        self.geometry("1200x500")
        self.minsize(700, 300)

        row_texto = 5

        ### CREACION DE FRAMES
        ### ---------------------------------------------------------###
        self.texto_de_entrada = ctk.CTkTextbox(self, font=("Helvetica", 15))
        self.texto_de_entrada.grid(row=row_texto, column=0, columnspan=4, sticky="nsew", padx=10, pady=0)#Cuadro de texto

        self.f_xml = ctk.CTkFrame(self)
        self.f_xml.grid(row=row_texto, column=4, columnspan=3, sticky= "nesw", padx=10, pady=0)#Frame para arrastrar el archivo .XML
        self.t_xml = ctk.CTkLabel(self.f_xml, text="Archivo .XML", font=("Helvetia", 15))
        self.t_xml.grid(row=0, column=0, padx = 10, pady = 10, sticky="new")
        self.b_xml = ctk.CTkButton(self.f_xml, text="Seleccionar Archivo", command=self.buscar_archivo)
        self.b_xml.grid(row=1, column=0, padx=20, pady=20, sticky="wes")


        ### CONFIGURAR PROPORCIONES DE FILAS
        self.grid_rowconfigure(row_texto, weight=1)
        self.f_xml.grid_rowconfigure(1, weight=1)

        # Configurar la columna del grid
        self.f_xml.grid_columnconfigure(0, weight=1) 
        for i in range(6):
            self.grid_columnconfigure(i, weight=1)
        ### ---------------------------------------------------------###

        ### CREACION DE CONFIGURACIONES
        ### ---------------------------------------------------------###
        #Nombre de mazo
        self.e_n_mazo = ctk.CTkEntry(self, placeholder_text="Nombre del mazo...")
        self.e_n_mazo.grid(row=1, column=0, padx=30, pady=20, sticky="wse")

        #Medida de redondeo
        self.menu_redondeo = ctk.StringVar(value="Aumento cable de 50mm")
        combobox = ctk.CTkOptionMenu(self, values=["Aumento cable de 150mm",
                                                    "Aumento cable de 100mm",
                                                    "Aumento cable de 75mm",
                                                    "Aumento cable de 50mm",
                                                    "Aumento cable de 25mm",
                                                    "Aumento cable de 10mm"],
                                                    variable=self.menu_redondeo)
        combobox.grid(row=1, column=4, columnspan=2, padx=30, pady=20, sticky="we")
        ### ---------------------------------------------------------###

        ### CREACION DE BOTONES EN F_BOTONES
        ### ---------------------------------------------------------###
        # Crear los botones
        self.b_guardar = ctk.CTkButton(self, text="Guardar en Excel", command=self.guardar_como_excel)
        self.b_cerrar = ctk.CTkButton(self, text="Cerrar", command=self.cerrar_ventana)
        self.b_ayuda = ctk.CTkButton(self, text="Ayuda", command=self.open_toplevel)

        # Usar grid para posicionar los botones
        self.b_guardar.grid(row=row_texto+1, column=0, columnspan=2, padx=30, pady=20, sticky="we")
        self.b_ayuda.grid(row=row_texto+1, column=2, columnspan=2, padx=30, pady=20, sticky="we")
        self.b_cerrar.grid(row=row_texto+1, column=4, columnspan=2, padx=30, pady=20, sticky="we")
        ### ---------------------------------------------------------###

        self.toplevel_window = None

    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Informacion(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

    ######################################################################################################
    def cerrar_ventana(self):
        quit()

    def guardar_como_excel(self):
        self.redondeo = 50
        try:
            n_mazo = self.e_n_mazo.get()
            if n_mazo == "":
                messagebox.showwarning("Advertencia", "El nombre del mazo está vacio.")
                return
            
            self.redondeo = int(self.menu_redondeo.get()[16:-2])

            texto = self.texto_de_entrada.get("0.0", ctk.END).strip()
            if not texto:
                messagebox.showwarning("Advertencia", "El área de texto está vacía.")
                return
            
            if self.t_xml.cget("text") == "Archivo .XML":
                messagebox.showwarning("Advertencia", "No se ha seleccionado archivo XML")
                return
            
            lineas = texto.split("\n")

            datos = []

            self.spools = self.leer_spools()
            self.cables = self.leer_cables()

            self.cables_spools = self.relacionar_cable_spool()

            for linea in lineas:
                if "NOMBRE DEL MAZO" in linea or "Nombre cable" in linea or "NETWORK" in linea:
                    continue

                partes = linea.split()
                if len(partes) < 3:
                    continue  # Saltar líneas que no tengan suficientes datos

                # Se asume que el formato es correcto
                for i, cable in enumerate(self.cables_spools):
                    if partes[0] == cable[0]:
                        color_cnd = cable[1]
                        font = cable[2]
                long = partes[2]

                #Convertir la longitud en entero y añadir un poco de longitud
                long = int(float(long) / 10) * 10 + self.redondeo
                long = str(long)
                # Unimos el resto de las partes para formar "Desde - Hasta"
                desde = " ".join(partes[3:7])
                hasta = " ".join(partes[-4:])
                # Intentamos dividir usando "   "

                datos.append([n_mazo, "","1", "1", "", color_cnd, long, "", "", "", "", font, desde, "25", "", "NORMAL", "FORWARDS", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", hasta, "25", "", "NORMAL", "BACKWARDS", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "1", "", "", "", "", "", "PUNTERA 1.5", "", "", "", "", "", "", "", "", "", "PUNTERA 1.5"])

            if not datos:
                messagebox.showwarning("Advertencia", "No se encontraron datos válidos para guardar.")
                return

            warnings.simplefilter(action='ignore', category=UserWarning)
            wb = oxl.load_workbook("Plantilla_Excel.xlsx")

            excel = wb.active

            for i in range(len(datos)):
                for index, dato in enumerate(datos[i]):
                    excel.cell(row=i+4, column=index+1, value = str(dato))

            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

            if file_path:
                wb.save(file_path)

            messagebox.showinfo("Estado", f"Se ha guardado el Excel en {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def leer_spools(self):
        spools = []
        spool_number = 1
        with open(self.xml_path) as xml:
            for linea in xml:
                if "<SPOOL" in linea:
                    spool = []
                    datos_linea = linea.split()
                    spool.append(spool_number)
                    spool.append(datos_linea[1][6:-1])


                    match spool[1]:
                        case "1X1_5_NEGRO":
                            spool[1] = "NEGRO 1.5"
                            font = "FUENTE B1.5"

                        case "1X1_5_GRIS":
                            spool[1] = "GRIS 1.5"
                            font = "FUENTE N1.5"

                        case "1X1_5_MARRON":
                            spool[1] = "MARRON 1.5"
                            font = "FUENTE N1.5"

                        case _:
                            font = ""

                    spool.append(font)
                    spools.append(spool)
                    spool_number = spool_number + 1
        return spools

    def leer_cables(self):
        cables = []
        with open(self.xml_path) as xml:
            for linea in xml:
                if "<CONNECTION" in linea:
                    cable = []
                    datos_linea = linea.split()
                    cable.append(datos_linea[1][6:-1])
                    cable.append(datos_linea[3][11:-1])
                    cable.append("")
                    cables.append(cable)
        return cables

    def relacionar_cable_spool(self):
        cables_spools = []
        for i, cable in enumerate(self.cables):
            for x, spool in enumerate(self.spools):
                if cable[1] == str(spool[0]):
                    cable[1] = spool[1]
                    cable[2] = spool[2]
                    cables_spools.append(cable)

        return cables_spools            

    def buscar_archivo(self):
        self.xml_path = filedialog.askopenfilename()
        if self.xml_path:
            if self.xml_path[-4::] == (".xml" or ".XML"):
                archivo = self.xml_path.split("/")
                self.t_xml.configure(text=f"Archivo seleccionado:\n {archivo[-1]}")
            else:
                messagebox.showwarning("Advertencia", "Seleccione un formato compatible")
##########################################################################################################

if __name__ == "__main__":
    app = Ventana_Principal()
    app.mainloop()
