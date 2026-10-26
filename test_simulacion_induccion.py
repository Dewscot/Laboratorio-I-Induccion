"""Comprobaciones físicas independientes: python -m unittest test_simulacion_induccion."""

from dataclasses import replace
import unittest

import numpy as np

from simulacion_induccion import G, LARGO_RIEL, Parametros, flujo_y_derivada, simular


class FisicaTest(unittest.TestCase):
    def test_movimiento_y_energia(self):
        p = Parametros()
        d = simular(p)
        self.assertAlmostEqual(d["s"][-1], LARGO_RIEL)
        np.testing.assert_allclose(d["v"]**2, 2 * G * np.sin(np.deg2rad(p.angulo)) * d["s"])

    def test_sin_movimiento_campo_o_flujo_normal(self):
        for p in [Parametros(angulo=0), Parametros(campo_mT=0), Parametros(direccion_B=-10)]:
            with self.subTest(p=p):
                np.testing.assert_array_equal(simular(p)["fem"], 0)

    def test_faraday_por_diferencias_finitas_del_flujo(self):
        # Comprobar también la cancelación cuando la espira es más larga que la zona.
        for p in [Parametros(vueltas=7), Parametros(vueltas=7, largo_cm=40, zona_cm=20)]:
            d = simular(p)
            h = 1e-7
            mas, _ = flujo_y_derivada(d["s"] + h, p)
            menos, _ = flujo_y_derivada(d["s"] - h, p)
            esperado = -p.vueltas * (mas - menos) / (2 * h) * d["v"]
            # Excluir los bordes, donde el modelo ideal no es diferenciable.
            _, dl = flujo_y_derivada(d["s"] - h, p)
            _, dr = flujo_y_derivada(d["s"] + h, p)
            interior = dl == dr
            np.testing.assert_allclose(d["fem"][interior], esperado[interior], atol=1e-11, rtol=1e-7)

    def test_integral_fem_recupera_cambio_flujo(self):
        p = Parametros(vueltas=10)
        d = simular(p, muestras=12001)
        entrada = d["s"] <= 0.75
        integral = np.trapezoid(d["fem"][entrada], d["t"][entrada])
        esperado = -p.vueltas * p.campo_mT * 1e-3 * p.ancho_cm * p.largo_cm * 1e-4 * np.cos(np.deg2rad(p.angulo))
        self.assertAlmostEqual(integral / esperado, 1, delta=0.002)
        self.assertAlmostEqual(np.trapezoid(d["fem"], d["t"]), 0, delta=abs(esperado) * 0.002)

    def test_escalas_y_resistencia_no_cambia_fem(self):
        p = Parametros()
        d = simular(p)
        for otro in [replace(p, vueltas=2), replace(p, campo_mT=2), replace(p, ancho_cm=20)]:
            np.testing.assert_allclose(simular(otro)["fem"], 2 * d["fem"])
        resistiva = simular(replace(p, resistencia=1000))
        np.testing.assert_array_equal(resistiva["fem"], d["fem"])
        self.assertLess(resistiva["voltaje_pico"], d["voltaje_pico"])

    def test_orientacion_fija_y_lenz(self):
        d = simular(Parametros(angulo=30))
        self.assertAlmostEqual(d["beta"], 30)
        self.assertLess(d["fem"].min(), 0)
        self.assertGreater(d["fem"].max(), 0)
        # Aceleración: el pulso de salida es más alto y más corto.
        self.assertGreater(d["fem"].max(), -d["fem"].min())
        self.assertLess(d["pulsos_ms"][1], d["pulsos_ms"][0])

    def test_carga_sonda_y_sensibilidad_hameg(self):
        p = Parametros(resistencia=1e5, carga=1e6, sonda=10)
        d = simular(p)
        r_paralelo = 1 / (1 / 1e6 + 1 / 10e6)
        np.testing.assert_allclose(d["voltaje"], d["fem"] * r_paralelo / (1e5 + r_paralelo))
        np.testing.assert_allclose(d["entrada_BNC"], d["voltaje"] / 10)
        self.assertAlmostEqual(d["div_expandido"], 5 * d["div_normal"])


if __name__ == "__main__":
    unittest.main()
