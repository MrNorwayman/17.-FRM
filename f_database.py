import ast

def read_text_file():
    with open('database.txt', 'r') as file:
        content = file.readlines()
    return content

def copia_database():
    content = read_text_file()
    matriz_vent =[] #Crea la matriz de ventiladores
    for line in content:
        if line[0:4] == 'VENT':
            vent = line.split(';')
            vent[3] = ast.literal_eval(vent[3])
            matriz_vent.append(vent[1::])
    return matriz_vent

class EventoSimulado:
    def __init__(self, xdata, ydata):
        self.xdata = xdata
        self.ydata = ydata
        self.button = 1
        self.dragging = True
        self.inaxes = True