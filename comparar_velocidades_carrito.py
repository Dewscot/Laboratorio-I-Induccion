"""Comparación de velocidades de un carrito sobre un plano inclinado.

Modelo ideal: v² = v0² + 2*g*d*sin(theta).

Edita los valores de CONFIGURACIÓN y ejecuta:
    python comparar_velocidades_carrito.py

Requiere pandas (disponible en el entorno científico habitual).
La distancia d se mide SOBRE el riel, desde la liberación hasta una misma
marca de referencia. No incluye rozamiento, rotación de ruedas ni frenado
magnético; por ello, las velocidades calculadas son predicciones ideales.
"""

from math import radians, sin, sqrt

import pandas as pd


# ======================================================================
# CONFIGURACIÓN: MODIFICA ESTOS VALORES
# ======================================================================
G = 9.81                          # aceleración gravitacional, m/s²
NUM_ENSAYOS = 6                  # número de mediciones por serie
VELOCIDAD_INICIAL_M_S = 0.0      # 0 si se suelta el carrito sin empujarlo

# A) Variar distancia, manteniendo fija la inclinación del riel
ANGULO_FIJO_GRADOS = 3.0
DISTANCIA_INICIAL_CM = 15.0
PASOS_DISTANCIA_CM = [10.0, 5.0]  # una serie por cada paso indicado

# B) Variar inclinación, manteniendo fija la distancia de liberación
DISTANCIA_FIJA_CM = 50.0
ANGULO_INICIAL_GRADOS = 1.0
PASO_ANGULO_GRADOS = 1.0

# Opcional: límite REAL de recorrido hasta la marca de referencia.
# Usa None si todavía no lo han medido; NO equivale al largo total del riel.
DISTANCIA_MAXIMA_UTIL_CM = None  # ejemplo: 65.0

# Opcional: guardar los resultados en archivos CSV.
GUARDAR_CSV = False
# ======================================================================


def velocidad_ideal(distancia_cm: float, angulo_grados: float) -> float:
    """Calcula la rapidez (m/s) al recorrer 'distancia_cm' sobre el riel."""
    if distancia_cm < 0:
        raise ValueError("La distancia no puede ser negativa.")
    if not 0 <= angulo_grados <= 90:
        raise ValueError("El ángulo debe estar entre 0° y 90°.")
    distancia_m = distancia_cm / 100.0
    aceleracion = G * sin(radians(angulo_grados))
    return sqrt(VELOCIDAD_INICIAL_M_S**2 + 2 * aceleracion * distancia_m)


def tabla_por_distancia(paso_cm: float) -> pd.DataFrame:
    """Serie con ángulo fijo y distancia creciente."""
    distancias = [DISTANCIA_INICIAL_CM + i * paso_cm for i in range(NUM_ENSAYOS)]
    velocidades = [velocidad_ideal(d, ANGULO_FIJO_GRADOS) for d in distancias]
    tabla = pd.DataFrame({
        "Ensayo": range(1, NUM_ENSAYOS + 1),
        "Distancia (cm)": distancias,
        "Ángulo (°)": [ANGULO_FIJO_GRADOS] * NUM_ENSAYOS,
        "Velocidad (m/s)": velocidades,
    })
    tabla["Cambio de v (m/s)"] = tabla["Velocidad (m/s)"].diff()
    return tabla


def tabla_por_angulo() -> pd.DataFrame:
    """Serie con distancia fija e inclinación creciente."""
    angulos = [ANGULO_INICIAL_GRADOS + i * PASO_ANGULO_GRADOS
               for i in range(NUM_ENSAYOS)]
    velocidades = [velocidad_ideal(DISTANCIA_FIJA_CM, a) for a in angulos]
    tabla = pd.DataFrame({
        "Ensayo": range(1, NUM_ENSAYOS + 1),
        "Distancia (cm)": [DISTANCIA_FIJA_CM] * NUM_ENSAYOS,
        "Ángulo (°)": angulos,
        "Velocidad (m/s)": velocidades,
    })
    tabla["Cambio de v (m/s)"] = tabla["Velocidad (m/s)"].diff()
    return tabla


def imprimir_tabla(titulo: str, tabla: pd.DataFrame) -> None:
    """Muestra la serie y su variación relativa entre el primer y último ensayo."""
    print(f"\n{titulo}")
    print("-" * len(titulo))
    print(tabla.to_string(index=False, float_format=lambda x: f"{x:.3f}", na_rep="—"))
    inicial = tabla["Velocidad (m/s)"].iloc[0]
    final = tabla["Velocidad (m/s)"].iloc[-1]
    if inicial > 0:
        print(f"Variación del primer al último ensayo: {final - inicial:.3f} m/s "
              f"({100 * (final / inicial - 1):.1f} %)")
    else:
        print(f"Variación del primer al último ensayo: {final - inicial:.3f} m/s")


def main() -> None:
    if NUM_ENSAYOS < 1:
        raise ValueError("NUM_ENSAYOS debe ser al menos 1.")
    if not PASOS_DISTANCIA_CM or any(p <= 0 for p in PASOS_DISTANCIA_CM):
        raise ValueError("PASOS_DISTANCIA_CM debe contener pasos positivos.")
    if PASO_ANGULO_GRADOS <= 0:
        raise ValueError("PASO_ANGULO_GRADOS debe ser positivo.")

    print("COMPARACIÓN IDEAL: CARRITO SOBRE PLANO INCLINADO")
    print("v = sqrt(v0² + 2*g*d*sin(theta))")
    print(f"g = {G} m/s² | v0 = {VELOCIDAD_INICIAL_M_S} m/s | "
          f"ensayos por serie = {NUM_ENSAYOS}")
    print("d es la distancia recorrida sobre el riel hasta la misma referencia.")

    tablas = {}
    for paso in PASOS_DISTANCIA_CM:
        nombre = f"Distancia, pasos de {paso:g} cm"
        tabla = tabla_por_distancia(paso)
        imprimir_tabla(f"A) {nombre} (ángulo fijo = {ANGULO_FIJO_GRADOS:g}°)", tabla)
        tablas[f"distancia_{paso:g}cm"] = tabla

    tabla_angulo = tabla_por_angulo()
    imprimir_tabla(f"B) Ángulo, pasos de {PASO_ANGULO_GRADOS:g}° "
                  f"(distancia fija = {DISTANCIA_FIJA_CM:g} cm)", tabla_angulo)
    tablas["angulo"] = tabla_angulo

    if DISTANCIA_MAXIMA_UTIL_CM is not None:
        for nombre, tabla in tablas.items():
            distancia_maxima = tabla["Distancia (cm)"].max()
            if distancia_maxima > DISTANCIA_MAXIMA_UTIL_CM:
                print(f"\nAVISO: la serie {nombre} requiere {distancia_maxima:g} cm; "
                      f"supera los {DISTANCIA_MAXIMA_UTIL_CM:g} cm útiles indicados.")

    if GUARDAR_CSV:
        for nombre, tabla in tablas.items():
            ruta = f"velocidades_{nombre}.csv"
            tabla.to_csv(ruta, index=False, encoding="utf-8-sig")
            print(f"CSV guardado: {ruta}")

    print("\nNota: son velocidades teóricas; para el laboratorio "
          "conviene medir la velocidad real.")


if __name__ == "__main__":
    main()
