# Simulación del experimento de inducción

Ejecutar en esta carpeta:

```bash
python simulacion_induccion.py
```

Requiere Python, NumPy y Matplotlib, ya disponibles en el entorno de este proyecto. La ventana permite mover el ángulo del riel, animar el carro y ver posición–tiempo y fem–tiempo. Los campos de la derecha se confirman con **Aplicar**. El botón **PNG + CSV** guarda gráficas, datos calculados en unidades SI y parámetros JSON en `resultados_simulacion/`. Al repetir una exportación con el mismo ángulo y vueltas se actualizan esos archivos.

Para generar los resultados sin abrir una ventana:

```bash
python simulacion_induccion.py --exportar --angulo 10 --vueltas 10
```

## Modelo y geometría

Fuente: [marco teorico julio.pdf](<documentos/borradores/marco teorico julio.pdf>), ecuaciones 1–5, 10–11 y apartado 2.5 (ecuaciones 15–18). La carga resistiva corresponde al apartado 2.6, incorporando además la resistencia de entrada del osciloscopio en paralelo con la carga.

- Riel recto de **1,50 m**, carro liberado desde el reposo. La posición representa el centro de la espira.
- El centro magnético permanece en **s = 0,75 m**; el riel gira alrededor de ese punto en el esquema. Las bobinas conservan su orientación en el laboratorio.
- Se supone que **la superficie de la espira es paralela al riel**. Si la espira se monta de otra forma, debe cambiarse esa geometría en el modelo.
- Campo uniforme dentro de una región efectiva de longitud `zona_cm`, medida sobre el riel, y nulo fuera. Esa longitud es un parámetro aproximado: no se identifica automáticamente con el radio ni con la separación de Helmholtz.
- La dirección de B es fija durante y entre bajadas. El valor predeterminado, 90° respecto de la horizontal, significa campo vertical y planos de las bobinas horizontales. No significa bobinas verticales.
- El cambio de inclinación sí cambia el ángulo entre la normal de la espira y B. Con B vertical, β = θ. En general, cos β = sen(θ + γ), con γ la dirección de B medida desde la horizontal hacia arriba.

Se calcula:

\[
a=g\sin\theta,\quad s(t)=\tfrac12at^2,\quad v(t)=at,
\]
\[
\Phi_B(s)=B_0 h\,\ell_{\mathrm{dentro}}(s)\cos\beta,
\qquad \mathcal E=-N_e\frac{d\Phi_B}{ds}v.
\]

Aquí h es el **ancho transversal** de la espira y ℓ_dentro es la longitud de su solapamiento con la región de campo. Se incluye la entrada, la salida y la posible cancelación si ambos lados de la espira se encuentran en campo uniforme. Al entrar aparece un pulso; al salir, otro de signo contrario. La orientación elegida de la normal fija el signo; invertir los cables lo invierte.

No se utiliza la expresión axial de Helmholtz sobre una trayectoria oblicua. La franja verde es una región **equivalente**, no un mapa real del campo. Su longitud se mantiene fija al mover el ángulo: si la trayectoria real cambia la zona atravesada, hay que ajustar ese parámetro. Los bordes abruptos producen saltos ideales; el campo real los suaviza. Las dimensiones dibujadas de las bobinas son ilustrativas.

Se omiten rozamiento, inercia de las ruedas, frenado magnético, autoinducción, capacitancias, ruido y respuesta de disparo. El cálculo de voltaje es apropiado como primera estimación cuando la respuesta es principalmente resistiva. Un resultado favorable no garantiza detección experimental. La resistencia propia debe actualizarse si cambian las vueltas o el alambre; el programa permite variarlas por separado para estudiar sus efectos.

## Comparación con el Hameg HM 203-7

Se consultó el [manual aportado](<documentos/referencias/Hameg - HM203-7, Manual Esp.pdf>), página PDF 3 (P1: datos técnicos), PDF 4 (Z1: sondas) y PDF 7 (M3: magnitud de señal):

| Característica | Valor del manual |
|---|---|
| Escala vertical más sensible, normal | 5 mV/div |
| Con expansión Y-MAG ×5 | 1 mV/div, banda hasta 3,5 MHz |
| Entrada directa | 1 MΩ en paralelo con 25 pF |
| Sonda pasiva ×10 | Atenúa 10 veces; entrada típica de las sondas indicadas: 10 MΩ |
| Base de tiempo calibrada | 0,2 µs/div a 0,1 s/div, secuencia 1–2–5 |

**mV/div es una escala de deflexión, no una resolución digital ni un umbral de ruido.** La simulación muestra la altura del pico respecto de cero. La altura total de ambos lóbulos corresponde al voltaje pico a pico, también informado. Una división es solamente una referencia visual elegida para comparar amplitudes; señales más pequeñas pueden observarse dependiendo del ruido y del ajuste.

Para los valores de ejemplo: acoplamiento **DC**, ajuste fino en **CAL**, entrada directa o sonda **×1**, 5 mV/div y, si hace falta, **Y-MAG ×5**. El manual recomienda DC para pulsos y advierte que AC puede deformar señales lentas (límite inferior aproximadamente 1,6 Hz). Empezar alrededor de **50 ms/div** para observar entrada y salida, y ajustar el disparo normal, nivel y flanco al primer pulso. La interfaz recalcula una base de tiempo inicial al cambiar la velocidad. Si la señal es mayor, usar una escala vertical menos sensible para evitar que salga de pantalla.

El HM 203-7 es un osciloscopio analógico convencional; no debe confundirse la exportación de esta simulación con una adquisición del instrumento. El paso aislado del carro produce una traza breve: para registrarla, planificar repeticiones y fotografía/vídeo de la pantalla, o una adquisición externa si la tienen. La señal real de fondo debe medirse con el mismo cableado, sonda y escala.

## Ejemplo calculado, no datos del laboratorio

Parámetros iniciales: θ = 10°, B = **1 mT supuesto**, espira de 10 × 10 cm paralela al riel, zona efectiva de campo de 30 cm, B vertical, resistencia propia de 1 Ω, carga de 1 kΩ y sonda ×1.

| Vueltas | Fem máxima en magnitud | Voltaje pico en la carga | Pico con Y×5 |
|---|---:|---:|---:|
| 1 | 0,177 mV | 0,177 mV | 0,18 div |
| 10 | 1,772 mV | 1,770 mV | 1,77 div |

Los pulsos duran unos **70 ms** y **57 ms**; la rapidez al centro es **1,60 m/s**. Con diez vueltas, el voltaje pico a pico es aproximadamente **3,23 mV**. Estos resultados sugieren que una sola vuelta puede producir una señal difícil de leer, mientras que diez vueltas ofrecen una amplitud más favorable bajo estos supuestos. No se conoce todavía el B real ni las dimensiones finales de la espira.

Si falta B, el campo central ideal puede estimarse con la ecuación 6 de Julio:

\[
B_0=\left(\frac45\right)^{3/2}\frac{\mu_0N_H I_H}{R_H}.
\]

N_H son las vueltas **por bobina de Helmholtz**, distintas de las vueltas N_e de la espira móvil. Por ejemplo, N_H = 200, R_H = 0,15 m e I_H = 1 A darían aproximadamente 1,20 mT. También son valores ilustrativos. Esta fórmula no determina la longitud efectiva de campo ni su perfil fuera del centro.

## Qué ayuda a aumentar la señal

| Cambio | Efecto bajo las aproximaciones del modelo |
|---|---|
| Más vueltas de la espira | Aumenta la fem proporcionalmente. En el montaje real también cambian resistencia e inductancia. |
| Campo mayor | Aumenta la fem si se conserva la geometría. Mantener la corriente de alimentación dentro de la capacidad del equipo. |
| Más ancho transversal h | Aumenta la fem durante la entrada y salida, mientras el campo cubra ese ancho. |
| Más longitud de espira en el sentido del movimiento | Cambia el flujo total y la duración/separación de pulsos; no aumenta directamente el factor N_e B h v cos β a igual velocidad. Puede cambiar la velocidad a la que ocurre el pico. |
| Más recorrido antes del campo | Aumenta la rapidez como √d y con ello la fem para el mismo acoplamiento. Agregar riel después de la zona no aumenta la velocidad de entrada. |
| Menor resistencia propia | No aumenta la fem para el mismo movimiento y campo. Aumenta la corriente y el voltaje sobre una carga fija. |
| Mejor alineación normal–campo | Aumenta \|cos β\|; una orientación perpendicular anula el flujo en este modelo. |

La corriente y el voltaje medido son distintos de la fem:

\[
R_{\rm ef}=R_L\parallel R_{\rm entrada},\qquad
i=\frac{\mathcal E}{r_e+R_{\rm ef}},\qquad
V_R=\mathcal E\frac{R_{\rm ef}}{r_e+R_{\rm ef}}.
\]

Para medir voltaje interesa una carga efectiva grande frente a la resistencia propia; para aumentar corriente, una resistencia total menor. Aumentar la resistencia del alambre no ayuda a inducir más fem.

Con B vertical, la velocidad aumenta al inclinar el riel pero el factor cos θ disminuye. Para geometría efectiva fija, la amplitud escala como cos θ √sen θ: **más inclinación no siempre produce más fem**. El máximo ideal de ese factor se encuentra cerca de 35,3°, sin que eso determine por sí solo el ángulo práctico del montaje real.

## Verificación

```bash
python -m unittest test_simulacion_induccion
```

Las comprobaciones contrastan conservación de energía mecánica, Faraday por diferencias finitas e integral del pulso, casos de fem nula, ley de Lenz, orientación, dependencia con vueltas/campo y carga de la sonda.
