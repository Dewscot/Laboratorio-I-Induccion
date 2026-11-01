# Bitácora: simulación web, geometría y medición de inducción

Fecha: 1 de noviembre de 2026.

## 1. Punto de partida

Se leyó la [bitácora del osciloscopio del 28 de octubre](bitacora_osciloscopio_2026-10-28.md)
para retomar el trabajo. Allí se habían propuesto ajustes iniciales para el Hameg
HM 203-7: un solo canal CH I, acoplamiento DC, 5 mV/div, posible expansión Y×5
para obtener 1 mV/div, y 50 ms/div como base inicial. Los ajustes finos deben
permanecer en CAL.

Esas escalas son orientativas: todavía no se ha aportado una señal experimental
ni se ha confirmado su amplitud, duración o ruido. El HM 203-7 es analógico y no
guarda trazas; se había sugerido registrar las pasadas mediante vídeo y repetirlas.

El usuario solicitó reemplazar la interfaz de Matplotlib de
`simulacion_induccion.py` por una versión web, debido a su aspecto y lentitud.

## 2. Corrección de la geometría

El usuario aclaró expresamente que **las bobinas están a los costados del riel,
no una arriba y otra abajo**.

Al revisar el proyecto se encontró un modelo lateral ya existente en
[`Simulacion 2/simulacion_induccion_helmholtz.py`](Simulacion%202/simulacion_induccion_helmholtz.py),
documentado en
[`Simulacion 2/SIMULACION_HELMHOLTZ.md`](Simulacion%202/SIMULACION_HELMHOLTZ.md).
Se tomó ese modelo como base de la versión web.

La geometría adoptada es:

- Dos bobinas circulares fijas a ambos costados del riel, con eje común transversal
  al sentido de avance del carrito.
- Captadora rectangular en el plano vertical longitudinal del riel. Su normal
  queda alineada con el campo en el plano medio entre las bobinas.
- Trayectoria centrada en el plano medio. Se supone que el riel gira alrededor
  del centro de las bobinas al modificar la inclinación.

**La posición lateral de las bobinas fue aclarada por el usuario. La orientación
de la captadora y el pivote central son supuestos del modelo existente**, que
deben contrastarse con el montaje real. Si la captadora queda acostada sobre el
riel o el cruce se desplaza respecto del centro, hay que revisar el flujo calculado.

Para esta geometría no se aplica el factor `cos(theta)` usado en el modelo
anterior con campo vertical y espira paralela al riel. La espira rota dentro del
plano medio sin cambiar la dirección de su normal transversal.

El archivo original `simulacion_induccion.py` se conservó como referencia;
no fue reescrito. El `README.md` distingue la versión web del modelo anterior.

## 3. Modelo físico de la versión web

El movimiento parte del reposo y se calcula sin pérdidas:

\[
a=g\sin\theta,\qquad s(t)=\tfrac12at^2,\qquad v(t)=at,
\qquad g=9{,}81\ \mathrm{m/s^2}.
\]

El riel mide 1,50 m y el centro de las bobinas está en `s = 0,75 m`.

El campo transversal se calcula integrando Biot–Savart para dos anillos
circulares con corrientes iguales y del mismo sentido. Se normaliza al campo
central B₀ introducido por el usuario; **B₀ no se calcula automáticamente a partir
de la corriente y las vueltas de las bobinas grandes**.

El perfil es suave, sin bordes artificiales de campo uniforme. Se integra el
campo sobre el área finita de la captadora con cuadratura de Gauss de 7×7 puntos:

\[
\Phi_B(s)=\iint_{S(s)}\vec B\cdot d\vec S,
\qquad \mathcal E(t)=-N\frac{d\Phi_B}{ds}v(t).
\]

Se calcula también la corriente y el voltaje sobre la carga efectiva:

\[
R_{\mathrm{ef}}=R_{\mathrm{carga}}\parallel R_{\mathrm{entrada}},
\qquad i=\frac{\mathcal E}{R_{\mathrm{propia}}+R_{\mathrm{ef}}},
\qquad V= iR_{\mathrm{ef}}.
\]

Se omiten rozamiento, inercia de las ruedas, fuerzas de cables, frenado magnético,
autoinducción, capacitancia y ruido. La integración conserva la resolución del
modelo Python; coincidir con él valida la traducción, pero no garantiza
convergencia para todas las geometrías extremas permitidas.

## 4. Versión web creada y publicada

**Enlace publicado, con acceso privado:**

[Inducción · Laboratorio virtual](https://induccion-espira-laboratorio.candycurl2.chatgpt.site)

**Apertura local sin conexión:** abrir
[`simulacion_web/dist/index.html`](simulacion_web/dist/index.html) en el navegador.
No requiere instalación ni servidor para este uso.

Alternativamente, desde `simulacion_web/`:

```bash
python3 -m http.server 8000 --directory dist
```

Después visitar `http://localhost:8000`.

### Archivos

| Archivo | Función |
| --- | --- |
| `simulacion_web/dist/index.html` | Interfaz y controles |
| `simulacion_web/dist/style.css` | Diseño adaptable a escritorio y móvil |
| `simulacion_web/dist/physics.js` | Modelo numérico JavaScript |
| `simulacion_web/dist/app.js` | Interacciones, animación, gráficas y exportación |
| `simulacion_web/verificar_modelo.py` | Contraste con el modelo Python lateral |
| `simulacion_web/README.md` | Uso, hipótesis y verificación |
| `simulacion_web/.openai/hosting.json` | Identidad y configuración de publicación en Sites |

### Funciones implementadas

- Animación mediante Canvas y `requestAnimationFrame`.
- Cálculos en un Web Worker para separar el trabajo numérico de la interfaz;
  modo compatible en el hilo principal si el navegador bloquea Workers.
- Tablas de campo y flujo conservadas por geometría para evitar repetir cálculos.
- Controles de campo central, radio y separación de las bobinas, vueltas y
  dimensiones de la captadora, resistencias y sonda ×1/×10.
- Reproducción, pausa, reinicio temporal, velocidad de reproducción y barra de tiempo.
- Vistas del montaje en perspectiva y desde arriba, con bobinas laterales.
- Gráficas de señal, campo, flujo y posición; campo y flujo se muestran en todo
  el recorrido incluso con inclinación de 0°.
- Vista de referencia del Hameg con escalas verticales y temporales ajustables.
  Representa la tensión al BNC, incluyendo la atenuación de la sonda.
- Indicadores de voltaje pico, voltaje pico a pico, rapidez al centro y altura
  en divisiones a 1 mV/div.
- Exportación CSV con series en unidades SI, parámetros y aclaración de que son
  resultados simulados.
- Mensajes para entradas inválidas y bloqueo de reproducción/exportación hasta corregirlas.

## 5. Entrada exacta de la inclinación

Posteriormente el usuario pidió poder escribir un valor exacto para la
inclinación del riel.

Se añadió una **casilla numérica junto al deslizador**, con rango de **0° a 60°**.
Ambos controles están sincronizados. La entrada numérica conserva los decimales
introducidos, por ejemplo `17.35789`, sin redondearlos a décimas. Esto especifica
el valor de la simulación; no implica esa precisión experimental del ángulo.

El deslizador permite ajustes rápidos redondeados a dos decimales. Restablecer
los valores devuelve ambos controles a 10°. Las entradas vacías o fuera de rango
generan un aviso.

La mejora quedó incorporada tanto en los archivos locales como en el mismo
enlace privado publicado. Si la página ya está abierta, recargarla.

## 6. Aclaraciones sobre vueltas y resistencias

**Número de vueltas:** corresponde a la captadora que viaja sobre el carrito
y atraviesa el campo. No son las vueltas de las dos bobinas grandes de Helmholtz.

**R propia:** resistencia del alambre de la captadora y sus conexiones.

**R carga:** resistencia externa adicional conectada entre los terminales de
la captadora. En la simulación se combina en paralelo con la entrada del
osciloscopio.

Los valores iniciales son ejemplos: R propia = 1 Ω, R carga = 1000 Ω,
10 vueltas captadoras y B₀ = 1 mT. No están confirmados como valores reales.

Se revisó la imagen local
[`panel_osciloscopio_HM203-7.png`](panel_osciloscopio_HM203-7.png).
Junto a las entradas CH I y CH II figura **«INPUT 1 MΩ ∥ 25 pF»**:
cada canal presenta una resistencia de entrada de **1 MΩ = 1 000 000 Ω**,
en paralelo con una capacitancia de 25 pF. Ese es el valor de la entrada directa;
la resistencia vista con una sonda depende también de la sonda.

La versión web ya incluye 1 MΩ para conexión directa/×1 y aproxima la entrada
de una sonda ×10 como 10 MΩ, con atenuación de voltaje por diez. El cálculo
actual solo incluye la parte resistiva, no los 25 pF.

### Conexión directa explicada

La captadora se representa mediante una fuente de fem en serie con su
resistencia propia. El osciloscopio se conecta entre los dos terminales:

```text
             R propia
       ┌─────/\/\/─────A──────┐
       │                     │
   Fem inducida         Entrada CH I
       ℰ                1 MΩ ∥ 25 pF
       │                     │
       └───────────────B──────┘

       Punta de CH I → A; masa → B.
       Sin resistencia externa adicional.
```

Para medir voltaje interesa una resistencia de entrada alta: así el instrumento
toma poca corriente y reduce la caída de tensión en la resistencia propia.
Un amperímetro, conectado en serie para medir corriente, necesita una resistencia
interna baja. Son formas distintas de minimizar la perturbación de la medición.

**Pendiente de implementar:** una opción explícita de conexión directa al
osciloscopio, sin resistencia externa. La interfaz actual sigue exigiendo una
R carga positiva. No se debe introducir otro 1 MΩ en ese campo para representar
únicamente la entrada del osciloscopio, porque quedaría en paralelo con el
1 MΩ que el modelo ya incluye y daría 0,5 MΩ efectivos.

## 7. Velocidad, voltaje y almacenamiento de energía

El usuario preguntó si la espira tiene una cantidad máxima de voltaje que pueda
almacenar. Se aclaró que la espira **genera fem mientras cambia el flujo**;
no almacena voltaje como un recipiente con capacidad máxima.

Para la misma geometría y el mismo recorrido por el campo, mayor velocidad
produce un cambio de flujo más rápido: pulsos más altos y más breves.
Para cualquier tramo con extremos de flujo fijados:

\[
\int_{t_1}^{t_2}\mathcal E\,dt=-N(\Phi_2-\Phi_1).
\]

Si se duplica uniformemente la velocidad sobre ese tramo, el pulso ideal duplica
su altura y reduce su duración a la mitad. Al recorrer una entrada y una salida
que vuelven al mismo flujo, las áreas con signo se compensan.

La espira puede almacenar energía magnética cuando circula corriente,
`U = ½ L I²`, debido a su inductancia. Es distinto de almacenar voltaje y esta
inductancia no está incluida en la simulación actual. El modelo ideal no impone
un máximo intrínseco de voltaje de la captadora; el aparato real tiene límites
por aislamiento, calentamiento y respuesta del circuito.

## 8. Verificaciones realizadas durante esta sesión

- Pasaron las nueve pruebas del modelo Python lateral.
- `simulacion_web/verificar_modelo.py` contrastó ocho casos y 17 magnitudes con
  NumPy, incluidas las series completas. Coincidieron con tolerancias
  `rtol=2e-8` y `atol=1e-11`.
- Se comprobaron campo y ángulo nulos, variación de geometría, vueltas,
  resistencias y sonda ×10.
- La prueba de cálculo en Node registró aproximadamente 29 ms en la primera
  ejecución y 0,4 ms de media al cambiar la inclinación con tablas disponibles.
  Son tiempos de esa prueba, no una garantía para cualquier dispositivo.
- Las pruebas de Chromium verificaron apertura local, Worker y modo compatible,
  animación, pausa, barra temporal, vistas, gráficas, escalas del Hameg, CSV,
  validación de entradas y diseño móvil sin desbordamiento. No se detectaron
  errores de JavaScript en las pruebas exitosas.
- Tras añadir el ángulo exacto se verificaron decimales, sincronización en ambos
  sentidos, valores vacíos y fuera de rango, extremos 0°/60°, reinicio y móvil.
- Sites confirmó la publicación privada inicial y su actualización posterior.

## 9. Pendientes al retomar

1. Añadir la opción de medición directa sin resistencia externa.
2. Confirmar orientación y forma de la captadora, dimensiones, centro de cruce
   y pivote real del riel. Ajustar el modelo si difieren de sus supuestos.
3. Sustituir los valores de ejemplo por B₀, vueltas, dimensiones y resistencias
   del montaje real. Actualizar R propia si cambian las vueltas o el alambre.
4. Medir la línea base y el ruido con el mismo cableado y escalas; registrar una
   pasada real para ajustar sensibilidad, base de tiempo y disparo.
5. Contrastar la señal real con la predicción. No tratar los CSV exportados ni
   los valores mostrados como mediciones del laboratorio.

Esta bitácora documenta el trabajo y las explicaciones de la conversación;
no certifica que se hayan realizado nuevas mediciones experimentales.
