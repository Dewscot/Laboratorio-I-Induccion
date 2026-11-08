"""Simulación interactiva: imán móvil en el costado del carrito y espira fija.

Ejecutar desde una terminal de VS Code (Windows / Miniforge):
    python simulacion_iman_lateral_interactiva.py

Modo no interactivo, para crear una imagen:
    python simulacion_iman_lateral_interactiva.py --exportar

Verificar cálculos y velocidad de actualización sin abrir ventanas:
    python simulacion_iman_lateral_interactiva.py --probar

Requiere únicamente NumPy y Matplotlib; la ventana usa Tkinter/TkAgg o QtAgg.

Física (exploratoria): imán de 35 x 15 mm aproximado por un dipolo
alineado transversalmente; flujo ≈ área de la espira * campo en su centro.
Esta aproximación es especialmente limitada a distancias pequeñas y NO es
una predicción calibrada del montaje real.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import time

import numpy as np
import matplotlib

G = 9.81
L_RIEL = 1.50
RADIO_CAPTADORA_M = 0.025          # diámetro ≈ 5 cm (supuesto)
RADIO_IMAN_M = 0.0175              # diámetro 35 mm
ESPESOR_IMAN_M = 0.015            # espesor 15 mm
BR_SUPUESTO_T = 1.2               # remanencia estimada, no medida
AREA = np.pi * RADIO_CAPTADORA_M**2
# mu0 m/(4*pi) = Br*radio^2*espesor/4 para dipolo uniforme ideal.
COEF_DIPOLO = BR_SUPUESTO_T * RADIO_IMAN_M**2 * ESPESOR_IMAN_M / 4.0


def seleccionar_backend(exportar: bool) -> None:
    """Importante: seleccionar ANTES de importar matplotlib.pyplot."""
    if exportar:
        matplotlib.use('Agg', force=True)
        return

    # Preferimos Tk porque se incluye habitualmente con Python en Windows.
    try:
        import tkinter  # noqa: F401
        matplotlib.use('TkAgg', force=True)
        return
    except (ImportError, ModuleNotFoundError):
        pass

    # Si Tk no está instalado, utilizar Qt si ya existe en el entorno.
    for modulo in ('PySide6', 'PyQt6', 'PySide2', 'PyQt5'):
        try:
            __import__(modulo)
            matplotlib.use('QtAgg', force=True)
            return
        except (ImportError, ModuleNotFoundError):
            continue

    raise SystemExit(
        'No hay un backend interactivo disponible. En tu terminal ejecuta:\n'
        '  python -c "import tkinter; print(\'Tk disponible\')"\n'
        'Si falla, en tu entorno Conda prueba: mamba install tk\n'
        'Como alternativa para generar solo PNG: --exportar'
    )


def campo_y_derivada(x_m: np.ndarray, d_m: np.ndarray):
    """B_y y derivada dB_y/dx de un dipolo transversal.

    x: desplazamiento longitudinal imán-espira, en metros.
    d: separación desde el CENTRO del imán al plano central de la espira,
       no la distancia desde su cara. Admiten broadcasting de NumPy.
    """
    r2 = x_m*x_m + d_m*d_m
    b = COEF_DIPOLO * (2*d_m*d_m - x_m*x_m) / r2**2.5
    dbdx = 3*COEF_DIPOLO * x_m*(x_m*x_m - 4*d_m*d_m) / r2**3.5
    return b, dbdx


def amplitud_distancias(angulo_grados: float, vueltas: int,
                        posicion_m: float, distancias_cm: np.ndarray) -> np.ndarray:
    """Barrido en distancia, calculado vectorialmente, sin 50 simulaciones."""
    x = np.linspace(-0.23, 0.23, 601)[None, :]
    d = np.asarray(distancias_cm, float)[:, None] / 100
    s = posicion_m + x
    v = np.sqrt(np.maximum(0., 2*G*np.sin(np.deg2rad(angulo_grados))*s))
    _, grad = campo_y_derivada(x, d)
    return np.max(np.abs(-vueltas*AREA*v*grad), axis=1)*1000


def amplitud_angulos(vueltas: int, posicion_m: float,
                       distancia_cm: float, angulos_grados: np.ndarray) -> np.ndarray:
    """El perfil espacial es fijo, así que la amplitud ∝ sqrt(sinθ)."""
    x = np.linspace(-0.23, 0.23, 601)
    s = posicion_m + x
    _, grad = campo_y_derivada(x, distancia_cm/100)
    factor = vueltas * AREA * np.max(np.abs(np.sqrt(2*G*s)*grad))*1000
    return factor * np.sqrt(np.maximum(0., np.sin(np.deg2rad(angulos_grados))))


def calcular(angulo: float = 10., distancia_cm: float = 5.,
             vueltas: int = 80, posicion_m: float = .75) -> dict:
    """Curva temporal local alrededor del paso de la espira fija."""
    x = np.linspace(-0.23, 0.23, 801)
    s = posicion_m + x
    a = G*np.sin(np.deg2rad(angulo))
    b, grad = campo_y_derivada(x, distancia_cm/100)
    v = np.sqrt(np.maximum(0., 2*a*s))
    fem_mV = -vueltas*AREA*v*grad*1000
    if a > 0:
        t_rel_ms = 1000*(np.sqrt(2*s/a)-np.sqrt(2*posicion_m/a))
        v_centro = np.sqrt(2*a*posicion_m)
    else:
        # Reposo: sin tiempo de paso real; se mantiene la curva nula.
        t_rel_ms = np.linspace(-250, 250, len(x))
        v_centro = 0.
    return {
        'x_cm': x*100,
        't_rel_ms': t_rel_ms,
        'B_mT': b*1000,
        'fem_mV': fem_mV,
        'pico_mV': float(np.max(np.abs(fem_mV))),
        'pp_mV': float(np.ptp(fem_mV)),
        'v_centro': float(v_centro),
    }


def crear_ventana():
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.widgets import Slider, Button

    fig = plt.figure(figsize=(13.6, 9), facecolor='#f5f7fa')
    try:
        fig.canvas.manager.set_window_title('Laboratorio I · Imán móvil, espira fija')
    except AttributeError:
        pass

    fig.text(.055, .964, 'Inducción · imán móvil y espira fija', fontsize=18,
             weight='bold', color='#1c2c3b')
    fig.text(.055, .935,
             'Riel 1,50 m · imán 35 × 15 mm · captadora 5 cm de diámetro · modelo exploratorio',
             fontsize=10, color='#526273')
    resumen = fig.text(.055, .899, '', fontsize=10.5, color='#153b4a',
                       bbox=dict(boxstyle='round,pad=.35', fc='#e9f2f5', ec='#b1cbd5'))

    ax_escena = fig.add_axes([.06,.718,.88,.145])
    ax_t = fig.add_axes([.075,.482,.395,.185])
    ax_b = fig.add_axes([.555,.482,.385,.185])
    ax_d = fig.add_axes([.075,.289,.395,.115])
    ax_a = fig.add_axes([.555,.289,.385,.115])
    for ax in (ax_t,ax_b,ax_d,ax_a):
        ax.set_facecolor('white')
        ax.grid(alpha=.2)
        ax.tick_params(labelsize=8)
    ax_t.set(title='Tensión inducida cerca del paso',
             xlabel='Tiempo respecto al cruce del centro (ms)', ylabel='Fem (mV)')
    ax_b.set(title='Campo normal en el centro de la captadora',
             xlabel='Posición relativa al cruce (cm)', ylabel='B (mT)')
    ax_d.set(title='Fem pico frente a separación lateral',
             xlabel='Distancia entre centros (cm)', ylabel='Fem pico (mV)')
    ax_a.set(title='Fem pico frente a inclinación',
             xlabel='Ángulo del riel (grados)',ylabel='Fem pico (mV)')
    for ax in (ax_t, ax_b, ax_d, ax_a):
        ax.title.set_fontsize(10)
        ax.xaxis.label.set_fontsize(9)
        ax.yaxis.label.set_fontsize(9)

    dr = np.linspace(3,12,91)
    ar = np.linspace(0,15,61)
    t_line, = ax_t.plot([], [], color='#be5b28', lw=2)
    b_line, = ax_b.plot([], [], color='#27769c', lw=2)
    d_line, = ax_d.plot([], [], color='#267f70', lw=2)
    a_line, = ax_a.plot([], [], color='#51669c', lw=2)
    d_marker, = ax_d.plot([], [], 'o', color='#be5b28', ms=7)
    a_marker, = ax_a.plot([], [], 'o', color='#be5b28', ms=7)
    ax_t.axhline(0, lw=1, color='#87939a', ls='--')
    ax_b.axvline(0, lw=1, color='#87939a', ls='--')

    def escena(posicion_m, distancia_cm):
        ax_escena.clear()
        ax_escena.set_xlim(0, 10)
        ax_escena.set_ylim(0, 3.1)
        ax_escena.axis('off')
        ax_escena.text(.15, 2.88, 'VISTA SUPERIOR · esquema, no a escala',
                       fontsize=8.5, color='#62707e')
        x0,x1= .55,9.4
        x_coil=x0+(x1-x0)*posicion_m/L_RIEL
        x_m=max(1.05,x_coil-.95)
        ax_escena.plot([x0,x1],[.92,.92],lw=6,color='#728190',solid_capstyle='round')
        ax_escena.plot([x0,x1],[1.51,1.51],lw=6,color='#728190',solid_capstyle='round')
        ax_escena.add_patch(Rectangle((x_m-.48,.92),.9,.59,fc='#c3d1d9',ec='#6b7680'))
        ax_escena.add_patch(Rectangle((x_m-.11,1.46),.23,.25,fc='#c84f4f',ec='#913b3b'))
        ax_escena.annotate('',xy=(x_m+.72,1.22),xytext=(x_m+.35,1.22),
                           arrowprops=dict(arrowstyle='->',lw=1.8,color='#253440'))
        ax_escena.text(x_m-.10,.55,'Carrito + imán',ha='center',fontsize=9)
        yc=2.25+.045*(distancia_cm-5)
        # Espira vertical longitudinal: desde arriba, se observa de canto.
        for yy in (yc-.04,yc,yc+.04):
            ax_escena.plot([x_coil-.27,x_coil+.27],[yy,yy],lw=2.5,color='#c18445')
        ax_escena.plot([x_coil,x_coil],[1.73,yc-.10],ls='--',color='#268c88')
        ax_escena.text(x_coil+.22,1.95,f'd = {distancia_cm:.1f} cm',fontsize=9,color='#167b79')
        ax_escena.text(x_coil,yc+.23,'Espira fija',fontsize=9,ha='center')
        ax_escena.text(x_coil,.37,f's = {posicion_m:.2f} m',fontsize=9,ha='center')
        ax_escena.text(x0,.12,'Inicio',fontsize=9)
        ax_escena.text(x1,.12,'Final',fontsize=9,ha='right')

    sx = [.171,.127,.083,.039]
    slider_angulo = Slider(fig.add_axes([.20,sx[0],.54,.021]), 'Inclinación (°)',
                           0,15,valinit=10,valstep=.5)
    slider_dist = Slider(fig.add_axes([.20,sx[1],.54,.021]), 'Distancia (cm)',
                         3,12,valinit=5,valstep=.5)
    slider_n = Slider(fig.add_axes([.20,sx[2],.54,.021]), 'Vueltas',
                      70,90,valinit=80,valstep=1,valfmt='%1.0f')
    slider_pos = Slider(fig.add_axes([.20,sx[3],.54,.021]), 'Posición (m)',
                        .50,1.10,valinit=.75,valstep=.05,valfmt='%1.2f')
    btn = Button(fig.add_axes([.81,.072,.13,.05]), 'Restablecer')
    fig.text(.055,.014,
             'Dipolo puntual, campo evaluado en el centro de cada vuelta. '
             'No incluye ruido, fricción, magnetización del carrito ni distribución finita del campo.',
             fontsize=8,color='#5c6872')

    def update(_=None):
        ang=slider_angulo.val
        dist=slider_dist.val
        n=int(slider_n.val)
        pos=slider_pos.val
        r=calcular(ang,dist,n,pos)
        peak_d=amplitud_distancias(ang,n,pos,dr)
        peak_a=amplitud_angulos(n,pos,dist,ar)
        t_line.set_data(r['t_rel_ms'],r['fem_mV'])
        b_line.set_data(r['x_cm'],r['B_mT'])
        d_line.set_data(dr,peak_d)
        a_line.set_data(ar,peak_a)
        d_marker.set_data([dist],[r['pico_mV']])
        a_marker.set_data([ang],[r['pico_mV']])
        for ax in (ax_t,ax_b,ax_d,ax_a):
            ax.relim()
            ax.autoscale_view()
        escena(pos,dist)
        resumen.set_text(
            f'θ = {ang:g}°   |   N = {n} vueltas   |   d = {dist:.1f} cm   |   '
            f's = {pos:.2f} m   |   v ≈ {r["v_centro"]:.2f} m/s   |   '
            f'fem pico ≈ {r["pico_mV"]:.1f} mV'
        )
        fig._ultimo_resultado = r
        fig.canvas.draw_idle()

    for sl in (slider_angulo,slider_dist,slider_n,slider_pos):
        sl.on_changed(update)
    btn.on_clicked(lambda event: [sl.reset() for sl in
                                   (slider_angulo,slider_dist,slider_n,slider_pos)])
    fig._controles = (slider_angulo,slider_dist,slider_n,slider_pos)
    fig._actualizar = update
    update()
    return fig


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exportar',action='store_true',help='guardar PNG sin ventana')
    parser.add_argument('--probar',action='store_true',help='pruebas automáticas sin ventana')
    args=parser.parse_args()
    seleccionar_backend(args.exportar or args.probar)
    from matplotlib import pyplot as plt

    try:
        fig=crear_ventana()
    except ImportError as exc:
        raise SystemExit(
            'No se pudo abrir una ventana con el backend seleccionado. '
            'Prueba en terminal: python -c "import tkinter; print(\'Tk disponible\')". '
            'Si no está disponible: mamba install tk. '
            'Para generar una imagen: --exportar'
        ) from exc

    if args.probar:
        sl_ang,sl_dist,sl_n,sl_pos=fig._controles
        t0=time.perf_counter()
        sl_pos.set_val(1.0)
        sl_dist.set_val(10)
        sl_n.set_val(70)
        sl_ang.set_val(15)
        elapsed=time.perf_counter()-t0
        a=calcular(10,5,80,.75)
        b=calcular(10,5,80,1.)
        assert b['v_centro']>a['v_centro']
        assert b['pico_mV']>a['pico_mV']
        assert calcular(0,5,80,.75)['pico_mV']==0
        assert calcular(10,5,70,.75)['pico_mV']<a['pico_mV']
        assert calcular(10,10,80,.75)['pico_mV']<a['pico_mV']
        print('Pruebas físicas: OK')
        print(f'Actualización de los 4 controles: {elapsed:.3f} s (incluye redibujado diferido)')
        print(f'Ejemplo: s=0,75 m: {a["pico_mV"]:.1f} mV; s=1,00 m: {b["pico_mV"]:.1f} mV')
        plt.close(fig)
    elif args.exportar:
        salida=Path(__file__).with_name('simulacion_iman_lateral_interactiva_preview.png')
        fig.savefig(salida,dpi=150)
        plt.close(fig)
        print('Imagen guardada en:',salida)
    else:
        print('Backend interactivo:',matplotlib.get_backend())
        print('Abriendo ventana... Cambia los cuatro deslizadores sin volver a ejecutar Python.')
        plt.show(block=True)


if __name__=='__main__':
    main()
