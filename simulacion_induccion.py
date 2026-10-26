"""Simulación interactiva del modelo de borde definido de «marco teorico julio».

Ejecutar: python simulacion_induccion.py
Sin ventana: python simulacion_induccion.py --exportar --vueltas 10

Requiere numpy y matplotlib. Todos los parámetros eléctricos y geométricos,
salvo el largo del riel y las especificaciones del osciloscopio, son ejemplos.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import time

import numpy as np


G = 9.81
LARGO_RIEL = 1.50
CENTRO_CAMPO = LARGO_RIEL / 2
CARPETA_SALIDA = Path(__file__).resolve().parent / "resultados_simulacion"


@dataclass(frozen=True)
class Parametros:
    angulo: float = 10.0            # grados, riel descendente hacia la derecha
    campo_mT: float = 1.0           # EJEMPLO; sustituir por B medido o calculado
    vueltas: int = 1
    ancho_cm: float = 10.0          # lado perpendicular al movimiento
    largo_cm: float = 10.0          # lado paralelo al movimiento
    zona_cm: float = 30.0           # longitud efectiva del campo SOBRE el riel
    direccion_B: float = 90.0       # grados antihorarios desde la horizontal
    resistencia: float = 1.0        # ohmios, resistencia propia de la espira
    carga: float = 1000.0           # ohmios, resistencia medida por el osciloscopio
    sonda: int = 1                  # atenuación: 1 o 10

    def validar(self):
        if not all(np.isfinite(v) for v in asdict(self).values()):
            raise ValueError("Todos los valores deben ser finitos.")
        if not 0 <= self.angulo <= 60:
            raise ValueError("La inclinación debe estar entre 0 y 60 grados.")
        if self.campo_mT < 0 or self.resistencia < 0 or self.carga <= 0:
            raise ValueError("Campo y resistencia propia ≥ 0; carga > 0.")
        if self.vueltas < 1 or self.vueltas != int(self.vueltas):
            raise ValueError("El número de vueltas debe ser un entero positivo.")
        if min(self.ancho_cm, self.largo_cm, self.zona_cm) <= 0:
            raise ValueError("Las dimensiones deben ser positivas.")
        if self.largo_cm + self.zona_cm >= 100 * LARGO_RIEL:
            raise ValueError("Largo de espira + zona de campo debe ser < 150 cm.")
        if not -180 <= self.direccion_B <= 180:
            raise ValueError("La dirección de B debe estar entre −180 y 180 grados.")
        if self.sonda not in (1, 10):
            raise ValueError("La sonda debe ser ×1 o ×10.")


def geometria(p):
    """La espira es paralela al riel; B conserva su dirección en el laboratorio."""
    theta, gamma = np.deg2rad([p.angulo, p.direccion_B])
    # Tangente del riel: (cos(theta), -sin(theta)); normal: (sin(theta), cos(theta)).
    cos_beta = float(np.sin(theta + gamma))
    if abs(cos_beta) < 1e-14:
        cos_beta = 0.0
    izquierda = CENTRO_CAMPO - p.zona_cm / 200
    derecha = CENTRO_CAMPO + p.zona_cm / 200
    return cos_beta, izquierda, derecha


def flujo_y_derivada(posicion, p):
    """Flujo por vuelta y dPhi/ds; área solapada con una región uniforme.

    Ecs. 16–18 de Julio, extendidas a entrada Y salida. Se usa el perfil
    efectivo 1D del apartado 2.5, no la fórmula axial fuera de su eje.
    En los bordes ideales la derivada salta; se asigna el valor exterior.
    """
    s = np.asarray(posicion, dtype=float)
    cos_beta, izquierda, derecha = geometria(p)
    frente, atras = s + p.largo_cm / 200, s - p.largo_cm / 200
    solapamiento = np.maximum(0, np.minimum(frente, derecha) - np.maximum(atras, izquierda))
    frente_dentro = (frente > izquierda) & (frente < derecha)
    atras_dentro = (atras > izquierda) & (atras < derecha)
    factor = p.campo_mT * 1e-3 * p.ancho_cm * 1e-2 * cos_beta
    flujo = factor * solapamiento
    derivada = factor * (frente_dentro.astype(float) - atras_dentro.astype(float))
    return flujo, derivada


def simular(p=Parametros(), muestras=2401):
    p.validar()
    if muestras < 3:
        raise ValueError("Se necesitan al menos tres muestras.")
    a = G * np.sin(np.deg2rad(p.angulo))
    cos_beta, izquierda, derecha = geometria(p)
    bordes = np.sort([izquierda - p.largo_cm / 200, izquierda + p.largo_cm / 200,
                      derecha - p.largo_cm / 200, derecha + p.largo_cm / 200])
    if a > 0:
        tiempo_final = np.sqrt(2 * LARGO_RIEL / a)
        eventos = np.sqrt(2 * bordes / a)
        # Incluir ambos lados de cada borde impide perder pulsos estrechos.
        dt = min(tiempo_final * 1e-9, np.min(np.diff(np.unique(eventos))) * 1e-5)
        t = np.unique(np.r_[np.linspace(0, tiempo_final, muestras),
                            eventos - dt, eventos, eventos + dt])
        pulsos_ms = 1000 * np.array([eventos[1] - eventos[0], eventos[3] - eventos[2]])
        ventana_senal = eventos[-1] - eventos[0]
    else:
        t = np.linspace(0, 3, muestras)
        eventos = np.array([])
        pulsos_ms = np.zeros(2)
        ventana_senal = 0.0
    s, v = 0.5 * a * t**2, a * t
    flujo, derivada = flujo_y_derivada(s, p)
    fem = -p.vueltas * derivada * v
    # Manual: 1 MΩ directo; 10 MΩ para una sonda pasiva ×10 equivalente.
    entrada = 1e6 * p.sonda
    carga_efectiva = 1 / (1 / p.carga + 1 / entrada)
    corriente = fem / (p.resistencia + carga_efectiva)
    voltaje = corriente * carga_efectiva
    entrada_BNC = voltaje / p.sonda
    pico = float(np.max(np.abs(voltaje)))
    return dict(t=t, s=s, v=v, flujo=flujo, fem=fem, voltaje=voltaje,
                corriente=corriente, entrada_BNC=entrada_BNC,
                fem_pico=float(np.max(np.abs(fem))), voltaje_pico=pico,
                voltaje_pp=float(np.ptp(voltaje)), cos_beta=cos_beta,
                beta=float(np.rad2deg(np.arccos(np.clip(cos_beta, -1, 1)))),
                rapidez_centro=float(np.sqrt(2 * a * CENTRO_CAMPO)),
                div_normal=pico / p.sonda / 0.005,
                div_expandido=pico / p.sonda / 0.001,
                pulsos_ms=pulsos_ms, eventos=eventos, ventana_senal=ventana_senal)


def base_tiempo(d):
    """Escala calibrada 1–2–5 para cubrir el paso por el campo en unas 8 divisiones."""
    if d["ventana_senal"] == 0:
        return "sin paso por el campo"
    escalas = np.array([m * 10.0**e for e in range(-7, 0) for m in (1, 2, 5)])
    escalas = escalas[(escalas >= 2e-7) & (escalas <= 0.1)]
    opciones = escalas[escalas >= d["ventana_senal"] / 8]
    if not len(opciones):
        return "100 ms/div; observar los pulsos por separado"
    return f"{opciones[0] * 1000:g} ms/div"


def resumen(p, d):
    div = d["div_expandido"]
    if d["fem_pico"] == 0:
        estado = "Sin fem para estos parámetros."
    elif div < 1:
        estado = "Pico < 1 división aun con Y×5: señal pequeña."
    else:
        estado = "Pico ≥ 1 división con Y×5: amplitud candidata."
    return (
        f"β (normal–campo): {d['beta']:.1f}° | v en el centro: {d['rapidez_centro']:.2f} m/s\n"
        f"Fem pico: {d['fem_pico'] * 1000:.3f} mV\n"
        f"Voltaje en la carga: {d['voltaje_pico'] * 1000:.3f} mV pico"
        f" / {d['voltaje_pp'] * 1000:.3f} mV pico a pico\n"
        f"Hameg, sonda ×{p.sonda}: {d['div_normal']:.2f} div a 5 mV/div;"
        f" {div:.2f} div con Y×5 (1 mV/div)\n"
        f"Pulsos entrada / salida: {d['pulsos_ms'][0]:.1f} / {d['pulsos_ms'][1]:.1f} ms"
        f" | Base inicial: {base_tiempo(d)}\n"
        f"{estado}\n"
        "La detectabilidad requiere comprobar ruido y disparo; 1 div es una referencia visual."
    )


def dibujar_graficas(ax_pos, ax_fem, p, d):
    for ax in (ax_pos, ax_fem):
        ax.clear()
        ax.grid(alpha=0.22)
        ax.set_xlabel("Tiempo (s)")
        ax.set_xlim(0, d["t"][-1])
    ax_pos.plot(d["t"], d["s"], color="#246791", lw=2)
    ax_pos.axhline(CENTRO_CAMPO, color="#87938e", ls="--", lw=1, label="Centro del campo: 0,75 m")
    ax_pos.set(title="Posición del centro de la espira", ylabel="Distancia sobre el riel (m)", ylim=(0, 1.57))
    ax_pos.legend(fontsize=8, loc="upper left")
    ax_fem.plot(d["t"], 1000 * d["fem"], color="#ba5c25", lw=2.3, label="Fem inducida")
    ax_fem.plot(d["t"], 1000 * d["voltaje"], color="#247f6e", lw=1.4, ls="--", label="Voltaje en la carga")
    ax_fem.axhline(0, color="#87938e", lw=0.7)
    escala = max(0.01, 1000 * d["fem_pico"] * 1.2)
    ax_fem.set(title="Fem y voltaje durante el paso", ylabel="Voltaje (mV)", ylim=(-escala, escala))
    ax_fem.legend(fontsize=8, loc="upper left")


def exportar(p, carpeta=CARPETA_SALIDA):
    import matplotlib.pyplot as plt

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    d = simular(p)
    nombre = f"simulacion_{p.angulo:g}grados_{p.vueltas}vueltas"
    datos = np.column_stack([d[k] for k in ("t", "s", "v", "flujo", "fem", "voltaje", "corriente")])
    np.savetxt(carpeta / f"{nombre}.csv", datos, delimiter=",",
               header="t_s,s_m,v_m_s,flujo_por_vuelta_Wb,fem_V,voltaje_carga_V,corriente_total_A",
               comments="")
    (carpeta / f"{nombre}.json").write_text(json.dumps({
        "origen": "Simulación ideal, NO datos medidos", "parametros": asdict(p),
        "largo_riel_m": LARGO_RIEL, "resumen": resumen(p, d),
        "modelo": "Julio, apartado 2.5: campo uniforme con borde definido. Espira paralela al riel.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    dibujar_graficas(*axes, p, d)
    fig.suptitle(f"Predicción ideal · riel de 1,50 m · θ = {p.angulo:g}° · {p.vueltas} vuelta(s)")
    fig.text(0.06, 0.07, f"B = {p.campo_mT:g} mT | espira {p.largo_cm:g} × {p.ancho_cm:g} cm | "
             f"zona = {p.zona_cm:g} cm | dirección B = {p.direccion_B:g}° | "
             f"r = {p.resistencia:g} Ω | carga = {p.carga:g} Ω", fontsize=9)
    fig.text(0.06, 0.025, "Valores de ejemplo ajustables; borde abrupto ideal. No constituye una medición del equipo.", fontsize=9)
    fig.tight_layout(rect=(0, 0.12, 1, 0.94))
    fig.savefig(carpeta / f"{nombre}.png", dpi=170)
    plt.close(fig)
    return carpeta / f"{nombre}.png"


class Aplicacion:
    def __init__(self, p=Parametros()):
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Button, RadioButtons, Slider, TextBox

        self.p = p
        self.fig = plt.figure(figsize=(14, 9), facecolor="#f7f8fa")
        self.fig.canvas.manager.set_window_title("Inducción · riel de 150 cm · Hameg HM 203-7")
        self.fig.text(0.06, 0.955, "Espira móvil y bobinas de Helmholtz", size=19, weight="bold")
        self.fig.text(0.06, 0.92, "Modelo sencillo de Julio · riel recto de 1,50 m · centro a 0,75 m", size=11)
        self.ax_escena = self.fig.add_axes([0.06, 0.66, 0.61, 0.22])
        self.ax_pos = self.fig.add_axes([0.06, 0.35, 0.275, 0.23])
        self.ax_fem = self.fig.add_axes([0.40, 0.35, 0.275, 0.23])
        self.texto = self.fig.text(0.06, 0.28, "", va="top", fontsize=9.7, linespacing=1.5)
        self.fig.text(0.72, 0.91, "Parámetros de ejemplo", weight="bold", fontsize=12)
        self.fig.text(0.72, 0.884, "Editar y pulsar «Aplicar». Unidades indicadas.", fontsize=8.5)
        campos = [
            ("campo_mT", "Campo B (mT)"), ("vueltas", "Vueltas de la espira"),
            ("ancho_cm", "Ancho transversal (cm)"), ("largo_cm", "Largo de espira (cm)"),
            ("zona_cm", "Zona de campo en riel (cm)"), ("direccion_B", "Dirección fija B (°)"),
            ("resistencia", "Resistencia espira (Ω)"), ("carga", "Resistencia carga (Ω)"),
        ]
        self.entradas = {}
        for i, (clave, etiqueta) in enumerate(campos):
            y = 0.832 - i * 0.047
            self.fig.text(0.72, y + 0.008, etiqueta, fontsize=9)
            caja = TextBox(self.fig.add_axes([0.907, y, 0.07, 0.033]), "", initial=f"{getattr(p, clave):g}")
            self.entradas[clave] = caja
        self.fig.text(0.72, 0.466, "90°: B vertical. La espira es paralela al riel.\nAl variar θ, la dirección de B se mantiene.", fontsize=8.5)
        self.radio = RadioButtons(self.fig.add_axes([0.72, 0.365, 0.25, 0.075]), ["Sonda ×1", "Sonda ×10"], active=0 if p.sonda == 1 else 1)
        self.aplicar = Button(self.fig.add_axes([0.72, 0.31, 0.12, 0.035]), "Aplicar")
        self.restablecer = Button(self.fig.add_axes([0.85, 0.31, 0.12, 0.035]), "Restablecer")
        self.aplicar.on_clicked(self.aplicar_campos)
        self.restablecer.on_clicked(self.reiniciar)
        self.fig.text(0.72, 0.277, "Hameg HM 203-7\n5 mV/div; 1 mV/div con Y×5.\nEntrada: 1 MΩ || 25 pF (directa).\nUsar acoplamiento DC y ajuste CAL.\nSonda ×10 reduce diez veces la altura.\nEl modelo usa solo la carga resistiva.", fontsize=9, va="top", linespacing=1.5)
        self.angulo = Slider(self.fig.add_axes([0.15, 0.095, 0.46, 0.025]), "Inclinación θ", 0, 60, valinit=p.angulo, valstep=0.1, valfmt="%1.1f°")
        self.angulo.on_changed(self.cambiar_angulo)
        self.animar = Button(self.fig.add_axes([0.72, 0.105, 0.11, 0.038]), "Animar")
        self.guardar = Button(self.fig.add_axes([0.845, 0.105, 0.13, 0.038]), "PNG + CSV")
        self.animar.on_clicked(self.alternar_animacion)
        self.guardar.on_clicked(self.guardar_resultados)
        self.estado = self.fig.text(0.06, 0.045, "", fontsize=9, color="#8a3e16")
        self.fig.text(0.06, 0.014, "Ideal: sin rozamiento, autoinducción ni frenado magnético. La zona uniforme es una aproximación; no reproduce el campo real 3D.", fontsize=8.5)
        self.timer = self.fig.canvas.new_timer(interval=40)
        self.timer.add_callback(self.paso_animacion)
        self.en_marcha = False
        self.actualizar()

    def actualizar(self):
        from matplotlib.patches import Ellipse

        self.timer.stop()
        self.en_marcha = False
        self.animar.label.set_text("Animar")
        self.d = simular(self.p)
        dibujar_graficas(self.ax_pos, self.ax_fem, self.p, self.d)
        self.texto.set_text(resumen(self.p, self.d))
        self.cursores = [ax.axvline(0, color="#59636c", lw=1, alpha=0.55) for ax in (self.ax_pos, self.ax_fem)]
        ax = self.ax_escena
        ax.clear()
        theta, gamma = np.deg2rad([self.p.angulo, self.p.direccion_B])
        self.e = np.array([np.cos(theta), -np.sin(theta)])
        b = np.array([np.cos(gamma), np.sin(gamma)])
        puntas = np.outer([-0.75, 0.75], self.e)
        zona = np.outer([-self.p.zona_cm / 200, self.p.zona_cm / 200], self.e)
        ax.plot(*zona.T, color="#b2dfd4", lw=24, solid_capstyle="butt", alpha=0.65)
        ax.plot(*puntas.T, color="#586570", lw=3)
        for signo in (-1, 1):
            centro = signo * 0.13 * b
            ax.add_patch(Ellipse(centro, 0.48, 0.045, angle=self.p.direccion_B - 90,
                                fill=False, lw=2.3, edgecolor="#617e9c"))
        origen = np.array([0.43, 0.21])
        ax.annotate("", xy=origen + 0.17 * b, xytext=origen,
                    arrowprops=dict(arrowstyle="->", color="#246791", lw=2))
        ax.text(0.45, 0.12, f"B fijo ({self.p.direccion_B:g}°)", fontsize=9, color="#246791")
        self.carro, = ax.plot([], [], color="#c46125", lw=5, marker="o", markevery=[1], ms=7)
        self.reloj = ax.text(0.01, 0.96, "", transform=ax.transAxes, va="top", fontsize=9)
        ax.text(0.99, 0.02, "Vista lateral esquemática · franja verde: zona uniforme equivalente",
                transform=ax.transAxes, ha="right", fontsize=8)
        alto = max(0.40, (0.75 + self.p.largo_cm / 200) * np.sin(theta) + 0.08)
        ax.set(xlim=(-1.1, 1.1), ylim=(-alto, alto), aspect="equal")
        ax.axis("off")
        self.mover_carro(0)
        self.fig.canvas.draw_idle()

    def mover_carro(self, t):
        s = 0.5 * G * np.sin(np.deg2rad(self.p.angulo)) * t**2
        puntos = np.outer([s - 0.75 - self.p.largo_cm / 200, s - 0.75,
                           s - 0.75 + self.p.largo_cm / 200], self.e)
        self.carro.set_data(*puntos.T)
        self.reloj.set_text(f"t = {t:.2f} s   |   posición = {s:.2f} m")
        for cursor in self.cursores:
            cursor.set_xdata([t, t])

    def cambiar_angulo(self, valor):
        self.p = replace(self.p, angulo=float(valor))
        self.actualizar()

    def aplicar_campos(self, _=None):
        try:
            valores = {k: float(c.text.replace(",", ".")) for k, c in self.entradas.items()}
            nuevo = replace(self.p, **valores, sonda=1 if self.radio.value_selected == "Sonda ×1" else 10)
            nuevo.validar()
            self.p = replace(nuevo, vueltas=int(nuevo.vueltas))
            self.estado.set_text("Parámetros aplicados. Las cifras son predicciones del modelo ideal.")
            self.actualizar()
        except ValueError as exc:
            self.estado.set_text(f"Revisar parámetros: {exc}")
            self.fig.canvas.draw_idle()

    def reiniciar(self, _=None):
        p = Parametros()
        for clave, caja in self.entradas.items():
            caja.set_val(f"{getattr(p, clave):g}")
        self.radio.set_active(0)
        self.p = p
        self.angulo.set_val(p.angulo)
        self.estado.set_text("Valores de ejemplo restablecidos.")

    def alternar_animacion(self, _=None):
        if self.en_marcha:
            self.timer.stop()
            self.en_marcha = False
            self.animar.label.set_text("Animar")
        else:
            self.inicio = time.monotonic()
            self.en_marcha = True
            self.animar.label.set_text("Detener")
            self.timer.start()
        self.fig.canvas.draw_idle()

    def paso_animacion(self):
        t = min(time.monotonic() - self.inicio, self.d["t"][-1])
        self.mover_carro(t)
        if t >= self.d["t"][-1]:
            self.timer.stop()
            self.en_marcha = False
            self.animar.label.set_text("Animar")
        self.fig.canvas.draw_idle()

    def guardar_resultados(self, _=None):
        try:
            archivo = exportar(self.p)
            self.estado.set_text(f"Guardado: resultados_simulacion/{archivo.stem} (.png, .csv, .json)")
        except OSError as exc:
            self.estado.set_text(f"No se pudo guardar: {exc}")
        self.fig.canvas.draw_idle()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exportar", action="store_true", help="Guardar PNG, CSV y parámetros sin abrir ventana")
    parser.add_argument("--angulo", type=float, default=10)
    parser.add_argument("--vueltas", type=int, default=1)
    parser.add_argument("--campo-mt", type=float, default=1)
    parser.add_argument("--salida", type=Path, default=CARPETA_SALIDA)
    args = parser.parse_args()
    p = Parametros(angulo=args.angulo, vueltas=args.vueltas, campo_mT=args.campo_mt)
    try:
        p.validar()
    except ValueError as exc:
        parser.error(str(exc))
    if args.exportar:
        import matplotlib
        matplotlib.use("Agg")
        archivo = exportar(p, args.salida)
        print(resumen(p, simular(p)))
        print(f"\nGráficas: {archivo}\nCSV y parámetros: misma carpeta.")
    else:
        import matplotlib.pyplot as plt
        app = Aplicacion(p)
        plt.show()
        return app


if __name__ == "__main__":
    main()
