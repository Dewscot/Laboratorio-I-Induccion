"""Verifica la captadora circular con NumPy y Node (sin modificar archivos).

Referencia independiente: Biot–Savart con 768 segmentos y flujo integrado
por franjas cartesianas sobre el disco (Gauss–Legendre 96 × 96).
Ejecutar: python3 simulacion_web/verificar_modelo.py
"""
import json
from pathlib import Path
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent
CASOS = [{}, {"radio_captadora_cm": 8, "vueltas": 100},
         {"radio_captadora_cm": 15, "radio_cm": 20, "separacion_cm": 25},
         {"radio_captadora_cm": 0.1}, {"radio_captadora_cm": 40},
         {"radio_captadora_cm": 1, "radio_cm": 2, "separacion_cm": 2}]
programa = r"""
const assert=require('node:assert/strict');
const physics=require('./dist/physics.js')(), p={...physics.defaults};
const base=physics.simulate(p), twice=physics.simulate({...p,vueltas:100});
for(let i=0;i<base.t.length;i++) {
  assert.equal(twice.fem[i],2*base.fem[i]);
  assert.equal(twice.flujo[i],base.flujo[i]);
}
for(const changes of [{angulo:0},{campo_mT:0}])
  assert.equal(physics.simulate({...p,...changes}).voltaje_pico,0);
for(const changes of [{radio_captadora_cm:0},{radio_captadora_cm:41},{radio_captadora_cm:NaN},{vueltas:0},{vueltas:1.5}])
  assert.throws(()=>physics.simulate({...p,...changes}));
const large=physics.simulate({...p,radio_captadora_cm:8});
assert.ok(large.voltaje_pico>base.voltaje_pico);
const angled=physics.simulate({...p,angulo:30});
assert.ok(Math.abs(angled.voltaje_pico/base.voltaje_pico-Math.sqrt(.5/Math.sin(Math.PI/18)))<1e-10);
const cases=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(cases.map(c=>{
 const params={...p,...c}, d=physics.simulate(params);
 return {params,s:Array.from(d.perfil_s),flux:Array.from(d.perfil_flujo),peak:d.voltaje_pico, sample_s:Array.from(d.s).filter((_,i)=>i%50===0), derivative:Array.from(d.dflujo_ds).filter((_,i)=>i%50===0)};
})));
"""
result = subprocess.run(['node', '-e', programa], cwd=ROOT, input=json.dumps(CASOS),
                        capture_output=True, text=True, check=True)
for case in json.loads(result.stdout):
    p = case['params']
    radius, separation = p['radio_cm']/100, p['separacion_cm']/100
    r = p['radio_captadora_cm']/100
    # Campo independiente por Biot–Savart, con una malla más fina.
    rho = np.arange(0, 1.6 + 0.000125, 0.000125)
    cosine = np.cos((np.arange(768)+0.5)*2*np.pi/768)
    field = np.empty_like(rho)
    q = separation/(2*radius)
    for start in range(0,len(rho),256):
        u = rho[start:start+256,None]/radius
        den = 1+u*u+q*q-2*u*cosine
        field[start:start+256] = (1+q*q)**1.5*np.mean((1-u*cosine)/den**1.5,axis=1)
    nodes, weights = np.polynomial.legendre.leggauss(96)
    angle = nodes*np.pi/2
    x = r*np.sin(angle)[:,None]
    y = r*np.cos(angle)[:,None]*nodes[None,:]
    area_weights = r*r*np.cos(angle)[:,None]**2*np.pi/2*weights[:,None]*weights[None,:]
    selected = np.arange(0,601,10)
    def flux_at(s):
        b = np.interp(np.hypot(s-.75+x,y),rho,field)
        return np.sum(b*area_weights)*p['campo_mT']/1000
    expected_derivative = np.array([(flux_at(s+.0005)-flux_at(s-.0005))/.001 for s in case['sample_s']])
    derivative_error = np.max(np.abs(np.array(case['derivative'])-expected_derivative))/np.max(np.abs(expected_derivative))
    assert derivative_error < .005, (p, 'derivada', derivative_error)
    expected = []
    for s in np.array(case['s'])[selected]:
        b = np.interp(np.hypot(s-.75+x,y),rho,field)
        expected.append(np.sum(b*area_weights)*p['campo_mT']/1000)
    expected = np.array(expected)
    actual = np.array(case['flux'])[selected]
    relative_error = np.max(np.abs(actual-expected))/np.max(np.abs(expected))
    assert relative_error < 3e-4, (p, relative_error)
    print(f"r={p['radio_captadora_cm']} cm, N={p['vueltas']}: error de flujo {relative_error:.2e}; pico {case['peak']*1000:.4f} mV")
print('OK: referencia independiente, proporcionalidad con N, dependencia angular, campo/ángulo nulos y parámetros inválidos.')
