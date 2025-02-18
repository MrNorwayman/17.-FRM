import matplotlib.pyplot as plt
import numpy as np


def calcular_puntos_intermedios(x_i, y_i, num_puntos=10000):
    coeficientes = np.polyfit(x_i, y_i, 10)
    polinomio = np.poly1d(coeficientes)
    # Generar puntos intermedios
    x = np.linspace(min(x_i), max(x_i), num_puntos)
    y = polinomio(x)
    return x, y

def extraer_datos(puntos):
    q = []
    ps = []
    N = []
    Ws = []
    for q_p, ps_p, N_p, Ws_p in puntos:
        q.append(q_p)
        ps.append(ps_p)
        N.append(N_p)
        Ws.append(Ws_p)
    return q, ps, N, Ws

def calcular_curva_trabajo(punto_curva_trabajo):
    q_a = punto_curva_trabajo[0]
    ps_a = punto_curva_trabajo[1]
    q_trabajo = [0, 0.5*q_a, 0.7*q_a, 0.85*q_a, 1*q_a, 1.1*q_a, 1.2*q_a, 1.3*q_a, 1.4*q_a, 1.6*q_a, 2*q_a, 2.5*q_a, 4*q_a]
    ps_trabajo = [0, 0.25*ps_a, 0.49*ps_a, 0.7225*ps_a, 1*ps_a, 1.21*ps_a, 1.44*ps_a, 1.69*ps_a, 1.96*ps_a, 2.56*ps_a, 4*ps_a, 6.25*ps_a, 16*ps_a] 
    return calcular_puntos_intermedios(q_trabajo, ps_trabajo)

def find_intersection(x1, y1, x2, y2):
    # Interpolar las curvas
    curve1 = np.interp(x1, x1, y1)
    curve2 = np.interp(x1, x2, y2)
    
    # Encontrar el punto de intersección
    idx = np.argwhere(np.diff(np.sign(curve1 - curve2)) != 0).reshape(-1) + 0
    intersections = []
    for i in idx:
        x_inter = (x1[i] + x1[i+1]) / 2
        y_inter = (curve1[i] + curve1[i+1]) / 2
        intersections.append([x_inter, y_inter])
    
    return intersections

def crear_nueva_curva(q_i, ps_i, N_i, Ws_i, f_q, f_ps, f_N, f_Ws):
    q_new = []
    ps_new = []
    N_new = []
    Ws_new = []
    for x in q_i:
        q_new.append(x*f_q)
    for x in ps_i:
        ps_new.append(x*f_ps)
    for x in N_i:
        N_new.append(x*f_N)
    for x in Ws_i:
        Ws_new.append(x*f_Ws)
    return q_new, ps_new, N_new, Ws_new
