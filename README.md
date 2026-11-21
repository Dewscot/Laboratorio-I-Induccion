# Laboratorio-I-Induccion
Experimento de inducción electromagnética mediante una espira móvil y bobinas de Helmholtz

[Bitácora única de trabajo](BITACORA_UNICA.md): modelo, simulador web,
osciloscopio, decisiones, mediciones y pendientes. Actualizar este documento
conforme avance el experimento. Es la única bitácora activa; los registros anteriores
se conservan en [un respaldo histórico ZIP](documentos/archivo/antecedentes_2026-11-03.zip).

Versión web con animación en Canvas, bobinas **a los costados del riel**, campo
suave de Biot–Savart, captadora circular de radio y vueltas ajustables
(inicialmente 4 cm y 50 vueltas) y vista de escalas del Hameg: abrir
[simulacion_web/dist/index.html](simulacion_web/dist/index.html) en el navegador.
Funciona sin instalación ni conexión a internet. Véanse
[las instrucciones y supuestos](simulacion_web/README.md).

[Versión web publicada (acceso privado)](https://induccion-espira-laboratorio.candycurl2.chatgpt.site):
versión anterior; la adaptación circular del 03-11 está disponible localmente.

Versión anterior en Matplotlib, con campo uniforme de bordes definidos y una
geometría distinta (conservada como referencia):

```bash
python simulacion_induccion.py
```

Instrucciones, aproximaciones y ejemplos en [SIMULACION.md](SIMULACION.md).

## Informe y análisis experimental

### Cambios de esta versión

- El informe incorpora el montaje, el procedimiento, las tablas de resultados y
  la discusión de los residuos. Las tablas se editan en el mismo archivo.
  [Informe en LaTeX](main.tex).
- Los dos TXT guardan el ángulo en grados y el voltaje en mV, con una fila por
  pasada. Para 5° a 9° se usaron `Rep1.1` y `Rep2.1`, tomadas después de
  recentrar el riel. De 10° a 15° se usaron `Rep1` y `Rep2`.
  [Picos positivos](analisis/picos_positivos.txt) · [Picos negativos](analisis/picos_negativos.txt).
- El script lee los TXT con `np.genfromtxt`, promedia las pasadas por ángulo y
  compara tres modelos con `curve_fit`.
  [Script](analisis/analisis_induccion.py) · [Ajustes](figuras/ajustes.pdf) · [Residuos](figuras/residuos.pdf).

Para regenerar los gráficos, ejecuten este comando desde la raíz del repositorio.

    python analisis/analisis_induccion.py

Si cambian los TXT, revisen también las tablas y los valores comentados en
`main.tex`. [Instrucciones del análisis](analisis/LEEME.txt).
Queda por completar la portada y cuantificar la incertidumbre instrumental del
osciloscopio.

## Compilación de documentos LaTeX

### VS Code y LaTeX Workshop (recomendado)

1. Abrir **la carpeta completa del repositorio** en VS Code (`Archivo > Abrir carpeta`), no únicamente un archivo `.tex`.
2. Tener instalada una distribución LaTeX que incluya `latexmk` y la extensión **LaTeX Workshop**.
3. Abrir `main.tex` o `guia_mediciones_induccion.tex`. La configuración compartida en `.vscode/settings.json` compila al guardar y también permite usar la receta **latexmk (PDF)** desde LaTeX Workshop.

Los archivos generados (PDF y auxiliares) se guardan por documento:

- `main.tex` → `.latex-build/main/main.pdf`
- `guia_mediciones_induccion.tex` → `.latex-build/guia_mediciones_induccion/guia_mediciones_induccion.pdf`

La carpeta `.latex-build/` está excluida de Git mediante `.gitignore`.

### Otros editores o terminal

Si el editor utiliza `latexmk` y se ejecuta desde la raíz del repositorio, el archivo `latexmkrc` establece `.latex-build/` como salida predeterminada. Por ejemplo:

```bash
latexmk -pdf main.tex
```

Ese comando no requiere LaTeX Workshop, pero deposita la salida directamente en `.latex-build/`, sin una subcarpeta por documento. Quien necesite el mismo esquema de subcarpetas puede indicar expresamente `-outdir`.

La configuración `latexmkrc` **no se aplica** si se ejecuta `pdflatex` directamente sin pasar por `latexmk`.

Para conservar o compartir una versión final, copiar el PDF elegido a `entregables/`. No añadir al repositorio los archivos auxiliares ni las compilaciones temporales.
