import numpy as np
from scipy.interpolate import RegularGridInterpolator

# LAS MATRICES ESTAN TODAS REFLEJADAS !!!!!! añadir la funcion rotar
factor_correccion_radial= np.array([[100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100]
                                    ])
factor_correccion_radial = np.rot90(factor_correccion_radial, 3)

factor_correccion_axial = np.array([[100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100],
                                    [100,   100,    100,    100,    100, 100, 100, 100, 100, 100]
                                    ])
factor_correccion_axial = np.rot90(factor_correccion_axial, 3)

def interpolar_factor_correccion(matriz, num_puntos=100):
    # Crear los puntos de la cuadrícula original
    x = np.arange(0, matriz.shape[1])
    y = np.arange(0, matriz.shape[0])
    # Crear la función de interpolación
    interpolador = RegularGridInterpolator((y, x), matriz, method='linear')
    # Crear los nuevos puntos de la cuadrícula para la interpolación
    x_new = np.linspace(0, matriz.shape[1] - 1, num_puntos)
    y_new = np.linspace(0, matriz.shape[0] - 1, num_puntos)
    x_new, y_new = np.meshgrid(x_new, y_new)
    puntos_nuevos = np.array([y_new.flatten(), x_new.flatten()]).T
    # Interpolar la matriz
    matriz_interpolada = interpolador(puntos_nuevos).reshape(num_puntos, num_puntos) / 100
    return matriz_interpolada


def calcular_puntos_intermedios(x_i, y_i, num_puntos=5000, orden=5):
    coeficientes = np.polyfit(x_i, y_i, orden)
    polinomio = np.poly1d(coeficientes)
    # Generar puntos intermedios
    x = np.linspace(np.min(x_i), np.max(x_i), num_puntos)
    y = polinomio(x)
    return x, y

def extraer_datos(puntos):
    puntos = np.array(puntos)
    q, ps, N, Ws = puntos.T
    return q, ps, N, Ws

def calcular_curva_trabajo(punto_curva_trabajo):
    q_a = punto_curva_trabajo[0]
    ps_a = punto_curva_trabajo[1]
    q_trabajo = np.array([0, 0.5*q_a, 0.7*q_a, 0.85*q_a, 1*q_a, 1.1*q_a, 1.2*q_a, 1.3*q_a, 1.4*q_a, 1.6*q_a, 2*q_a, 2.5*q_a, 4*q_a])
    ps_trabajo = np.array([0, 0.25*ps_a, 0.49*ps_a, 0.7225*ps_a, 1*ps_a, 1.21*ps_a, 1.44*ps_a, 1.69*ps_a, 1.96*ps_a, 2.56*ps_a, 4*ps_a, 6.25*ps_a, 16*ps_a])
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
    q_new = q_i * f_q
    ps_new = ps_i * f_ps
    N_new = N_i * f_N
    Ws_new = Ws_i * f_Ws
    return q_new.tolist(), ps_new.tolist(), N_new.tolist(), Ws_new.tolist()

def crear_curva_consumo_disponible(q, ps, Ws):
    consumo_disponible=q*ps/3600
    max_consumo_disponible=np.max(consumo_disponible)

    rendimiento=consumo_disponible/Ws*100
    max_rendimiento=np.max(rendimiento)
    return consumo_disponible.tolist(), rendimiento.tolist(), max_rendimiento, max_consumo_disponible