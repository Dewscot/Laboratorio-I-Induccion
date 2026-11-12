# Bitácora única — Experimento de inducción en plano inclinado

**Creación:** 1 de noviembre de 2026. **Última actualización:** 4 de noviembre de 2026.  
**Documento de trabajo:** desde esta fecha concentra las decisiones, el modelo, la instrumentación, los resultados y los pendientes. Se actualizará conforme avance el experimento.

## 1. Procedencia y forma de actualizar

Esta es la **única bitácora activa** del proyecto. Reúne las bitácoras del
osciloscopio (28-10) y la simulación web (01-11), la consulta sobre la bobina de
galletera (01-11) y los avances y aclaraciones del 03-11.

Los tres registros anteriores se conservan íntegros en un solo
[respaldo histórico ZIP](documentos/archivo/antecedentes_2026-11-03.zip).
Se retiraron sus copias sueltas de la raíz para evitar duplicación. El respaldo
conserva su redacción original y puede describir modelos ya reemplazados.

También se consultaron el [marco teórico](marco_teorico_experimento_plano_inclinado_faraday.md),
[main.pdf](main.pdf), el [README del proyecto](README.md) y las
[instrucciones del simulador](simulacion_web/README.md). Estos documentos cumplen
funciones distintas de la bitácora; las nuevas decisiones y avances se registran aquí.

Al actualizar:

1. Cambiar la fecha de última actualización y añadir una entrada fechada al historial.
2. Actualizar la sección correspondiente y los pendientes; conservar en el historial las decisiones reemplazadas y el motivo.
3. Distinguir entre **aclaración del montaje**, **supuesto**, **predicción simulada** y **medición real**. Registrar unidades e incertidumbres cuando haya mediciones.
4. Vincular los datos, fotografías, vídeos o archivos que respalden cada resultado.

## 2. Estado actual y objetivo

El experimento estudia la relación entre inclinación del riel, velocidad del carrito, variación de flujo y señal inducida en una captadora móvil:

\[
\theta\longrightarrow a\longrightarrow v\longrightarrow
\frac{d\Phi_B}{dt}\longrightarrow\mathcal E\longrightarrow V,\ I.
\]

El marco teórico original planteaba estudiar corriente inducida. La propuesta de `main.pdf`, leída el 03-11, toma como observable el máximo absoluto del voltaje respecto de la línea base: **U_pk = max |V(t) − V₀|**. Se propone compararlo con √sen θ y, si se mide la rapidez por vídeo, también con v. **El osciloscopio mide voltaje entre sus terminales**: para informar corriente se debe especificar la resistencia o el método de conversión. Falta concretar el circuito real y confirmar el protocolo de medición.

El 04-11 el usuario informó que, en el último laboratorio, el voltaje era demasiado pequeño para distinguirlo claramente del ruido y las interferencias. No se aportaron trazas, amplitudes, duración del pulso ni ajustes confirmados del osciloscopio. Los resultados del simulador son predicciones. Las verificaciones de software del 03-11 se detallan en el historial; no equivalen a una validación experimental.

## 3. Montaje y geometría de referencia

| Elemento | Estado documentado |
| --- | --- |
| Bobinas grandes | El usuario aclaró que están a los costados del riel, no arriba y abajo. |
| Campo del modelo | Dos anillos circulares fijos, con eje común transversal al avance y corrientes iguales del mismo sentido. |
| Captadora del modelo web | Circular, con vueltas coincidentes y sin núcleo; vertical en el plano longitudinal del riel, con normal transversal. Valores iniciales: unas 50 vueltas y radio medio de 4 cm, según el usuario. Orientación real en el carrito pendiente de confirmar. |
| Trayectoria del modelo | Centrada en el plano medio entre las bobinas. Pendiente de contrastar con el montaje. |
| Giro del riel | Se supone un pivote en el centro de las bobinas. Pendiente de confirmar. |
| Recorrido simulado | Riel de 1,50 m; centro de bobinas en \(s=0,75\ \mathrm m\). No equivale a una medida nueva del aparato. |

En esta geometría la captadora gira dentro del plano medio y su normal conserva la dirección transversal. **No corresponde añadir el factor \(\cos\theta\) del modelo anterior con campo vertical y espira paralela al riel.** Si la captadora real está acostada o el cruce no está centrado, debe revisarse el flujo.

El programa anterior, [simulacion_induccion.py](simulacion_induccion.py), se conserva como referencia de otra geometría, con campo uniforme de bordes definidos. La versión web se basa en el modelo lateral de [Simulación 2](Simulacion%202/simulacion_induccion_helmholtz.py), documentado en [SIMULACION_HELMHOLTZ.md](Simulacion%202/SIMULACION_HELMHOLTZ.md).

### Captadora provisional y preparación

- Datos aportados por el usuario: aproximadamente **50 vueltas**, **radio de 4 cm**
  (diámetro de 8 cm) y continuidad del alambre confirmada por él. No se informó
  el método de comprobación ni una resistencia medida.
- [Fotografía de la captadora](figuras/captadora%20provisional.jpeg): bobinado
  aproximadamente circular, deformable, sin núcleo visible. La foto no permite
  contar vueltas ni verificar dimensiones o aislamiento.
- Área aproximada por vuelta: **A = πr² ≈ 0,00503 m² = 50,3 cm²**.
- Mantener las vueltas juntas como un anillo compacto, con centro abierto.
  El flujo atraviesa la superficie encerrada por cada vuelta; no hace falta
  cubrir el disco con alambre ni convertir el bobinado en una espiral plana.
- Acomodar las vueltas aproximadamente en un mismo plano y fijarlas a un
  soporte rígido y aislante, conservando su forma durante el descenso. Esto
  fue recomendado; no se ha confirmado su implementación.
- Continuidad significa que existe un camino conductor entre los extremos
  recorriendo el devanado. No demuestra por sí sola ausencia de cortocircuitos
  entre vueltas. Para medir, las puntas deben contactar cobre; si hay esmalte,
  retirarlo solo en los extremos de conexión. Queda pendiente medir R propia.

## 4. Marco teórico integrado

### 4.1. Movimiento del carrito

Con eje \(s\) paralelo al riel, sentido positivo hacia abajo y sin pérdidas:

\[
ma=mg\sin\theta,\qquad a=g\sin\theta,
\]
\[
s(t)=s_0+v_0t+\tfrac12at^2,\qquad v(t)=v_0+at.
\]

La masa se cancela en esta aproximación. Para una distancia fija \(L\) desde la liberación hasta una posición de referencia:

\[
v_f=\sqrt{v_0^2+2gL\sin\theta}.
\]

Si parte del reposo, \(v_f=\sqrt{2gL\sin\theta}\). Aquí \(L\) es la distancia hasta esa posición, no necesariamente toda la longitud del riel. La web usa \(g=9,81\ \mathrm{m/s^2}\), \(s_0=0\) y \(v_0=0\).

Si hay una fuerza resistiva \(F_r\), el balance pasa a \(ma=mg\sin\theta-F_r\). Rozamiento, rodadura, inercia de las ruedas y fuerzas de los cables pueden modificar la velocidad real.

### 4.2. Campo, flujo y fem

El flujo por una vuelta de la captadora es

\[
\Phi_B(s)=\iint_{S(s)}\vec B\cdot d\vec S.
\]

Para campo uniforme y superficie plana se reduce a \(BA\cos\alpha\), donde \(\alpha\) es el ángulo entre campo y normal, que no debe confundirse automáticamente con la inclinación \(\theta\) del riel.

Un campo aproximadamente uniforme en la zona central no implica flujo constante durante toda la pasada: la captadora atraviesa regiones con distinto campo. La web integra Biot–Savart para los dos anillos y normaliza el resultado al campo central \(B_0\) ingresado. **No calcula automáticamente \(B_0\) a partir de corriente y vueltas de las bobinas grandes.** Desde el 03-11, el flujo por vuelta se integra sobre el disco circular con 24 nodos radiales de Gauss y 96 posiciones angulares. Se supone que todas las vueltas tienen el mismo radio y orientación, despreciando el espesor del bobinado.

Para \(N\) vueltas con el mismo flujo enlazado, Faraday–Lenz da

\[
\mathcal E=-N\frac{d\Phi_B}{dt}
=-N\frac{d\Phi_B}{ds}v(t).
\]

El signo representa la oposición al cambio de flujo. El número \(N\) del simulador corresponde a la captadora móvil, no a las bobinas grandes.

### 4.3. Circuito y magnitud medida

El modelo representa la captadora como una fuente de fem en serie con su resistencia propia:

\[
R_{\mathrm{ef}}=R_{\mathrm{carga}}\parallel R_{\mathrm{entrada}},
\qquad i=\frac{\mathcal E}{R_{\mathrm{propia}}+R_{\mathrm{ef}}},
\qquad V=iR_{\mathrm{ef}}.
\]

- **R propia:** resistencia del alambre de la captadora y sus conexiones.
- **R carga:** resistencia externa entre sus terminales.
- **R entrada:** resistencia presentada por el instrumento y la sonda.

En conexión directa, sin carga externa, se debe usar \(R_{\mathrm{ef}}=R_{\mathrm{entrada}}\). Con entrada mucho mayor que la resistencia propia, el voltaje terminal se aproxima a la fem. Si se usa una resistencia externa conocida, la corriente por ella es \(V/R_{\mathrm{carga}}\); la corriente total de la captadora incluye además la rama del instrumento.

La web todavía exige R carga positiva: **falta una opción explícita sin resistencia externa**. Introducir 1 MΩ como carga para representar solamente el osciloscopio duplica esa rama: junto al 1 MΩ ya incluido produce 0,5 MΩ efectivos.

### 4.4. Dependencia con velocidad e inclinación

Para el mismo perfil espacial de flujo, la fem en cada posición es proporcional a la velocidad. Con trayectoria, geometría y resistencias constantes, el modelo ideal desde reposo predice una amplitud proporcional a \(\sqrt{\sin\theta}\). El marco original lo expresa como \(I_{\max}\propto\sqrt{\sin\theta}\); una señal bipolar exige precisar qué pico o amplitud se compara. La predicción también puede contrastarse con voltaje si el circuito permanece fijo.

Mayor velocidad produce pulsos más altos y breves. Si se multiplica uniformemente la velocidad por dos en un tramo, la fem ideal duplica su altura y reduce su duración a la mitad. Para extremos de flujo fijados:

\[
\int_{t_1}^{t_2}\mathcal E\,dt=-N(\Phi_2-\Phi_1).
\]

Las áreas con signo se compensan al volver al mismo flujo. Esta igualdad corresponde a la fem; el voltaje medido depende del circuito.

La espira genera fem mientras cambia el flujo; no tiene una capacidad de almacenamiento de voltaje. Puede almacenar energía magnética \(U=\tfrac12 L_{\mathrm{ind}}i^2\) si circula corriente. La autoinducción no está incluida en el modelo actual, que tampoco impone un máximo intrínseco de voltaje. El montaje real tiene límites de aislamiento, calentamiento y respuesta eléctrica.

### 4.5. Variables y límites

La variable independiente es \(\theta\). Los observables posibles son \(V(t;\theta)\), amplitud pico, pico a pico, duración del pulso o corriente inferida mediante un circuito especificado.

Mantener controlados: distancia de liberación, masa y configuración del carrito, condición inicial, posición de las bobinas, trayectoria, orientación y dimensiones de la captadora, vueltas, resistencias, excitación de las bobinas y configuración del osciloscopio.

La simulación omite rozamiento, inercia de ruedas, fuerzas de cables, frenado magnético, autoinducción, capacitancia y ruido. Para comparación cuantitativa hacen falta geometría real, campo caracterizado, velocidad e incertidumbres de las mediciones. La cuadratura fija puede requerir refinamiento en geometrías extremas: las verificaciones cubren los casos probados, no todas las combinaciones permitidas.

## 5. Simulador web

- [Versión publicada](https://induccion-espira-laboratorio.candycurl2.chatgpt.site): acceso privado según el registro del 01-11-2026; conserva la versión anterior. La adaptación circular del 03-11 está en los archivos locales y no se ha publicado. Disponibilidad del enlace no comprobada en esta sesión.
- [Abrir localmente](simulacion_web/dist/index.html): funciona sin instalación ni conexión. Alternativamente, desde `simulacion_web/`, ejecutar `python3 -m http.server 8000 --directory dist` y abrir `http://localhost:8000`.

Funciones documentadas:

- Animación Canvas, reproducción, pausa, reinicio, barra temporal y velocidad de reproducción.
- Vistas en perspectiva y desde arriba, con bobinas laterales.
- Controles de campo central, radio y separación de bobinas, vueltas y radio de la captadora circular, resistencias y sonda ×1/×10.
- Inclinación numérica de 0° a 60° sincronizada con el deslizador. Conserva los decimales escritos; el deslizador redondea a dos decimales. Restablecer devuelve 10°. La precisión de entrada no implica precisión experimental.
- Gráficas de señal, campo, flujo y posición; campo y flujo disponibles incluso a 0°.
- Vista Hameg con escalas ajustables y tensión al BNC, incluida la atenuación de sonda; indicadores de pico, pico a pico, rapidez al centro y divisiones a 1 mV/div.
- CSV en unidades SI con parámetros y advertencia de resultados simulados. Entradas inválidas bloquean reproducción y exportación.
- Cálculo en Web Worker, alternativa en hilo principal y tablas reutilizadas según geometría.

La captadora inicia con **50 vueltas y radio de 4 cm**, estimaciones aportadas por el usuario. **B₀ = 1 mT, R propia = 1 Ω y R carga = 1000 Ω siguen siendo ejemplos**, no parámetros medidos. El radio de la captadora es ajustable entre 0,1 y 40 cm; las vueltas admiten enteros positivos. Si cambia la captadora, medir también su resistencia propia.

Archivos principales: `simulacion_web/dist/index.html`, `style.css`, `physics.js` y `app.js`; contraste numérico en `simulacion_web/verificar_modelo.py`; configuración de publicación en `simulacion_web/.openai/hosting.json`.

## 6. Osciloscopio Hameg HM 203-7

### 6.1. Conexión

Usar como máximo un canal: **CH I**. Conectar punta al terminal A de la captadora y masa al B, o medir en paralelo con la carga si está instalada. La masa del osciloscopio está conectada a tierra de protección.

Según la imagen del panel revisada en la bitácora web, cada entrada indica **1 MΩ ∥ 25 pF**. La web modela únicamente la parte resistiva: 1 MΩ para entrada directa/×1 y aproximadamente 10 MΩ con sonda ×10, además de dividir por diez el voltaje al BNC. La impedancia real con sonda depende de ella.

Para señales pequeñas se propuso conexión directa o sonda ×1. La entrada alta toma poca corriente y reduce la caída en R propia. Un amperímetro en serie requiere, en cambio, baja resistencia interna.

### 6.2. Ajustes iniciales propuestos

| Control | Propuesta inicial |
| --- | --- |
| Canal | CH I; CH I/II sin pulsar. |
| DUAL, ADD, X-Y | Sin pulsar. |
| Acoplamiento de entrada | DC. |
| Sensibilidad | 5 mV/div; MAG ×5 de CH I solamente si hace falta, para 1 mV/div efectivo. |
| Cero vertical | Centrado, con espacio para ambas polaridades. |
| Altura buscada | Aproximadamente 4–6 divisiones totales, sin recortar la señal. |
| TIME/DIV exterior | 50 ms/div como comienzo; no confundir con 50 µs. |
| Ajuste fino temporal | Mando central al tope izquierdo en CAL, sin forzarlo. |
| Ajustes finos | Vertical y temporal en CAL. |
| X-MAG ×10 | Sin pulsar. |
| Disparo | Interno, fuente CH I, acoplamiento DC; EXT sin pulsar. |
| AT/NORM | AUTO sin pulsar para localizar la base; NORMAL pulsado para disparar con el pulso. |
| LEVEL y flanco | Nivel por encima del ruido y dentro del primer pulso; flanco según su polaridad. |

En NORMAL puede no verse traza sin disparo válido. Las escalas proceden de propuestas orientadas por simulación: ajustar sensibilidad, tiempo y disparo con una pasada real.

**Sensibilidad y unidades, aclaradas el 03-11:** el manual (página 3 del PDF,
«Datos técnicos») especifica 5 mV/div en la escala ordinaria más sensible y
1 mV/div con expansión vertical Y×5. Con conexión directa o sonda ×1, un pulso
de 3 mV ocuparía 3 divisiones a 1 mV/div, desde la línea base. Es un ejemplo,
no una medición. Los milivoltios expresan **voltaje**; la corriente se expresa
en amperios o miliamperios. La sensibilidad de escala no es un umbral garantizado
de detección: hay que medir el ruido y observar una pasada real.

### 6.3. Registro y referencias

El HM 203-7 es analógico y no guarda trazas. Se propuso grabar la pantalla en vídeo y repetir las pasadas. Primero registrar línea base y ruido con el mismo cableado y escalas.

- [Imagen del panel](panel_osciloscopio_HM203-7.png): esquema de ubicación extraído de la página 23 del manual; no representa los ajustes ya colocados ni contiene anotaciones añadidas.
- Manual local: [Hameg — HM203-7, Manual Esp.pdf](documentos/referencias/Hameg%20-%20HM203-7,%20Manual%20Esp.pdf).
- Referencia externa consignada el 28-10: [instrucciones reproducidas en ManualsLib](https://www.manualslib.com/manual/3288230/Hameg-Hm-203-7.html?page=21). No se volvió a consultar durante esta consolidación.

## 7. Verificaciones del software

Antecedentes del **modelo rectangular del 01-11-2026**; no se repitieron para esta consolidación:

- Nueve pruebas del modelo Python lateral aprobadas.
- Contraste JavaScript–NumPy: ocho casos y 17 magnitudes, incluidas series completas; tolerancias `rtol=2e-8`, `atol=1e-11`.
- Casos de campo y ángulo nulos, cambios de geometría, vueltas, resistencias y sonda ×10.
- Cálculo en Node: aproximadamente 29 ms iniciales y 0,4 ms de media al cambiar inclinación con tablas disponibles; tiempos de esa prueba.
- Chromium: apertura local, Worker y alternativa compatible, animación, pausa, tiempo, vistas, gráficas, escalas, CSV, validación y móvil; sin errores JavaScript en las pruebas exitosas.
- Entrada exacta de ángulo: decimales, sincronización, entradas vacías o fuera de rango, extremos 0°/60°, reinicio y móvil.
- Publicación privada inicial y actualización posterior confirmadas por Sites en esa sesión.

El **modelo circular del 03-11** pasó seis casos con una referencia independiente de flujo y gradiente, además de comprobaciones físicas y de interfaz; el detalle está en el historial. El script actual `python3 simulacion_web/verificar_modelo.py` verifica la captadora circular y reemplaza el contraste rectangular anterior.

## 8. Pendientes de trabajo

- [ ] Confirmar orientación real de la captadora circular, radio medio y vueltas con mayor precisión, centro de cruce y pivote del riel.
- [ ] Concretar el circuito y protocolo para medir U_pk, según main.pdf; la estimación de campo magnético sigue siendo una posible ampliación.
- [ ] Añadir al simulador conexión directa sin resistencia externa.
- [ ] Reemplazar parámetros de ejemplo por los del aparato: B₀, dimensiones y separación de bobinas, vueltas, área y R propia de la captadora, carga y sonda.
- [ ] Medir ruido y línea base; registrar una pasada y ajustar escalas y disparo.
- [ ] Probar un filtro RC pasabajos, registrar R y C, y comprobar que no distorsione el voltaje pico, especialmente a la mayor inclinación.
- [ ] Registrar repeticiones por ángulo con condiciones de liberación constantes e incertidumbres.
- [ ] Comparar señal real con predicción y revisar pérdidas mecánicas o respuesta eléctrica si hace falta.
- [ ] Si se retoma la alternativa de la galletera, caracterizar su bobina fija (no confundir con el rotor o inducido). Actualmente se trabaja con la captadora circular provisional; no se ha adoptado la alternativa de motor.

## 9. Registro de próximas mediciones

Copiar esta ficha por sesión; los campos vacíos no representan datos obtenidos:

| Dato | Registro |
| --- | --- |
| Fecha y responsables | |
| Objetivo de la sesión | |
| Captadora: tipo, orientación, vueltas, dimensiones y resistencia | |
| Bobinas: posición, dimensiones, separación y excitación | |
| Campo: medido o supuesto, método y unidades | |
| Ángulo e incertidumbre | |
| Posición de liberación y distancia de referencia | |
| Carga externa y conexión | |
| Sonda, V/div efectivo, tiempo/div, acoplamiento y disparo | |
| Ruido y línea base | |
| Repetición; pico positivo, negativo, pico a pico y duración | |
| Vídeo, fotografía o archivo de datos | |
| Observaciones, comparación y siguiente paso | |

## 10. Historial de avances y decisiones

### 28-10-2026 — Preparación del osciloscopio

Se propuso CH I, DC, 5 mV/div o 1 mV/div mediante MAG ×5 y 50 ms/div. Se guardó la imagen del panel y se sugirió registro en vídeo. Sin señal real aportada ni ajustes confirmados en el instrumento.

### 01-11-2026 — Simulación web y geometría lateral

Se adoptó el modelo lateral tras la aclaración del usuario sobre las bobinas. Se creó y publicó la interfaz web, luego se añadió entrada numérica exacta de inclinación. Se documentaron resistencias, entrada del osciloscopio y relación entre velocidad, fem y energía. Quedó pendiente la conexión directa sin carga externa.

### 01-11-2026 — Consolidación de la bitácora

Se leyeron y reunieron los tres documentos de origen en este archivo. Se aclaró la diferencia entre voltaje observado y corriente inferida, y entre geometría confirmada y supuestos. Se incorporó como pendiente la consulta del usuario sobre sustituir la espira por el inducido de una galletera para medir campo magnético; todavía no se ha evaluado ni adoptado esa modificación. Las futuras actualizaciones se concentrarán en esta bitácora.

### 01-11-2026 — Bobina fija de galletera y consulta externa

El usuario confirmó que dispone de la bobina fija de una galletera y desconoce su número de vueltas. Falta saber si conserva el núcleo de hierro, su geometría y sus conexiones. Se discutió distinguir detección y comparación de señales de la medición de campo en teslas; no se hicieron pruebas ni se adoptó el reemplazo. Se creó `consulta_chatgpt_bobina_galletera.md` (ahora dentro del respaldo histórico ZIP), un resumen autónomo del contexto, las alternativas y las preguntas para continuar la consulta en ChatGPT web.


### 03-11-2026 — Captadora provisional circular y adaptación de la web local

El usuario consiguió una captadora de aproximadamente 50 vueltas y 4 cm de
radio, y confirmó continuidad del alambre. La fotografía está en
[figuras/captadora provisional.jpeg](figuras/captadora%20provisional.jpeg).
Se observa un bobinado aproximadamente circular, algo deformado y sin núcleo
visible; la fotografía no verifica vueltas, dimensiones ni aislamiento entre
vueltas. No se ha informado un valor de resistencia propia ni una señal medida.

Se sustituyó la captadora rectangular de la **web local** por una circular.
Se añadieron radio medio ajustable, diámetro y área por vuelta; se actualizaron
la animación, el cálculo de flujo, los metadatos y nombre del CSV. El número de
vueltas sigue siendo editable y ahora inicia en 50; el radio inicia en 4 cm.
La versión Python de Simulación 2 conserva la geometría rectangular anterior.
Esta modificación no actualiza la versión alojada en Sites.

El modelo usa N vueltas coincidentes, rígidas y sin núcleo. El flujo integra
el campo sobre el disco encerrado por cada vuelta, aunque el centro del aro
esté vacío. La normal se mantiene transversal, como en la geometría lateral
anterior. El montaje real deberá respetar esa orientación para contrastarlo.

Verificaciones realizadas:

- Node/NumPy: seis geometrías, incluyendo radios de 0,1; 4; 8; 15 y 40 cm,
  y un caso con bobinas grandes de radio 2 cm y captadora de radio 1 cm.
- Referencia independiente por franjas cartesianas y Biot–Savart más fino:
  errores normalizados menores de 0,03 % en flujo y 0,5 % en gradiente espacial.
- Duplicar vueltas duplica la fem; se comprobó la dependencia ideal con el ángulo,
  señal nula para campo o ángulo nulos y rechazo de entradas inválidas.
- Chromium: controles de vueltas y radio, reproducción, vistas, gráficas, CSV,
  reinicio, tamaño móvil y alternativa sin Worker; sin errores JavaScript.

Estos resultados verifican el programa para los casos probados, no la validez
experimental del modelo. Quedan pendientes campo, resistencia, geometría real
y registros de pasadas. Las combinaciones extremas de captadora grande y
bobinas muy próximas pueden requerir refinamiento numérico.


### 03-11-2026 — Aclaraciones de uso y consolidación final

Se leyó la propuesta `main.pdf` y se identificó el objetivo de comparar el voltaje
pico con la inclinación y, si es posible, con la rapidez. Se explicó continuidad,
la conveniencia de conservar un aro compacto y el significado del área encerrada.
El usuario confirmó continuidad; quedan pendientes resistencia y caracterización.
Se revisaron los datos técnicos del Hameg y se aclaró la diferencia entre mV de
voltaje y mA de corriente, y entre sensibilidad vertical y detección de señal.

A petición del usuario se dejaron reunidos en esta bitácora los avances,
decisiones, supuestos, resultados simulados y pendientes. Las dos bitácoras
anteriores y la consulta de galletera se archivaron íntegramente en
`documentos/archivo/antecedentes_2026-11-03.zip`, verificando el contenido antes
de retirar los archivos sueltos. Se actualizaron los enlaces y el README.
No se añadieron datos experimentales ni se repitieron pruebas numéricas durante
esta organización documental.

La consulta histórica de galletera queda como alternativa sin ensayar: se
habían considerado bobinas de relé, electroválvula, transformador o estator,
o fabricar una bobina contando vueltas. Para la bobina fija disponible faltaban
núcleo, conexiones, geometría, vueltas, resistencia e inductancia. Detectar o
comparar pulsos no equivale a medir campo en teslas; esto último requiere
caracterización o calibración. Un núcleo de hierro modificaría el campo y la
respuesta y no está representado en el modelo actual. No se identificó la
captadora circular fotografiada como esa bobina de motor.


### 04-11-2026 — Señal débil, interferencias y propuesta de filtro pasabajos

**Observación comunicada por el usuario:** en el último laboratorio el voltaje
fue tan bajo que no pudo medirse claramente con el osciloscopio, debido a señales
parásitas atribuidas a los cables de la captadora y a fuentes externas. No se
aportaron valores de amplitud, fotografías, trazas ni frecuencia medida del ruido.
La descripción de señal útil del orden de Hz y ruido del orden de MHz es una
hipótesis de trabajo, no una caracterización espectral confirmada.

El profesor recomendó usar un capacitor como filtro. El usuario confirmó que
disponen de resistencias y capacitores variables; no indicó sus rangos ni los
valores utilizados. No se confirmó todavía el montaje o ensayo de un filtro.

**Recomendación discutida:** probar un filtro RC pasabajos, con una resistencia
en serie entre el terminal A de la captadora y CH I, y un capacitor entre la
entrada CH I y el terminal B, conectado a la masa de CH I. El osciloscopio mide
sobre el capacitor. Instalarlo cerca de la entrada, con conexiones cortas.
La frecuencia de corte aproximada es `fc = 1/(2πRC)`, suponiendo resistencia
propia de la captadora pequeña frente a R, entrada del instrumento mucho mayor
que R y efectos inductivos despreciables en la banda útil. El filtro atenúa
componentes rápidas; no amplifica la señal.

Valores propuestos para explorar, no componentes ya adoptados ni resultados:

| R | C | Corte aproximado |
| --- | --- | --- |
| 10 kΩ | 100 nF | 159 Hz |
| 10 kΩ | 330 nF | 48 Hz |
| 10 kΩ | 1 µF | 16 Hz |

Se propuso empezar con 10 kΩ y 100 nF y aumentar C gradualmente si hace falta.
Usar un capacitor no polarizado para la señal bipolar. Un capacitor solo en
paralelo también modifica la respuesta, pero el filtrado depende de la resistencia
e inductancia de la captadora y puede presentar resonancia; no se dimensionó
esa alternativa. La inductancia y capacitancia no están incluidas en el simulador
actual, por lo que este no predice todavía la señal con filtro.

**Aclaración sobre escalas:** los milivoltios determinan la elección de VOLTS/DIV,
no TIME/DIV. La escala temporal depende de la duración del pulso. Se reiteraron
como inicio 5 mV/div, o 1 mV/div efectivo con Y×5, acoplamiento DC y 50 ms/div,
ajustando el tiempo hasta observar el pulso completo. El usuario no confirmó
el TIME/DIV realmente usado.

**Comprobaciones propuestas:**

- Trenzar juntos los dos cables de salida y reducir las áreas de los lazos y
  las conexiones de masa para disminuir captación de interferencias.
- Registrar línea base con el carrito quieto y comparar pasadas con y sin filtro,
  manteniendo ángulo y posición de liberación.
- Comprobar que al aumentar C no disminuya apreciablemente el pico ni se ensanche
  el pulso. La frecuencia de repetición de las pasadas no determina por sí sola
  el ancho de banda necesario para conservar su forma.
- Revisar especialmente la mayor inclinación, donde el pulso esperado es más
  breve. Una atenuación distinta según el ángulo sesgaría la comparación de U_pk.
- Una vez elegido el filtro, mantener R y C constantes entre ángulos y registrar
  sus valores. Comparar alturas requiere repeticiones, pues puede variar la pasada.
- Verificar la frecuencia del ruido: el corte de 159 Hz atenúa poco una posible
  interferencia de red de 50 Hz. No se identificó todavía su contribución.

Referencias consultadas durante la conversación:
[Analog Devices, filtro pasabajos y frecuencia de corte](https://www.analog.com/en/resources/technical-articles/a-beginners-guide-to-filter-topologies.html)
y [Tektronix, captación de ruido y conexiones de sondas](https://www.tek.com/en/documents/whitepaper/abcs-probes-primer).

Queda pendiente medir la duración y amplitud del pulso, caracterizar el ruido,
conocer los rangos de componentes disponibles y ensayar el filtro. No se informó
una señal recuperada ni una mejora experimental confirmada.

### 04-11-2026 — Lecturas recomendadas y cierre de la sesión

Se recomendaron las siguientes lecturas, en este orden, para comprender el
filtro RC pasabajos antes de ensayarlo:

1. [Electrónica básica, unidad 3 — Universidad Abierta y a Distancia de México](https://dmd.unadmexico.mx/contenidos/DCEIT/BLOQUE2/TM/03/KELB/U3/descargables/KELB_U3_Contenido.pdf).
   En español; buscar «Filtro pasa bajo RC» dentro del PDF. Introducción al
   circuito y a las frecuencias que deja pasar.
2. [An Introduction to Electrical Filters — Analog Devices](https://wiki.analog.com/university/courses/engineering_discovery/lab_5).
   En inglés, con enfoque experimental: construcción y observación de filtros RC.
3. [A Beginner’s Guide to Filter Topologies — Analog Devices](https://www.analog.com/en/resources/technical-articles/a-beginners-guide-to-filter-topologies.html).
   Leer primero la introducción y el filtro pasabajos de un polo; dejar las
   configuraciones avanzadas para después.

Conceptos para orientar la lectura: reactancia capacitiva
`X_C = 1/(2πfC)`, salida tomada sobre el capacitor, constante de tiempo
`τ = RC`, frecuencia de corte `fc = 1/(2πRC)` y efecto del filtro sobre la
altura y duración de un pulso. La transición es gradual: interesa reducir el
ruido sin alterar apreciablemente el pico útil que se comparará entre ángulos.

El usuario dio por terminada la sesión por hoy. Las lecturas quedan recomendadas,
sin confirmación de haberlas realizado. Al retomar, siguen pendientes la
caracterización de señal y ruido y el ensayo del filtro descrito arriba; no se
registraron nuevas mediciones ni pruebas del montaje.
