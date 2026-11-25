import numpy as np
import matplotlib.pyplot as plt
import os

print(os.getcwd())
angulo = 15
if angulo <= 9:
    sufijo = ".1"
else:
    sufijo = ""

datos1 = np.genfromtxt(
    f"datos/grado {angulo}/Rep1{sufijo} {angulo} grados0.csv",
    delimiter=",",
    skip_header=1,
    skip_footer=1
)

datos2 = np.genfromtxt(
    f"datos/grado {angulo}/Rep2{sufijo} {angulo} grados0.csv",
    delimiter=",",
    skip_header=1,
    skip_footer=1
)

t1 = datos1[:, 0]
t2 = datos2[:, 0]

V1 = datos1[:, 2] * 1000
V2 = datos2[:, 2] * 1000

Vmax1 = np.max(V1)
Vmax2 = np.max(V2)

Vmin1 = np.min(V1)
Vmin2 = np.min(V2)

Vmax_prom = (Vmax1 + Vmax2) / 2
Vmin_prom = (Vmin1 + Vmin2) / 2

print("Ángulo:", angulo)

print("\nRepetición 1")
print(f"Máximo: {Vmax1:.6f} mV")
print(f"Mínimo: {Vmin1:.6f} mV")

print("\nRepetición 2")
print(f"Máximo: {Vmax2:.6f} mV")
print(f"Mínimo: {Vmin2:.6f} mV")

print("\nPromedios")
print(f"Máximo: {Vmax_prom:.6f} mV")
print(f"Mínimo: {Vmin_prom:.6f} mV")

print("\nFila para TXT positivo:")
print(f"{angulo:<4} {Vmax1:12.6f} {Vmax2:12.6f}")

print("\nFila para TXT negativo:")
print(f"{angulo:<4} {Vmin1:12.6f} {Vmin2:12.6f}")


plt.plot(t1, V1, label="Repetición 1")
plt.plot(t2, V2, label="Repetición 2")

plt.xlabel("Tiempo (s)")
plt.ylabel("Voltaje (mV)")
plt.title(f"Voltaje inducido a {angulo}°")

plt.legend()
plt.grid()
#plt.show()