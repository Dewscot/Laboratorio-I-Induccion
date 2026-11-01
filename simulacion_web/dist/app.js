/* Interfaz sin dependencias: los cálculos se ejecutan fuera del hilo de dibujo. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id), physics=createPhysics();
  const scene=$('scene'), plot=$('plot'), form=$('parameters');
  const sceneCtx=scene.getContext('2d'), plotCtx=plot.getContext('2d');
  const sceneBase=document.createElement('canvas'), plotBase=document.createElement('canvas');
  const fmt=(x,n=2)=>Number(x).toLocaleString('es-CL',{minimumFractionDigits:n,maximumFractionDigits:n});
  let params={...physics.defaults}, data=null, running=false, currentTime=0, lastFrame=null;
  let view='perspective', plotMode='signal', revision=0, debounce, dirty=true, failedWorker=false;
  let sceneLayout=null, plotLayout=null, worker=null, workerURL=null;
  const state={};

  // Un Worker de Blob mantiene el funcionamiento sin conexión y también en file://.
  try {
    workerURL=URL.createObjectURL(new Blob([
      'const physics=('+createPhysics.toString()+')();\n'+
      'onmessage=({data:m})=>{const start=performance.now();try {'+
      'const d=physics.simulate(m.p);postMessage({id:m.id,p:m.p,d,ms:performance.now()-start});'+
      '}catch(e){postMessage({id:m.id,error:e.message});}};'
    ],{type:'text/javascript'}));
    worker=new Worker(workerURL);
    worker.onmessage=event=>receive(event.data);
    worker.onerror=()=>{
      worker.terminate(); worker=null; failedWorker=true;
      URL.revokeObjectURL(workerURL); workerURL=null;
      compute(readParams());
    };
  } catch { failedWorker=true; if(workerURL) URL.revokeObjectURL(workerURL); }

  function readParams() {
    return Object.fromEntries(Object.keys(physics.defaults).map(k=>[k,form.elements[k].value===''?NaN:Number(form.elements[k].value)]));
  }
  function showError(message) {
    $('error').textContent=message; $('error').hidden=!message;
    $('play').disabled=!!message || !data; $('export').disabled=!!message || !data;
  }
  function setRunning(value) {
    running=value; lastFrame=null;
    $('play').textContent=running?'Ⅱ Pausar':currentTime>=data?.end?'↻ Repetir':'▶ Iniciar';
    dirty=true; requestFrame();
  }
  function compute(p) {
    const id=++revision;
    setRunning(false);
    try { physics.validate(p); } catch(e) {showError(e.message); $('compute-status').textContent='Revisa los parámetros'; return;}
    showError(''); $('compute-status').textContent='Calculando…';
    $('play').disabled=true; $('export').disabled=true;
    if(worker) worker.postMessage({id,p});
    else setTimeout(()=>{
      if(id!==revision) return;
      const start=performance.now();
      try {receive({id,p,d:physics.simulate(p),ms:performance.now()-start});}
      catch(e) {receive({id,error:e.message});}
    },0);
  }
  function receive(message) {
    if(message.id!==revision) return;
    if(message.error) {showError(message.error); $('compute-status').textContent='No se pudo calcular'; return;}
    const fraction=data?currentTime/data.end:0;
    params=message.p; data=message.d; currentTime=fraction*data.end;
    showError('');
    $('peak').innerHTML=fmt(data.voltaje_pico*1000,3)+'<em>mV</em>';
    $('pp').textContent=fmt(data.voltaje_pp*1000,3)+' mV pico a pico';
    $('speed').innerHTML=fmt(data.rapidez_centro)+'<em>m/s</em>';
    $('divisions').innerHTML=fmt(data.div_expandido)+'<em>div</em>';
    $('division-note').textContent=`Sonda ×${params.sonda} · 1 mV/div con Y×5`;
    $('helmholtz-note').textContent=params.radio_cm===params.separacion_cm?'D = R · configuración de Helmholtz':'D ≠ R · par de bobinas circulares';
    $('compute-status').textContent=`Actualizado · ${Math.round(message.ms)} ms${failedWorker?' · modo compatible':''}`;
    updatePositionUI(); buildScene(); buildPlot();
    dirty=true; requestFrame();
    // Punto de inspección para verificar la interfaz sin exponer datos externos.
    state.params=params; state.data=data;
  }
  function updatePositionUI() {
    $('timeline').value=data?currentTime/data.end*1000:0;
    $('time-label').textContent=fmt(currentTime,3)+' s';
  }
  function resize(canvas,buffer) {
    const rect=canvas.getBoundingClientRect(), ratio=Math.min(window.devicePixelRatio||1,2);
    canvas.width=buffer.width=Math.max(1,Math.round(rect.width*ratio));
    canvas.height=buffer.height=Math.max(1,Math.round(rect.height*ratio));
    return {w:rect.width,h:rect.height,ratio};
  }
  function path(ctx,points,color,width=1,close=false) {
    if(!points.length) return;
    ctx.beginPath(); points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));
    if(close) ctx.closePath(); ctx.strokeStyle=color; ctx.lineWidth=width; ctx.stroke();
  }
  function arrow(ctx,from,to,color,width=1.4) {
    path(ctx,[from,to],color,width);
    const a=Math.atan2(to[1]-from[1],to[0]-from[0]), size=5;
    path(ctx,[[to[0]-size*Math.cos(a-.5),to[1]-size*Math.sin(a-.5)],to,
      [to[0]-size*Math.cos(a+.5),to[1]-size*Math.sin(a+.5)]],color,width);
  }
  function buildScene() {
    if(!data) return;
    const dims=resize(scene,sceneBase),{w,h,ratio}=dims, ctx=sceneBase.getContext('2d');
    ctx.setTransform(ratio,0,0,ratio,0,0);
    ctx.fillStyle='#102d2b'; ctx.fillRect(0,0,w,h);
    const theta=params.angulo*Math.PI/180, R=params.radio_cm/100, D=params.separacion_cm/100;
    const raw=([x,y,z])=>view==='top'?[x,y]:[.94*x+.65*y, .11*x+.42*y-.88*z];
    const bounds=[[-.82,0,0],[.82,0,0]];
    for(const side of [-1,1]) for(let i=0;i<64;i++) bounds.push([R*Math.cos(i*Math.PI/32),side*D/2,R*Math.sin(i*Math.PI/32)]);
    const e=[Math.cos(theta),0,-Math.sin(theta)], n=[Math.sin(theta),0,Math.cos(theta)];
    for(const end of [-.75,.75]) for(const u of [-1,1]) for(const v of [-1,1]) {
      bounds.push(e.map((v0,k)=>(end+u*params.largo_cm/200)*v0+v*params.ancho_cm/200*n[k]));
    }
    const coords=bounds.map(raw), xs=coords.map(p=>p[0]), ys=coords.map(p=>p[1]);
    const minX=Math.min(...xs),maxX=Math.max(...xs), minY=Math.min(...ys),maxY=Math.max(...ys);
    const scale=Math.min((w-80)/(maxX-minX),(h-76)/Math.max(.25,maxY-minY));
    const project=p=>{const q=raw(p);return [w/2+(q[0]-(minX+maxX)/2)*scale,h/2+(q[1]-(minY+maxY)/2)*scale];};
    sceneLayout={...dims,project,e,n};
    // Grille discrète dans le plan horizontal, sans suggérer un champ uniforme.
    for(let x=-.9;x<=.91;x+=.15) path(ctx,[project([x,-.4,-.2]),project([x,.4,-.2])],'#1b3b34',.7);
    for(let y=-.4;y<=.41;y+=.1) path(ctx,[project([-.9,y,-.2]),project([.9,y,-.2])],'#1b3b34',.7);
    function coil(side) {
      for(let turn=-1;turn<=1;turn++) {
        const points=[];
        for(let i=0;i<=128;i++) {
          const a=i*Math.PI/64;
          points.push(project([(R+turn*.004)*Math.cos(a),side*D/2,(R+turn*.004)*Math.sin(a)]));
        }
        path(ctx,points,side<0?'#6a9d8d':'#91bc9d',turn===0?2.2:1);
      }
      const anchor=project([0,side*D/2,-R]);
      path(ctx,[anchor,[anchor[0],anchor[1]+12]],'#517f69',2);
      path(ctx,[[anchor[0]-9,anchor[1]+12],[anchor[0]+9,anchor[1]+12]],'#517f69',2);
    }
    coil(-1);
    // Deux rails parallèles, entre les deux bobines, jamais sur leur axe.
    for(const y of [-.024,.024]) {
      path(ctx,[-.75,.75].map(u=>project([u*e[0],y,u*e[2]])),'#8baba0',2.1);
    }
    for(let u=-.75;u<=.76;u+=.1) path(ctx,[project([u*e[0],-.033,u*e[2]]),project([u*e[0],.033,u*e[2]])],'#496b5c',1);
    // Les flèches indiquent le sens local au centre, pas un volume uniforme.
    for(const x of [-R*.4,0,R*.4]) arrow(ctx,project([x,-D*.31,0]),project([x,D*.31,0]),'#6cc6a4',1.2);
    coil(1);
    ctx.font='10px system-ui'; ctx.textAlign='center';
    for(const side of [-1,1]) {
      const anchor=project([0,side*D/2,R]);
      ctx.fillStyle='#9fbdac'; ctx.fillText(`Bobina ${side<0?'1':'2'}`,anchor[0]+side*14,anchor[1]-12);
    }
    ctx.textAlign='left'; ctx.fillStyle='#8ad3b0'; ctx.fillText('B transversal',20,24);
    ctx.fillStyle='#7a9c89';ctx.font='9px system-ui';
    ctx.fillText(view==='top'?'Vista superior · espira vista de canto':'Espira en el plano vertical del riel',20,h-12);
    const start=project([-.75*e[0],0,-.75*e[2]]), end=project([.75*e[0],0,.75*e[2]]);
    ctx.fillStyle='#9cb7a7';ctx.textAlign='center';ctx.fillText('0 m',start[0],start[1]+24);ctx.fillText('1,50 m',end[0],end[1]+24);
  }
  function drawScene() {
    if(!sceneLayout) return;
    const {ratio,project,e,n,w}=sceneLayout, ctx=sceneCtx;
    ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(sceneBase,0,0);
    ctx.setTransform(ratio,0,0,ratio,0,0);
    const s=.5*data.a*currentTime**2, center=s-.75;
    const loop=[];
    for(const [u,v] of [[-1,-1],[1,-1],[1,1],[-1,1]]) loop.push(project(e.map((v0,k)=>(center+u*params.largo_cm/200)*v0+v*params.ancho_cm/200*n[k])));
    ctx.beginPath(); loop.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();
    ctx.fillStyle='#d9a16516';ctx.fill();ctx.strokeStyle='#edb071';ctx.lineWidth=2.7;ctx.stroke();
    const c=project(e.map(v=>center*v));
    ctx.beginPath();ctx.arc(c[0],c[1],3.8,0,2*Math.PI);ctx.fillStyle='#f0c290';ctx.fill();
    ctx.textAlign='right';ctx.font='10px ui-monospace,monospace';ctx.fillStyle='#c3d8c6';
    ctx.fillText(`s = ${fmt(s)} m   v = ${fmt(data.a*currentTime)} m/s`,w-20,24);
  }
  function buildPlot() {
    if(!data) return;
    const dims=resize(plot,plotBase),{w,h,ratio}=dims, ctx=plotBase.getContext('2d');
    const scope=plotMode==='scope';
    $('scope-controls').hidden=!scope;
    let x=data.t,series=[],xmin=0,xmax=data.end,ymin,ymax,xLabel='Tiempo (s)',yLabel='mV';
    if(plotMode==='signal') {
      series=[{y:data.fem,k:1000,color:'#c88a4e',dash:[5,4]},{y:data.voltaje,k:1000,color:'#278a6c'}];
      ymax=Math.max(.002,data.fem_pico*1000*1.18);ymin=-ymax;
      $('plot-key').innerHTML='<span class="key-line orange"></span> Fem <span class="key-line teal"></span> Voltaje en la carga';
      $('plot-caption').textContent='Tensiones calculadas durante todo el recorrido. La línea vertical sigue a la espira.';
    } else if(plotMode==='field' || plotMode==='flux') {
      x=data.perfil_s;xmax=1.5;xLabel='Posición sobre el riel (m)';
      const field=plotMode==='field',values=field?data.perfil_campo:data.perfil_flujo,k=field?1000:1e6;
      series=[{y:values,k,color:field?'#528d80':'#ae8a59'}];
      const lo=Math.min(...values)*k,hi=Math.max(...values)*k,pad=Math.max((hi-lo)*.13,field?.0001:.001);
      ymin=Math.min(0,lo)-pad;ymax=hi+pad;yLabel=field?'mT':'µWb';
      $('plot-key').textContent=field?'Componente transversal B en el plano medio':'Flujo magnético por vuelta';
      $('plot-caption').textContent=field?'El campo varía suavemente; puede cambiar de signo lejos del centro por su retorno.':'Integral del campo sobre el área de la espira. La fem depende de cómo cambia este flujo en el tiempo.';
    } else if(plotMode==='position') {
      series=[{y:data.s,k:1,color:'#50859a'}];ymin=0;ymax=1.6;yLabel='m';
      $('plot-key').textContent='Posición del centro de la espira';
      $('plot-caption').textContent='Partida desde el reposo: s = ½ g sen(θ) t². A 0° la espira permanece detenida.';
    } else {
      const tdiv=Number($('tdiv').value)/1000, vdiv=Number($('vdiv').value);
      xmin=data.centro_t-5*tdiv;xmax=xmin+10*tdiv;ymin=-4*vdiv;ymax=4*vdiv;
      series=[{y:data.entrada_BNC,k:1000,color:'#80d9a3'}];
      $('plot-key').textContent=`CH I · DC · sonda ×${params.sonda} · tensión en el BNC`;
      const clipped=data.voltaje_pico*1000/params.sonda>4*vdiv;
      const cutWindow=xmin>0 || xmax<data.end;
      $('plot-caption').textContent=`Referencia de escala: ${fmt(data.voltaje_pico*1000/params.sonda/vdiv)} div de pico. ${clipped?'La señal excede la altura de pantalla. ':''}${cutWindow?'Se muestra una ventana centrada en el cruce. ':''}El ruido y el disparo deben comprobarse en el instrumento.`;
    }
    const left=58,right=18,top=28,bottom=37, pw=Math.max(1,w-left-right),ph=h-top-bottom;
    const X=v=>left+(v-xmin)/(xmax-xmin)*pw,Y=v=>top+(ymax-v)/(ymax-ymin)*ph;
    plotLayout={...dims,X,Y,xmin,xmax,ymin,ymax,left,top,pw,ph,spatial:['field','flux'].includes(plotMode),scope};
    ctx.setTransform(ratio,0,0,ratio,0,0);ctx.fillStyle=scope?'#102e29':'#ffffff';ctx.fillRect(0,0,w,h);
    ctx.font='9px system-ui';ctx.textAlign='right';ctx.fillStyle=scope?'#7fa48c':'#9aa69c';ctx.fillText(yLabel,left-8,14);
    const nx=scope?10:5, ny=scope?8:4;
    for(let j=0;j<=ny;j++) {
      const val=ymin+(ymax-ymin)*j/ny, yy=Y(val);
      path(ctx,[[left,yy],[w-right,yy]],scope?'#27493b':'#edf0e9',.8);
      ctx.fillStyle=scope?'#7fa48c':'#9aa69c';ctx.textAlign='right';ctx.fillText(fmt(val,Math.max(Math.abs(ymin),Math.abs(ymax))<.01?4:2),left-8,yy+3);
    }
    for(let j=0;j<=nx;j++) {
      const val=xmin+(xmax-xmin)*j/nx, xx=X(val);
      path(ctx,[[xx,top],[xx,h-bottom]],scope?'#27493b':'#edf0e9',.8);
      if(!scope || j%2===0) {ctx.fillStyle=scope?'#7fa48c':'#9aa69c';ctx.textAlign='center';ctx.fillText(fmt(val,2),xx,h-bottom+17);}
    }
    ctx.textAlign='center';ctx.fillStyle=scope?'#7fa48c':'#9aa69c';ctx.fillText(xLabel,left+pw/2,h-5);
    if(ymin<0 && ymax>0) path(ctx,[[left,Y(0)],[w-right,Y(0)]],scope?'#486e53':'#ced9ce',1);
    ctx.save();ctx.beginPath();ctx.rect(left,top,pw,ph);ctx.clip();
    for(const line of series) {
      ctx.setLineDash(line.dash||[]);
      path(ctx,Array.from(x,(val,i)=>[X(val),Y(line.y[i]*line.k)]),line.color,scope?1.6:1.9);
    }
    ctx.setLineDash([]);ctx.restore();
  }
  function drawPlot() {
    if(!plotLayout) return;
    const ctx=plotCtx,{ratio,X,left,top,pw,ph,spatial,scope}=plotLayout;
    ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(plotBase,0,0);
    const val=spatial?.5*data.a*currentTime**2:currentTime, xx=X(val);
    if(xx<left || xx>left+pw) return;
    ctx.setTransform(ratio,0,0,ratio,0,0);
    ctx.setLineDash([3,4]);path(ctx,[[xx,top],[xx,top+ph]],scope?'#c0d9ab':'#98ad9a',1);ctx.setLineDash([]);
    ctx.fillStyle=scope?'#c0d9ab':'#617c68';ctx.beginPath();ctx.moveTo(xx-3,top);ctx.lineTo(xx+3,top);ctx.lineTo(xx,top+5);ctx.fill();
  }
  let framePending=false;
  function requestFrame() {if(!framePending) {framePending=true;requestAnimationFrame(frame);}}
  function frame(timestamp) {
    framePending=false;
    if(running && data) {
      if(lastFrame!==null) currentTime=Math.min(data.end,currentTime+(timestamp-lastFrame)/1000*Number($('rate').value));
      lastFrame=timestamp;dirty=true;updatePositionUI();
      if(currentTime>=data.end) {running=false;lastFrame=null;$('play').textContent='↻ Repetir';}
    }
    if(dirty && data) {drawScene();drawPlot();dirty=false;}
    if(running) requestFrame();
  }
  form.addEventListener('submit',e=>e.preventDefault());
  form.addEventListener('input',event=>{
    if(event.target===$('angulo-slider')) {
      // El deslizador permite ajustes rápidos; el campo numérico conserva
      // todos los decimales introducidos directamente por el usuario.
      form.elements.angulo.value=Number(Number($('angulo-slider').value).toFixed(2));
      $('angulo-slider').value=form.elements.angulo.value;
    } else if(event.target===form.elements.angulo && form.elements.angulo.value!=='') {
      const angle=Number(form.elements.angulo.value);
      if(Number.isFinite(angle) && angle>=0 && angle<=60) $('angulo-slider').value=angle;
    }
    clearTimeout(debounce);setRunning(false);
    // Invalida ya cualquier respuesta pendiente al comenzar una nueva edición.
    revision++;$('play').disabled=true;$('export').disabled=true;
    debounce=setTimeout(()=>compute(readParams()),90);
  });
  $('reset').onclick=()=>{
    clearTimeout(debounce);
    for(const [key,val] of Object.entries(physics.defaults)) form.elements[key].value=val;
    $('angulo-slider').value=physics.defaults.angulo;currentTime=0;compute(readParams());
  };
  $('play').onclick=()=>{if(!data)return;if(currentTime>=data.end)currentTime=0;setRunning(!running);};
  $('rewind').onclick=()=>{currentTime=0;setRunning(false);updatePositionUI();};
  $('timeline').oninput=()=>{if(!data)return;currentTime=Number($('timeline').value)/1000*data.end;setRunning(false);updatePositionUI();};
  document.querySelectorAll('[data-view]').forEach(button=>button.onclick=()=>{
    view=button.dataset.view;
    document.querySelectorAll('[data-view]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
    buildScene();dirty=true;requestFrame();
  });
  document.querySelectorAll('[data-plot]').forEach(button=>button.onclick=()=>{
    plotMode=button.dataset.plot;
    document.querySelectorAll('[data-plot]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
    buildPlot();dirty=true;requestFrame();
  });
  for(const key of ['vdiv','tdiv']) $(key).onchange=()=>{buildPlot();dirty=true;requestFrame();};
  $('scope-fit').onclick=()=>{
    if(!data)return;
    const peak=data.voltaje_pico*1000/params.sonda, vertical=[1,5,10,20,50,100,200,500];
    let v=vertical.find(x=>x>=peak/3)||500;
    // Se conservan las escalas calibradas 1–2–5 del instrumento.
    if(peak/3>500) {
      const exponent=Math.floor(Math.log10(peak/3));
      v=[1,2,5,10].map(m=>m*10**exponent).find(scale=>scale>=peak/3);
      if(!Array.from($('vdiv').options).some(option=>Number(option.value)===v)) $('vdiv').add(new Option(`${v} mV/div`,v));
    }
    $('vdiv').value=v;
    $('tdiv').value=[10,20,50,100].find(x=>x/1000>=data.ventana_senal/8)||100;
    buildPlot();dirty=true;requestFrame();
  };
  $('export').onclick=()=>{
    if(!data)return;
    const keys=['t','s','v','campo','flujo','dflujo_ds','fem','voltaje','corriente','entrada_BNC'];
    const rows=['# SIMULACIÓN IDEAL; no son mediciones experimentales',
      '# Geometría: bobinas laterales; espira vertical longitudinal; riel centrado',
      '# Parámetros: '+JSON.stringify(params),
      't_s,s_m,v_m_s,B_transversal_T,flujo_por_vuelta_Wb,dPhi_ds_Wb_m,fem_V,voltaje_carga_V,corriente_A,entrada_BNC_V'];
    for(let i=0;i<data.t.length;i++) rows.push(keys.map(k=>data[k][i].toPrecision(12)).join(','));
    const url=URL.createObjectURL(new Blob([rows.join('\n')+'\n'],{type:'text/csv;charset=utf-8'}));
    const link=document.createElement('a');link.href=url;link.download=`induccion_lateral_${params.angulo}grados_${params.vueltas}vueltas.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  new ResizeObserver(()=>{if(data){buildScene();buildPlot();dirty=true;requestFrame();}}).observe(document.querySelector('main'));
  document.addEventListener('visibilitychange',()=>{lastFrame=null;});
  window.addEventListener('pagehide',event=>{if(!event.persisted){worker?.terminate();if(workerURL)URL.revokeObjectURL(workerURL);}});
  Object.defineProperty(window,'inductionSimulation',{value:state});
  compute(params);
})();
