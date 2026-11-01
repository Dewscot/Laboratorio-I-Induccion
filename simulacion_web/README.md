# Inducción · versión web

Abrir **`dist/index.html`** en Firefox, Chrome o Chromium. No requiere instalación,
servidor, Python, Matplotlib, conexión a internet ni bibliotecas externas.

También se puede servir desde esta carpeta:

```bash
python3 -m http.server 8000 --directory dist
```

Luego visitar `http://localhost:8000`.

## Geometría utilizada

Esta versión usa el montaje de **`Simulacion 2/simulacion_induccion_helmholtz.py`**:
dos bobinas **a los costados del riel**, eje transversal y captadora rectangular
vertical en el plano longitudinal del riel. Se presupone que la trayectoria
permanece en el plano medio y que el riel gira alrededor del centro de las bobinas.
La captadora rota dentro de ese plano, manteniendo su normal alineada con el campo.

Por ello no se aplica el factor `cos(theta)` del modelo inicial
`simulacion_induccion.py`. El campo se obtiene de Biot–Savart para anillos circulares;
su perfil es suave. Se calcula el flujo sobre el área finita con cuadratura de
Gauss de 7×7 puntos. El campo central B₀, dimensiones y resistencias iniciales son
ejemplos ajustables. El modelo no incluye ruido, pérdidas mecánicas ni inductancia.
Para bobinas muy próximas y espiras grandes, la cuadratura fija puede requerir
refinamiento: la coincidencia con Python valida la traducción, no la convergencia
para todas las geometrías admitidas.

## Uso

- La inclinación se puede escribir como valor numérico exacto (por ejemplo,
  `17.35°`) o ajustar con el deslizador. Ambos controles están sincronizados;
  el campo numérico conserva los decimales introducidos y admite de 0° a 60°.
- Los parámetros actualizan la predicción automáticamente; las entradas inválidas
  muestran un mensaje y deshabilitan la reproducción y exportación.
- **Iniciar / Pausar**, la barra temporal y la velocidad permiten explorar la pasada.
- **Perspectiva / Desde arriba** muestran las dos bobinas laterales. Desde arriba la
  espira vertical se ve de canto. El dibujo es esquemático.
- **Señal / Campo / Flujo / Posición** permiten comparar magnitudes. Campo y flujo
  muestran el recorrido completo incluso con la espira detenida a 0°.
- **Hameg** representa el voltaje al BNC con atenuación ×1 o ×10 y escalas calibradas.
  La ventana se centra en el cruce del centro. El ajuste de escalas es orientativo,
  y el ruido y disparo deben comprobarse en el instrumento real.
- **Exportar CSV** guarda las series en unidades SI, la geometría y los parámetros
  como comentarios iniciales (`#`). Por ejemplo: `numpy.loadtxt(archivo, delimiter=',',
  comments='#', skiprows=4)` para leer los valores después de los comentarios y encabezado.

## Rendimiento y estructura

`dist/physics.js` contiene el modelo numérico sin dependencias. `dist/app.js` crea
un Web Worker mediante Blob (compatible con apertura local) y conserva tablas
de campo y flujo por geometría. Cambiar la inclinación, vueltas, resistencias o
campo central aprovecha esas tablas. La animación usa `requestAnimationFrame`
y Canvas; fondos y gráficas se reutilizan durante la reproducción. En navegadores
que bloquean Workers se usa un modo compatible en el hilo principal.

`dist/style.css` y `dist/index.html` completan la interfaz adaptable a escritorio y
móvil. La publicación privada usa Sites, con identidad en `.openai/hosting.json`.

## Verificación numérica

```bash
python3 simulacion_web/verificar_modelo.py
```

El contraste ejecuta Node.js y NumPy sobre ocho casos y 17 magnitudes, incluyendo
las series completas, campo y ángulo nulos, sonda ×10 y cambios de geometría.
La tolerancia es `rtol=2e-8`, `atol=1e-11`.
