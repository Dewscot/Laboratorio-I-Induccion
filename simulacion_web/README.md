# Inducción · versión web

Abrir **`dist/index.html`** en Firefox, Chrome o Chromium. No requiere instalación,
servidor, Python, Matplotlib, conexión a internet ni bibliotecas externas.

También se puede servir desde esta carpeta:

```bash
python3 -m http.server 8000 --directory dist
```

Luego visitar `http://localhost:8000`.

## Geometría utilizada

Esta versión conserva el campo lateral de `Simulacion 2`, con dos bobinas
fijas a los costados del riel, y usa una **captadora circular** vertical en el
plano longitudinal. La trayectoria permanece en el plano medio y el riel gira
alrededor del centro de las bobinas. La normal de la captadora es transversal;
no se aplica un factor adicional `cos(theta)`.

Los controles **Número de vueltas** y **Radio de la captadora** permiten probar
otras bobinas. Valores iniciales: **50 vueltas y radio de 4 cm**, estimados por
el usuario para la captadora provisional; el radio es medio, no el diámetro.
Admite radios de 0,1 a 40 cm y números enteros positivos de vueltas.
El dibujo, el área indicada, las señales y el CSV usan esos mismos parámetros.

El modelo aproxima el bobinado compacto como N vueltas coincidentes, sin núcleo,
de área `πr²`. El flujo por vuelta integra el campo sobre el disco encerrado
(aunque el centro esté vacío), con cuadratura polar de 24 nodos radiales y
96 posiciones angulares. Faraday usa `fem = -N (dΦ/ds) v`. El campo se obtiene
por Biot–Savart y se normaliza al B₀ introducido. Un radio mayor puede cambiar
la forma de los pulsos, además de su amplitud.

El campo, las resistencias y las dimensiones de las bobinas grandes siguen
siendo ejemplos: deben medirse para comparar amplitudes experimentales. Al
cambiar de captadora hay que actualizar su resistencia propia. Se omiten
espesor del bobinado, ruido, pérdidas mecánicas e inductancia. Geometrías con
bobinas muy próximas y captadoras grandes pueden necesitar refinamiento de la
cuadratura; la verificación cubre los casos indicados en el script, no todas
las combinaciones posibles.

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

El contraste ejecuta Node.js y NumPy. Compara flujo y gradiente espacial con
una integración independiente por franjas cartesianas sobre el disco y un
campo de Biot–Savart más fino. Incluye la captadora provisional, radios mayores,
el radio mínimo, bobinas pequeñas, proporcionalidad con las vueltas, dependencia
angular, campo/ángulo nulos y entradas inválidas. Tolerancias normalizadas por
el máximo de cada perfil: 0,03 % para flujo y 0,5 % para gradiente.
