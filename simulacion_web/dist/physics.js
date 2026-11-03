/* Modelo lateral con captadora circular de vueltas coincidentes, en unidades SI.
 * La fábrica autocontenida permite ejecutarlo en un Worker incluso desde file://.
 */
function createPhysics() {
  const defaults = Object.freeze({angulo:10, campo_mT:1, radio_cm:15, separacion_cm:15,
    vueltas:50, radio_captadora_cm:4, resistencia:1, carga:1000, sonda:1});
  const G=9.81, L=1.5, C=.75;
  const radialCache=new Map(), fluxCache=new Map();
  function validate(p) {
    if (!Object.keys(defaults).every(k=>Number.isFinite(p[k]))) throw Error('Completa todos los parámetros con números finitos.');
    if(p.angulo<0 || p.angulo>60) throw Error('La inclinación debe estar entre 0° y 60°.');
    if(p.campo_mT<0 || p.resistencia<0 || p.carga<=0) throw Error('Campo y resistencia propia ≥ 0; carga > 0.');
    if(p.radio_cm<2 || p.radio_cm>80 || p.separacion_cm<2 || p.separacion_cm>100) throw Error('Radio: 2–80 cm. Separación: 2–100 cm.');
    if(!Number.isInteger(p.vueltas) || p.vueltas<1) throw Error('Las vueltas deben ser un entero positivo.');
    if(p.radio_captadora_cm<0.1 || p.radio_captadora_cm>40) throw Error('El radio de la captadora debe estar entre 0,1 y 40 cm.');
    if(![1,10].includes(p.sonda)) throw Error('La sonda debe ser ×1 o ×10.');
  }
  function cache(map,key,value,limit=8) {
    if(map.size>=limit) map.delete(map.keys().next().value);
    map.set(key,value); return value;
  }
  function interp(grid,x,start,step) {
    const q=Math.max(0,Math.min(grid.length-1,(x-start)/step));
    const i=Math.min(grid.length-2,Math.floor(q)), f=q-i;
    return grid[i]*(1-f)+grid[i+1]*f;
  }
  function radial(p) {
    const key=[p.radio_cm,p.separacion_cm].join(',');
    if(radialCache.has(key)) return radialCache.get(key);
    const R=p.radio_cm/100, q=p.separacion_cm/(2*p.radio_cm), norm=(1+q*q)**1.5;
    const b=new Float64Array(4101), cos=new Float64Array(192);
    for(let j=0;j<192;j++) cos[j]=Math.cos((j+.5)*2*Math.PI/192);
    for(let i=0;i<b.length;i++) {
      const u=i*.0005/R; let sum=0;
      for(let j=0;j<192;j++) {
        const den=1+u*u+q*q-2*u*cos[j];
        sum+=(1-u*cos[j])/(den*Math.sqrt(den));
      }
      b[i]=norm*sum/192;
    }
    b[0]=1;
    return cache(radialCache,key,b);
  }
  // Gauss–Legendre radial y promedio angular: dS = r dr dφ.
  function diskQuadrature(radius) {
    const points=[], order=24, angles=96;
    for(let i=0;i<order;i++) {
      let z=Math.cos(Math.PI*(i+.75)/(order+.5)), derivative;
      for(let iter=0;iter<30;iter++) {
        let prev=1, current=z;
        for(let j=2;j<=order;j++) {const next=((2*j-1)*z*current-(j-1)*prev)/j;prev=current;current=next;}
        derivative=order*(z*current-prev)/(z*z-1);
        const step=current/derivative; z-=step;
        if(Math.abs(step)<1e-14) break;
      }
      const r=radius*(z+1)/2, weight=2/((1-z*z)*derivative*derivative);
      for(let j=0;j<angles;j++) {
        const angle=2*Math.PI*(j+.5)/angles;
        points.push([r*Math.cos(angle),r*Math.sin(angle),weight*radius/2*r*2*Math.PI/angles]);
      }
    }
    return points;
  }
  function fluxTable(p) {
    const key=[p.radio_cm,p.separacion_cm,p.radio_captadora_cm].join(',');
    if(fluxCache.has(key)) return fluxCache.get(key);
    const b=radial(p), points=diskQuadrature(p.radio_captadora_cm/100);
    const flux=new Float64Array(3801), der=new Float64Array(3801);
    for(let k=0;k<flux.length;k++) {
      const x=-.2+k*.0005-C; let sum=0;
      for(const [u,v,weight] of points) sum+=weight*interp(b,Math.hypot(x+u,v),0,.0005);
      flux[k]=sum; // flujo por vuelta y por tesla de campo central
    }
    for(let k=1;k<flux.length-1;k++) der[k]=(flux[k+1]-flux[k-1])/.001;
    der[0]=(-3*flux[0]+4*flux[1]-flux[2])/.001;
    const n=flux.length; der[n-1]=(3*flux[n-1]-4*flux[n-2]+flux[n-3])/.001;
    return cache(fluxCache,key,{flux,der});
  }
  function simulate(p={...defaults},samples=3001) {
    validate(p);
    if(!Number.isInteger(samples) || samples<101) throw Error('Se necesitan al menos 101 muestras.');
    const table=fluxTable(p), b=radial(p), a=G*Math.sin(p.angulo*Math.PI/180);
    const end=a>0?Math.sqrt(2*L/a):3;
    const effective=1/(1/p.carga+1/(1e6*p.sonda));
    const names=['t','s','v','campo','flujo','dflujo_ds','fem','voltaje','corriente','entrada_BNC'];
    const d=Object.fromEntries(names.map(k=>[k,new Float64Array(samples)]));
    let peak=0,femPeak=0,min=Infinity,max=-Infinity;
    for(let i=0;i<samples;i++) {
      const t=end*i/(samples-1), s=.5*a*t*t, v=a*t;
      const phi=interp(table.flux,s,-.2,.0005)*p.campo_mT*.001;
      const der=interp(table.der,s,-.2,.0005)*p.campo_mT*.001;
      const emf=-p.vueltas*der*v, current=emf/(p.resistencia+effective), voltage=current*effective;
      d.t[i]=t; d.s[i]=s; d.v[i]=v; d.flujo[i]=phi; d.dflujo_ds[i]=der;
      d.campo[i]=interp(b,Math.abs(s-C),0,.0005)*p.campo_mT*.001;
      d.fem[i]=emf; d.corriente[i]=current; d.voltaje[i]=voltage; d.entrada_BNC[i]=voltage/p.sonda;
      peak=Math.max(peak,Math.abs(voltage)); femPeak=Math.max(femPeak,Math.abs(emf));
      min=Math.min(min,voltage); max=Math.max(max,voltage);
    }
    const dist=Math.min(1.8*p.radio_cm/100,C*.9);
    const window=a>0?Math.sqrt(2*(C+dist)/a)-Math.sqrt(2*(C-dist)/a):0;
    const perfil_s=new Float64Array(601), perfil_campo=new Float64Array(601), perfil_flujo=new Float64Array(601);
    for(let i=0;i<601;i++) {
      const s=L*i/600; perfil_s[i]=s;
      perfil_campo[i]=interp(b,Math.abs(s-C),0,.0005)*p.campo_mT*.001;
      perfil_flujo[i]=interp(table.flux,s,-.2,.0005)*p.campo_mT*.001;
    }
    return {...d, perfil_s, perfil_campo, perfil_flujo, end, a, voltaje_pico:peak, voltaje_pp:max-min, fem_pico:femPeak,
      rapidez_centro:Math.sqrt(2*a*C), ventana_senal:window, div_normal:peak/p.sonda/.005,
      div_expandido:peak/p.sonda/.001, centro_t:a>0?Math.sqrt(2*C/a):end/2};
  }
  return {defaults,validate,simulate,radial,interp};
}
if(typeof module!=='undefined') module.exports=createPhysics;
