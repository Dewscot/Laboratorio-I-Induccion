"""Regenera los TXT de picos a partir de las trazas del osciloscopio en datos/."""

import csv
from pathlib import Path

import numpy as np
from scipy.ndimage import median_filter


ANGULOS = (5, 6, 7, 8, 9, 10, 11, 12.5, 13, 14, 15)
RECENTRADOS = (5, 6, 7, 8, 9)
VENTANA = 21  # muestras


def medir_picos(archivo):
    # La última fila exportada puede no contener MATH1V.
    with archivo.open(encoding="utf-8-sig", newline="") as entrada:
        filas = csv.DictReader(entrada)
        muestras = [(float(fila["Time(s)"]), float(fila["MATH1V"]))
                    for fila in filas if fila["MATH1V"] not in (None, "")]
    if len(muestras) <= VENTANA:
        raise ValueError(f"Muy pocas muestras de MATH1V en {archivo.name}")

    t, voltaje = np.array(muestras).T
    voltaje *= 1000  # V a mV
    if not np.isfinite(voltaje).all() or not np.all(np.diff(t) > 0):
        raise ValueError(f"Traza de voltaje o tiempo inválida en {archivo.name}")

    suavizado = median_filter(voltaje, size=VENTANA)
    borde = VENTANA // 2
    i_pos = borde + np.argmax(suavizado[borde:-borde])
    # El lóbulo negativo precede al positivo en estas pasadas.
    candidatos = np.flatnonzero((t >= t[i_pos] - 0.52) & (t <= t[i_pos] - 0.15)
                                & (np.arange(len(t)) >= borde))
    if candidatos.size == 0:
        raise ValueError(f"Sin ventana para el pico negativo en {archivo.name}")
    i_neg = candidatos[np.argmin(suavizado[candidatos])]

    reposo = (t < t[i_neg] - 0.14) | (t > t[i_pos] + 0.14)
    if not reposo.any():
        raise ValueError(f"Sin tramo para estimar la línea base en {archivo.name}")
    base = np.median(voltaje[reposo])
    positivo, negativo = suavizado[[i_pos, i_neg]] - base
    if positivo <= 0 or negativo >= 0:
        raise ValueError(f"Polaridad inesperada en {archivo.name}")
    return positivo, negativo


def extraer_picos(datos, salida):
    archivos = list(datos.rglob("Rep* grados0.csv"))
    pasadas = []
    for angulo in ANGULOS:
        sufijo = ".1" if angulo in RECENTRADOS else ""
        for rep in (1, 2):
            nombre = f"Rep{rep}{sufijo} {angulo:g} grados0.csv"
            rutas = [archivo for archivo in archivos if archivo.name == nombre]
            if len(rutas) != 1:
                ubicaciones = ", ".join(str(ruta.relative_to(datos)) for ruta in sorted(rutas))
                detalle = ubicaciones or "archivo ausente"
                raise ValueError(f"Se esperaba una copia de {nombre}: {detalle}")
            pasadas.append((angulo, *medir_picos(rutas[0])))

    # Guarda los TXT después de medir todas las pasadas seleccionadas.
    for columna, (tipo, extremo) in enumerate(
        (("positivos", "máximo positivo"), ("negativos", "mínimo negativo")), start=1
    ):
        lineas = [
            f"# {extremo} respecto de la línea base de Math1 (RIGOL DHO804).",
            "# 5 a 9 grados: Rep1.1 y Rep2.1 tras recentrar; demás ángulos: Rep1 y Rep2.",
            "# Dos filas por ángulo, en orden de repetición (1 y 2).",
            "# angulo_deg voltaje_mV",
        ]
        for pasada in pasadas:
            valor = np.round(pasada[columna], 6)
            lineas.append(f"{pasada[0]:g} {valor}")
        ruta = salida / f"picos_{tipo}.txt"
        if not ruta.exists() or ruta.read_text(encoding="utf-8").splitlines() != lineas:
            ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return len(pasadas)


if __name__ == "__main__":
    carpeta = Path(__file__).resolve().parent
    cantidad = extraer_picos(carpeta.parent / "datos", carpeta)
    print(f"Se procesaron {cantidad} pasadas. Los TXT de picos están en analisis/.")
