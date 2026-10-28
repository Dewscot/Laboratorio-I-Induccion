"""Inducción: carrito ENTRE dos bobinas de Helmholtz, riel transversal a su eje.

Montaje (vista superior): dos bobinas fijas a los lados del riel. Sus ejes
coinciden en la dirección transversal del riel. La espira captadora es plana,
está fija al carrito, contenida en el plano longitudinal vertical del riel,
y tiene su normal orientada sobre el eje común de Helmholtz.

Campo magnético: integración numérica de Biot-Savart para dos anillos
circulares con corrientes iguales, evaluada en el plano medio entre ellos.
Flujo: integral del campo normal sobre una espira rectangular de área finita.
No se utiliza el modelo anterior de campo uniforme con bordes abruptos.

Hipótesis importantes: las bobinas permanecen fijas, el riel pivota alrededor
del centro del sistema, el carrito sigue el plano medio de las bobinas, las
vueltas captadoras son equivalentes, y se omiten rozamiento, autoinducción,
frenado magnético y fuerzas de cables. Estos datos SON SIMULADOS.

Ejecución:
    python simulacion_induccion_helmholtz.py
    python simulacion_induccion_helmholtz.py --exportar --angulo 15 --vueltas 40
    python simulacion_induccion_helmholtz.py --comparar

Requiere únicamente NumPy y Matplotlib.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict, replace
from functools import lru_cache
import json
from pathlib import Path
import time

import numpy as np

G = 9.81
LARGO_RIEL = 1.50
CENTRO_CAMPO = 0.75
SALIDA = Path(__file__).resolve().parent / "resultados_simulacion_helmholtz"


@dataclass(frozen=True)
class Parametros:
    angulo: float = 10.0           # inclinación respecto a la horizontal [°]
    campo_mT: float = 1.0          # campo central B0, EJEMPLO, NO medido [mT]
    radio_cm: float = 15.0         # radio de CADA bobina de Helmholtz [cm]
    separacion_cm: float = 15.0    # entre planos de bobinas [cm]; Helmholtz: D=R
    vueltas: int = 10             # vueltas de la ESPIRA CAPTADORA
    ancho_cm: float = 10.0        # tamaño captador en plano, transversal a riel [cm]
    largo_cm: float = 10.0        # tamaño captador paralelo al riel [cm]
    resistencia: float = 1.0      # ohmios, espira y conexiones
    carga: float = 1000.0         # ohmios, resistencia donde se mide V
    sonda: int = 1               # atenuación ×1 o ×10 del osciloscopio

    def validar(self):
        if not all(np.isfinite(float(v)) for v in asdict(self).values()):
            raise ValueError("Todos los parámetros deben ser finitos.")
        if not (0 <= self.angulo <= 60):
            raise ValueError("Inclinación: de 0° a 60°.")
        if self.campo_mT < 0 or self.resistencia < 0 or self.carga <= 0:
            raise ValueError("Campo y resistencia propia >= 0; carga > 0.")
        if not (2 <= self.radio_cm <= 80 and 2 <= self.separacion_cm <= 100):
            raise ValueError("Radio: 2–80 cm; separación: 2–100 cm.")
        if self.vueltas < 1 or self.vueltas != int(self.vueltas):
            raise ValueError("Las vueltas deben ser un entero positivo.")
        if min(self.ancho_cm, self.largo_cm) <= 0 or max(self.ancho_cm, self.largo_cm) > 80:
            raise ValueError("Dimensiones de la espira: entre 0 y 80 cm.")
        if self.sonda not in (1, 10):
            raise ValueError("Sonda: ×1 o ×10.")


@lru_cache(maxsize=32)
def _perfil_radial_normalizado(radio_cm: float, separacion_cm: float):
    """B normal/B(0) en el PLANO MEDIO, según Biot-Savart para dos aros.

    El eje común de los aros es la dirección horizontal transversal al riel.
    La distancia radial rho se mide desde ese eje, dentro del plano del riel.
    Para D=R se reproduce el campo central de un par de Helmholtz.
    La aproximación por aros omite espesor real y soporte de las bobinas.
    """
    R = radio_cm / 100
    q = separacion_cm / (2 * radio_cm)
    rho = np.linspace(0, 2.05, 4101)
    u = (rho / R)[:, None]
    # Integración por regla del punto medio sobre el ángulo del conductor.
    phi = (np.arange(192) + 0.5) * (2 * np.pi / 192)
    c = np.cos(phi)[None, :]
    denom = 1 + u*u + q*q - 2*u*c
    ratio = (1 + q*q)**1.5 * np.mean((1 - u*c) / denom**1.5, axis=1)
    ratio[0] = 1.0
    rho.setflags(write=False)
    ratio.setflags(write=False)
    return rho, ratio


@lru_cache(maxsize=64)
def _flujo_espira_tabla(radio_cm: float, separacion_cm: float,
                         ancho_cm: float, largo_cm: float, campo_mT: float):
    """Integra B·dS en una espira rectangular del plano medio entre bobinas.

    Cuadratura de Gauss sobre el área. La espira rota DENTRO del plano medio
    cuando el riel se inclina, por lo que su normal sigue alineada con B.
    """
    s = np.linspace(-0.20, LARGO_RIEL + 0.20, 3801)
    rho_grid, perfil = _perfil_radial_normalizado(radio_cm, separacion_cm)
    nodos, pesos = np.polynomial.legendre.leggauss(7)
    L = largo_cm / 100
    W = ancho_cm / 100
    # u: dirección del movimiento; w: eje en el plano, perpendicular al riel.
    u = nodos * (L / 2)
    w = nodos * (W / 2)
    rho = np.sqrt((s[:, None, None] - CENTRO_CAMPO + u[None, :, None])**2
                  + w[None, None, :]**2)
    campo_norm = np.interp(rho.ravel(), rho_grid, perfil).reshape(rho.shape)
    pesos_area = np.outer(pesos, pesos) / 4
    phi = (campo_mT * 1e-3) * (L * W) * np.einsum("sij,ij->s", campo_norm, pesos_area)
    derivada = np.gradient(phi, s, edge_order=2)
    s.setflags(write=False)
    phi.setflags(write=False)
    derivada.setflags(write=False)
    return s, phi, derivada


def campo_en_riel(s, p: Parametros):
    """Componente transversal B (tesla) en el plano medio entre bobinas."""
    rr, b = _perfil_radial_normalizado(p.radio_cm, p.separacion_cm)
    return p.campo_mT * 1e-3 * np.interp(np.abs(np.asarray(s) - CENTRO_CAMPO), rr, b)


def flujo_y_derivada(posicion, p: Parametros):
    """Flujo magnético por vuelta y dPhi/ds, ambas en SI."""
    s, phi, der = _flujo_espira_tabla(p.radio_cm, p.separacion_cm,
                                      p.ancho_cm, p.largo_cm, p.campo_mT)
    x = np.asarray(posicion)
    return np.interp(x, s, phi), np.interp(x, s, der)


def tiempo_en_posicion(s, aceleracion):
    return np.sqrt(2 * np.maximum(s, 0) / aceleracion) if aceleracion > 0 else np.zeros_like(s)


def simular(p: Parametros = Parametros(), muestras: int = 3001):
    p.validar()
    if muestras < 101:
        raise ValueError("Se necesitan al menos 101 muestras.")
    a = G * np.sin(np.deg2rad(p.angulo))
    tiempo_final = np.sqrt(2 * LARGO_RIEL / a) if a else 3.0
    t = np.linspace(0, tiempo_final, muestras)
    s = 0.5 * a * t*t
    v = a * t
    phi, dphids = flujo_y_derivada(s, p)
    fem = -p.vueltas * dphids * v
    # Entrada analógica: 1 MΩ con conexión directa; ×10 aprox. 10 MΩ.
    r_entrada = 1e6 * p.sonda
    r_efectiva = 1 / (1 / p.carga + 1 / r_entrada)
    corriente = fem / (p.resistencia + r_efectiva)
    voltaje = corriente * r_efectiva
    al_bnc = voltaje / p.sonda

    # Máximos con su signo a cada lado del centro, NO bordes artificiales.
    def pico_lado(mascara):
        indices = np.flatnonzero(mascara)
        idx = indices[np.argmax(np.abs(voltaje[indices]))]
        return float(voltaje[idx]), float(t[idx]), float(s[idx])

    p_ent = pico_lado(s < CENTRO_CAMPO) if a else (0., 0., 0.)
    p_sal = pico_lado(s >= CENTRO_CAMPO) if a else (0., 0., 0.)
    distancia_referencia = min(1.8 * p.radio_cm / 100, CENTRO_CAMPO * 0.9)
    ventana = float((tiempo_en_posicion(CENTRO_CAMPO + distancia_referencia, a)
                     - tiempo_en_posicion(CENTRO_CAMPO - distancia_referencia, a))) if a else 0.0
    pico = float(np.max(np.abs(voltaje)))
    return {
        "t": t, "s": s, "v": v, "flujo": phi, "dflujo_ds": dphids,
        "campo": campo_en_riel(s, p), "fem": fem, "voltaje": voltaje,
        "corriente": corriente, "entrada_BNC": al_bnc,
        "fem_pico": float(np.max(np.abs(fem))),
        "voltaje_pico": pico, "voltaje_pp": float(np.ptp(voltaje)),
        "rapidez_centro": float(np.sqrt(2*a*CENTRO_CAMPO)),
        "pico_entrada": p_ent, "pico_salida": p_sal,
        "div_normal": pico / p.sonda / .005,
        "div_expandido": pico / p.sonda / .001,
        "ventana_senal": ventana,
    }


def base_tiempo(d):
    if d["ventana_senal"] <= 0:
        return "sin paso (θ = 0°)"
    escalas = np.array([m*10.**e for e in range(-7, 0) for m in (1, 2, 5)])
    escalas = escalas[(escalas >= 2e-7) & (escalas <= .1)]
    opciones = escalas[escalas >= d["ventana_senal"] / 8]
    return f"{opciones[0]*1000:g} ms/div" if opciones.size else "100 ms/div; revisar por separado"


def resumen(p, d):
    entrada, t_ent, _ = d["pico_entrada"]
    salida, t_sal, _ = d["pico_salida"]
    if d["fem_pico"] == 0:
        estado = "Sin fem para estos parámetros."
    elif d["div_expandido"] < 1:
        estado = "Señal < 1 div. con Y×5; verificar sensibilidad y ruido."
    else:
        estado = "Señal ≥ 1 div. con Y×5; comprobar ruido y disparo."
    return (f"Campo central B₀ = {p.campo_mT:g} mT (SUPUESTO); "
            f"R = {p.radio_cm:g} cm, D = {p.separacion_cm:g} cm\n"
            f"Rapidez al centro: {d['rapidez_centro']:.2f} m/s | "
            f"fem pico: {d['fem_pico']*1000:.3f} mV\n"
            f"Voltaje sobre carga: {d['voltaje_pico']*1000:.3f} mV pico; "
            f"{d['voltaje_pp']*1000:.3f} mV p-p\n"
            f"Lado llegada: {entrada*1000:+.3f} mV a {t_ent:.3f} s; "
            f"lado salida: {salida*1000:+.3f} mV a {t_sal:.3f} s\n"
            f"Hameg ×{p.sonda}: {d['div_normal']:.2f} div (5 mV/div), "
            f"{d['div_expandido']:.2f} div (Y×5). Base orientativa: {base_tiempo(d)}\n"
            f"{estado} Las bobinas NO forman un campo de bordes abruptos.")


def graficas(ax_pos, ax_volt, p, d):
    for ax in (ax_pos, ax_volt):
        ax.clear()
        ax.grid(alpha=.22)
        ax.set_xlabel("Tiempo (s)")
        ax.set_xlim(0, d["t"][-1])
    ax_pos.plot(d["t"], d["s"], color="#27638c", lw=2)
    ax_pos.axhline(CENTRO_CAMPO, color="#7b858e", ls="--", lw=1, label="Centro de bobinas")
    ax_pos.set(title="Movimiento por el riel", ylabel="Posición s (m)", ylim=(0, LARGO_RIEL*1.05))
    ax_pos.legend(fontsize=8, loc="upper left")
    ax_volt.plot(d["t"], d["fem"]*1000, color="#b95e29", lw=2.2, label="Fem")
    ax_volt.plot(d["t"], d["voltaje"]*1000, color="#188277", lw=1.6, ls="--", label="Voltaje en carga")
    ax_volt.axhline(0, color="#94a3b8", lw=.7)
    ymax = max(.002, d["fem_pico"]*1000*1.15)
    ax_volt.set(title="Inducción (campo suave)", ylabel="Tensión (mV)", ylim=(-ymax, ymax))
    ax_volt.legend(fontsize=8, loc="upper left")


def grafico_perfil(ax, p):
    ax.clear()
    posiciones = np.linspace(0, LARGO_RIEL, 600)
    B = campo_en_riel(posiciones, p)
    ax.plot(posiciones, B*1000, color="#7854a3", lw=2)
    ax.axvline(CENTRO_CAMPO, color="#7b858e", ls="--", lw=1)
    ax.axhline(0, color="#94a3b8", lw=.8)
    ax.set(title="Campo transversal en el riel", xlabel="Posición s (m)",
           ylabel="$B_\\perp$ (mT)", xlim=(0, LARGO_RIEL))
    ax.grid(alpha=.22)


def comparar_angulos(p, carpeta=None):
    """Compara U_pk para varias inclinaciones, con la misma geometría y B."""
    import matplotlib.pyplot as plt
    angulos = np.array([3., 5., 8., 10., 15., 20., 25., 30.])
    picos = np.array([simular(replace(p, angulo=float(th)), 1901)["voltaje_pico"]
                      for th in angulos]) * 1000
    x = np.sqrt(np.sin(np.deg2rad(angulos)))
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.plot(x, picos, "o-", lw=1.6, label="Simulación: campo de bobinas circulares")
    if x[-1] > 0:
        ax.plot(x, picos[-1]*x/x[-1], "--", label=r"Referencia $U_{pk}\propto\sqrt{\sin\theta}$")
    ax.set(xlabel=r"$\sqrt{\sin\theta}$", ylabel="Voltaje pico sobre la carga (mV)",
           title="Variar θ manteniendo alineación y campo")
    ax.grid(alpha=.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    if carpeta is not None:
        carpeta = Path(carpeta)
        carpeta.mkdir(parents=True, exist_ok=True)
        fig.savefig(carpeta / "comparacion_angulos.png", dpi=170)
        np.savetxt(carpeta / "comparacion_angulos.csv", np.column_stack((angulos, x, picos)),
                   delimiter=",", header="angulo_grados,raiz_seno_angulo,voltaje_pico_mV", comments="")
    return fig, angulos, picos


def exportar(p, carpeta=SALIDA):
    import matplotlib.pyplot as plt
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    d = simular(p)
    nombre = f"helmholtz_transversal_{p.angulo:g}grados_{p.vueltas}vueltas"
    claves = ("t", "s", "v", "campo", "flujo", "dflujo_ds", "fem", "voltaje", "corriente")
    np.savetxt(carpeta / f"{nombre}.csv", np.column_stack([d[k] for k in claves]),
               delimiter=",", header="t_s,s_m,v_m_s,B_transversal_T,flujo_por_vuelta_Wb,dPhi_ds_Wb_m,fem_V,voltaje_carga_V,corriente_A",
               comments="")
    (carpeta / f"{nombre}.json").write_text(json.dumps({
        "origen": "SIMULACIÓN, no resultados medidos",
        "geometria": "Helmholtz a lados del riel; eje de bobinas perpendicular al riel; espira vertical longitudinal alineada",
        "modelo": "Campo de dos anillos por Biot-Savart en plano medio; flujo integrado sobre area captadora finita",
        "hipotesis": ["Riel pivota alrededor del centro de bobinas y mantiene plano medio", "Espira sin nucleo y centrada", "Movimiento sin perdidas ni autoinduccion"],
        "parametros": asdict(p), "longitud_riel_m": LARGO_RIEL,
        "campo_central_mT": p.campo_mT, "resumen": resumen(p, d),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.9))
    grafico_perfil(axes[0], p)
    graficas(axes[1], axes[2], p, d)
    fig.suptitle(f"Helmholtz transversal · θ = {p.angulo:g}° · {p.vueltas} vueltas captadoras")
    fig.text(.04, .016, "Simulación ideal, no medición. Campo calculado en plano medio; bobinas circulares delgadas.", fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, .94))
    destino = carpeta / f"{nombre}.png"
    fig.savefig(destino, dpi=180)
    plt.close(fig)
    return destino


class Aplicacion:
    def __init__(self, p=Parametros()):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Ellipse
        from matplotlib.widgets import Button, RadioButtons, Slider, TextBox

        self.p = p
        self.fig = plt.figure(figsize=(15, 9.2), facecolor="#f7f8fa")
        self.fig.canvas.manager.set_window_title("Inducción · Helmholtz transversal · Hameg HM203-7")
        self.fig.text(.055, .954, "Espira móvil entre dos bobinas de Helmholtz", size=18, weight="bold")
        self.fig.text(.055, .921, "Nuevo montaje: bobinas a ambos lados del riel; campo transversal. Riel 1,50 m.", size=10)
        self.ax_escena = self.fig.add_axes([.055, .66, .36, .235])
        self.ax_perfil = self.fig.add_axes([.468, .667, .22, .215])
        self.ax_pos = self.fig.add_axes([.065, .365, .272, .218])
        self.ax_fem = self.fig.add_axes([.411, .365, .277, .218])
        self.texto = self.fig.text(.055, .293, "", va="top", fontsize=9.1, linespacing=1.35)
        self.fig.text(.72, .915, "Parámetros (valores supuestos)", fontsize=12, weight="bold")
        self.fig.text(.72, .887, "Editar y pulsar Aplicar. Unidades indicadas.", fontsize=8.4)
        campos = [
            ("campo_mT", "Campo central B₀ (mT)"),
            ("radio_cm", "Radio bobinas R (cm)"),
            ("separacion_cm", "Separación D (cm)"),
            ("vueltas", "Vueltas captadoras"),
            ("ancho_cm", "Ancho espira (cm)"),
            ("largo_cm", "Largo espira (cm)"),
            ("resistencia", "Resistencia espira (Ω)"),
            ("carga", "Resistencia carga (Ω)"),
        ]
        self.entradas = {}
        for i, (key, desc) in enumerate(campos):
            yy = .841 - i*.046
            self.fig.text(.72, yy+.005, desc, fontsize=8.7)
            self.entradas[key] = TextBox(self.fig.add_axes([.903, yy, .075, .031]), "", initial=f"{getattr(p, key):g}")
        self.fig.text(.72, .458, "Helmholtz ideal: D = R. Espira en plano vertical\nlongitudinal, con su normal transversal al riel.", fontsize=8.1)
        self.radio = RadioButtons(self.fig.add_axes([.72, .354, .25, .071]),
                                  ["Sonda ×1", "Sonda ×10"], active=0 if p.sonda == 1 else 1)
        self.btn_aplicar = Button(self.fig.add_axes([.72, .306, .12, .037]), "Aplicar")
        self.btn_reset = Button(self.fig.add_axes([.855, .306, .12, .037]), "Restablecer")
        self.btn_aplicar.on_clicked(self.aplicar_campos)
        self.btn_reset.on_clicked(self.reiniciar)
        self.fig.text(.72, .285,
                      "Hameg HM203-7: 5 mV/div; 1 mV/div con Y×5.\n"
                      "Entrada directa 1 MΩ (sonda ×10: aproximación\n"
                      "10 MΩ). DC y mando CAL. Captura analógica:\n"
                      "repetir o filmar. La detectabilidad requiere pruebas.",
                      fontsize=8.5, va="top", linespacing=1.5)
        self.angulo = Slider(self.fig.add_axes([.15, .092, .46, .025]), "Inclinación θ",
                             0, 60, valinit=p.angulo, valstep=.1, valfmt="%1.1f°")
        self.angulo.on_changed(self.cambiar_angulo)
        self.btn_anim = Button(self.fig.add_axes([.72, .103, .113, .038]), "Animar")
        self.btn_save = Button(self.fig.add_axes([.848, .103, .13, .038]), "PNG + CSV")
        self.btn_compare = Button(self.fig.add_axes([.72, .15, .258, .037]), "Comparar varios ángulos")
        self.btn_anim.on_clicked(self.alternar_animacion)
        self.btn_save.on_clicked(self.guardar_resultados)
        self.btn_compare.on_clicked(self.comparar)
        self.estado = self.fig.text(.055, .049, "", fontsize=8.9, color="#8a3e16")
        self.fig.text(.055, .019,
                      "Modelo: Biot-Savart en plano medio; espira rectangular centrada. Bobinas fijas y riel girando SOBRE el centro; sin pérdidas.",
                      fontsize=8.1)
        self.timer = self.fig.canvas.new_timer(interval=40)
        self.timer.add_callback(self.paso_animacion)
        self.en_marcha = False
        self.actualizar()

    def actualizar(self):
        from matplotlib.patches import Ellipse
        self.timer.stop()
        self.en_marcha = False
        self.btn_anim.label.set_text("Animar")
        self.d = simular(self.p)
        graficas(self.ax_pos, self.ax_fem, self.p, self.d)
        grafico_perfil(self.ax_perfil, self.p)
        self.texto.set_text(resumen(self.p, self.d))
        self.cursores = [a.axvline(0, lw=1, color="#627384", alpha=.5) for a in (self.ax_pos, self.ax_fem)]
        self.marker_campo, = self.ax_perfil.plot([], [], "o", color="#c05e24", markersize=5)
        self.ax_escena.clear()
        ax = self.ax_escena
        R = self.p.radio_cm/100
        D = self.p.separacion_cm/100
        ancho = max(.35, R*1.6, D*.85)
        vertical = max(.4, R*1.55)
        # Vista superior: cada aro vertical se ve de canto como un óvalo estrecho.
        ax.plot([-.038, -.038], [-vertical, vertical], color="#657482", lw=3)
        ax.plot([.038, .038], [-vertical, vertical], color="#657482", lw=3)
        for signo in (-1, 1):
            ax.add_patch(Ellipse((signo*D/2, 0), width=.022, height=2*R,
                                 fill=False, edgecolor="#ad6d24", lw=3))
        for yy in np.linspace(-min(R*.75,.25), min(R*.75,.25), 4):
            ax.annotate("", (D*.38, yy), (-D*.38, yy),
                        arrowprops=dict(arrowstyle="->", lw=1.7, color="#8750a0"))
        self.carro, = ax.plot([], [], "s", markersize=16, color="#c16128")
        self.captadora, = ax.plot([], [], color="#df9838", lw=3.8)
        ax.text(-D/2, R+.055, "Bobina 1", ha="center", fontsize=8)
        ax.text(D/2, R+.055, "Bobina 2", ha="center", fontsize=8)
        
        ax.text(D*.4, .9*R, "B", fontsize=9, color="#8750a0")
        self.reloj = ax.text(.02, .97, "", transform=ax.transAxes, va="top", fontsize=8.5)
        ax.set(xlim=(-ancho, ancho), ylim=(-vertical, vertical), aspect="auto")
        ax.axis("off")
        ax.text(.99, .02, "Vista superior · aros de canto · dibujo no a escala",
                transform=ax.transAxes, ha="right", fontsize=7.7)
        self.mover_carro(0)
        self.fig.canvas.draw_idle()

    def mover_carro(self, t):
        a = G*np.sin(np.deg2rad(self.p.angulo))
        s = .5*a*t*t
        y = s - CENTRO_CAMPO
        self.carro.set_data([0], [y])
        L = self.p.largo_cm/100
        self.captadora.set_data([0, 0], [y-L/2, y+L/2])
        self.reloj.set_text(f"t = {t:.2f} s | s = {s:.2f} m | θ = {self.p.angulo:g}°")
        for c in self.cursores:
            c.set_xdata([t, t])
        self.marker_campo.set_data([s], [float(campo_en_riel(s, self.p)*1000)])

    def cambiar_angulo(self, value):
        self.p = replace(self.p, angulo=float(value))
        self.actualizar()

    def aplicar_campos(self, _=None):
        try:
            vals = {key: float(w.text.replace(",", ".")) for key, w in self.entradas.items()}
            nuevo = replace(self.p, **vals,
                            sonda=1 if self.radio.value_selected == "Sonda ×1" else 10)
            nuevo.validar()
            self.p = replace(nuevo, vueltas=int(nuevo.vueltas))
            self.actualizar()
            self.estado.set_text("Actualizado. Las cifras son predicciones ideales, no mediciones.")
        except ValueError as err:
            self.estado.set_text(f"Revisar parámetros: {err}")
        self.fig.canvas.draw_idle()

    def reiniciar(self, _=None):
        p = Parametros()
        for k,w in self.entradas.items():
            w.set_val(f"{getattr(p,k):g}")
        self.radio.set_active(0)
        self.p = p
        self.angulo.set_val(p.angulo)
        self.actualizar()
        self.estado.set_text("Valores de ejemplo restablecidos.")

    def alternar_animacion(self, _=None):
        if self.en_marcha:
            self.timer.stop()
            self.en_marcha = False
            self.btn_anim.label.set_text("Animar")
        else:
            self.inicio = time.monotonic()
            self.en_marcha = True
            self.btn_anim.label.set_text("Detener")
            self.timer.start()
        self.fig.canvas.draw_idle()

    def paso_animacion(self):
        t = min(time.monotonic()-self.inicio, self.d["t"][-1])
        self.mover_carro(t)
        if t >= self.d["t"][-1]:
            self.timer.stop()
            self.en_marcha = False
            self.btn_anim.label.set_text("Animar")
        self.fig.canvas.draw_idle()

    def guardar_resultados(self, _=None):
        try:
            file = exportar(self.p)
            self.estado.set_text(f"Guardado: {file.parent.name}/{file.stem} (.png, .csv, .json)")
        except OSError as err:
            self.estado.set_text(f"Error de escritura: {err}")
        self.fig.canvas.draw_idle()

    def comparar(self, _=None):
        import matplotlib.pyplot as plt
        fig, _, _ = comparar_angulos(self.p)
        fig.show()
        self.estado.set_text("Comparación abierta en otra ventana (modelo ideal).")
        self.fig.canvas.draw_idle()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exportar", action="store_true", help="Exporta PNG, CSV y JSON sin ventana")
    parser.add_argument("--comparar", action="store_true", help="Gráfica y CSV para varios ángulos")
    parser.add_argument("--angulo", type=float, default=10)
    parser.add_argument("--vueltas", type=int, default=10)
    parser.add_argument("--campo-mt", type=float, default=1)
    parser.add_argument("--radio-cm", type=float, default=15)
    parser.add_argument("--separacion-cm", type=float, default=15)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()
    p = Parametros(angulo=args.angulo, vueltas=args.vueltas,
                   campo_mT=args.campo_mt, radio_cm=args.radio_cm,
                   separacion_cm=args.separacion_cm)
    try:
        p.validar()
    except ValueError as err:
        parser.error(str(err))
    if args.exportar or args.comparar:
        import matplotlib
        matplotlib.use("Agg")
        if args.exportar:
            file = exportar(p, args.salida)
            print(resumen(p, simular(p)))
            print(f"\nExportado: {file}")
        if args.comparar:
            fig, a, u = comparar_angulos(p, args.salida)
            import matplotlib.pyplot as plt
            plt.close(fig)
            print("Comparación (ángulo grados, U_pico mV):")
            for theta, pico in zip(a, u):
                print(f"  {theta:5.1f}: {pico:.5f}")
            print(f"Guardado en {args.salida}")
    else:
        import matplotlib.pyplot as plt
        app = Aplicacion(p)
        plt.show()
        return app


if __name__ == "__main__":
    main()
