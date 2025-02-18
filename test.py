import matplotlib.pyplot as plt
import f_grafics


f_correc = f_grafics.interpolar_factor_correccion(f_grafics.factor_correccion_radial)
plt.figure(figsize=(8, 6))
plt.imshow(f_correc, cmap='viridis', origin='lower')
plt.colorbar(label='Factor de Corrección Radial')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Matriz Interpolada de Factor de Corrección Radial')
plt.show()