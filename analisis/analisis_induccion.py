from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


carpeta = Path(__file__).resolve().parent
figuras = carpeta.parent / "figuras"
plt.switch_backend("Agg")  # El script guarda las figuras como PDF.


def proporcional(x, a):
    return a * x


def recta(x, a, b):
    return a * x + b


fig_ajustes, ejes_ajustes = plt.subplots(1, 2, figsize=(7.1, 2.5))
fig_residuos, ejes_residuos = plt.subplots(1, 2, figsize=(7.1, 2.5))

for i, (archivo, titulo) in enumerate([
    ("picos_positivos.txt", r"Pico positivo $V_+$"),
    ("picos_negativos.txt", r"Magnitud del pico negativo $|V_-|$"),
]):
    angulo, voltaje = np.genfromtxt(carpeta / archivo, unpack=True)
    magnitud = np.abs(voltaje)

    # Promedio las dos pasadas de cada ángulo antes de ajustar.
    theta = np.unique(angulo)
    promedio = np.array([magnitud[angulo == valor].mean() for valor in theta])
    x = np.sqrt(np.sin(np.deg2rad(theta)))
    theta_curva = np.linspace(theta.min(), theta.max(), 200)
    x_curva = np.sqrt(np.sin(np.deg2rad(theta_curva)))

    ax = ejes_ajustes[i]
    ar = ejes_residuos[i]
    ax.scatter(angulo, magnitud, facecolors="none", edgecolors="0.55", s=12,
               label="Pasadas")
    ax.scatter(theta, promedio, color="0.15", s=13, zorder=5, label="Promedio")
    ar.axhline(0, color="0.55", linewidth=0.7)

    modelos = [
        ("Proporcional", r"$A\sqrt{\sin\theta}$",
         proporcional, x, x_curva, "-", "o", "#164673"),
        ("Con término constante", r"$A\sqrt{\sin\theta}+b$",
         recta, x, x_curva, "--", "s", "#9b3c24"),
        ("Lineal en el ángulo", r"$m\theta+c$",
         recta, theta, theta_curva, ":", "^", "#34694e"),
    ]
    print(f"\n{archivo}")
    for nombre, formula, modelo, predictor, curva, linea, marcador, color in modelos:
        parametros, _ = curve_fit(modelo, predictor, promedio)
        residuos = promedio - modelo(predictor, *parametros)
        rmse = np.sqrt(np.mean(residuos**2))
        valores = ", ".join(f"{p:.4f}" for p in parametros)
        print(f"{nombre:23s} | parámetros: {valores:18s} | RMSE: {rmse:.4f} mV")

        ax.plot(theta_curva, modelo(curva, *parametros), linea, color=color,
                linewidth=1.4, label=formula)
        ar.plot(theta, residuos, linestyle="none", marker=marcador, color=color,
                markerfacecolor="none", markersize=3.5)

    for eje in (ax, ar):
        eje.set(title=titulo, xlabel="Ángulo (°)")
        eje.grid(alpha=0.23)
        eje.set_axisbelow(True)

ejes_ajustes[0].set_ylabel("Magnitud (mV)")
ejes_residuos[0].set_ylabel("Residuo (mV)")
fig_ajustes.legend(*ejes_ajustes[0].get_legend_handles_labels(), loc="upper center",
                   ncol=5, fontsize=7, frameon=False)
fig_ajustes.tight_layout(rect=(0, 0, 1, 0.88))
fig_residuos.tight_layout()
fig_ajustes.savefig(figuras / "ajustes.pdf", bbox_inches="tight")
fig_residuos.savefig(figuras / "residuos.pdf", bbox_inches="tight")
