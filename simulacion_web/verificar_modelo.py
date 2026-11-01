"""Contrasta el modelo JavaScript con la implementación NumPy del montaje lateral.

Ejecutar desde cualquier carpeta: python simulacion_web/verificar_modelo.py
Requiere NumPy y Node.js; no abre Matplotlib ni instala paquetes.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "Simulacion 2"))
from simulacion_induccion_helmholtz import Parametros, simular

CASOS = [
    {},
    {"angulo": 0},
    {"campo_mT": 0},
    {"angulo": 25, "vueltas": 40},
    {"sonda": 10, "carga": 100, "resistencia": 15},
    {"radio_cm": 20, "separacion_cm": 25, "largo_cm": 15, "ancho_cm": 8},
    {"angulo": 60, "campo_mT": 3, "vueltas": 1},
    {"radio_cm": 2, "separacion_cm": 2, "largo_cm": 1, "ancho_cm": 1},
]
CLAVES = ["t", "s", "v", "campo", "flujo", "dflujo_ds", "fem", "voltaje",
          "corriente", "entrada_BNC", "fem_pico", "voltaje_pico", "voltaje_pp",
          "rapidez_centro", "div_normal", "div_expandido", "ventana_senal"]

programa = r"""
const fs=require('node:fs');
const physics=require('./dist/physics.js')();
const {cases,keys}=JSON.parse(fs.readFileSync(0,'utf8'));
const results=cases.map(p=>{
  const d=physics.simulate({...physics.defaults,...p});
  return Object.fromEntries(keys.map(k=>[k,ArrayBuffer.isView(d[k])?Array.from(d[k]):d[k]]));
});
process.stdout.write(JSON.stringify(results));
"""
resultado = subprocess.run(["node", "-e", programa], cwd=ROOT,
                           input=json.dumps({"cases": CASOS, "keys": CLAVES}),
                           text=True, capture_output=True, check=True)
web = json.loads(resultado.stdout)
for i, (cambios, obtenido) in enumerate(zip(CASOS, web), 1):
    esperado = simular(Parametros(**cambios))
    for clave in CLAVES:
        np.testing.assert_allclose(obtenido[clave], esperado[clave], rtol=2e-8, atol=1e-11,
                                   err_msg=f"Caso {i}, {clave}")
    print(f"Caso {i}: OK · {cambios or 'parámetros iniciales'}")
print(f"{len(CASOS)} casos coinciden con Python; {len(CLAVES)} magnitudes por caso.")
