"""Pruebas automáticas de la simulación para bobinas A LOS LADOS del riel."""
import unittest
from dataclasses import replace

import numpy as np

from simulacion_induccion_helmholtz import (
    CENTRO_CAMPO, Parametros, campo_en_riel, flujo_y_derivada, simular
)


class TestHelmholtzTransversal(unittest.TestCase):
    def setUp(self):
        self.p = Parametros(angulo=15, vueltas=10)

    def test_campo_central_y_simetria(self):
        self.assertAlmostEqual(float(campo_en_riel(.75, self.p)), .001, places=9)
        dx = .13
        self.assertAlmostEqual(float(campo_en_riel(.75-dx, self.p)),
                               float(campo_en_riel(.75+dx, self.p)), places=10)

    def test_flujo_simetrico_derivada_antisimetrica(self):
        pts = np.array([.57, .63, .75, .87, .93])
        phi, derivada = flujo_y_derivada(pts, self.p)
        self.assertTrue(np.allclose(phi, phi[::-1], atol=1e-11))
        self.assertTrue(np.allclose(derivada, -derivada[::-1], atol=1e-10))
        self.assertAlmostEqual(derivada[2], 0, delta=1e-10)

    def test_fem_es_faraday(self):
        d = simular(self.p)
        self.assertTrue(np.allclose(d["fem"], -self.p.vueltas*d["dflujo_ds"]*d["v"], atol=1e-12))

    def test_fem_cambia_signo_al_cruzar_centro(self):
        d = simular(self.p)
        self.assertLess(d["pico_entrada"][0], 0)
        self.assertGreater(d["pico_salida"][0], 0)

    def test_campo_cero_no_induce(self):
        d = simular(replace(self.p, campo_mT=0))
        self.assertEqual(d["voltaje_pico"], 0)

    def test_angulo_cero_no_induce(self):
        d = simular(replace(self.p, angulo=0))
        self.assertEqual(d["voltaje_pico"], 0)

    def test_escala_por_vueltas(self):
        p2 = replace(self.p, vueltas=20)
        d1, d2 = simular(self.p), simular(p2)
        self.assertAlmostEqual(d2["voltaje_pico"]/d1["voltaje_pico"], 2, places=6)

    def test_escala_raiz_seno_angulo_al_cambiar_angulo(self):
        a, b = 8., 25.
        d1 = simular(replace(self.p, angulo=a))
        d2 = simular(replace(self.p, angulo=b))
        esperado = np.sqrt(np.sin(np.deg2rad(b))/np.sin(np.deg2rad(a)))
        self.assertAlmostEqual(d2["voltaje_pico"]/d1["voltaje_pico"], esperado, delta=.001)

    def test_campo_varia_suavemente(self):
        d = simular(self.p)
        s, b = d["s"], d["campo"]
        near = (s > .5) & (s < 1.)
        self.assertTrue(np.all(np.isfinite(b)))
        self.assertLess(np.max(np.abs(np.diff(b[near]))), .00003)


if __name__ == "__main__":
    unittest.main()
