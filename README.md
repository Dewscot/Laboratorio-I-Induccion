# Laboratorio-I-Induccion
Experimento de inducción electromagnética mediante una espira móvil y bobinas de Helmholtz

Simulación interactiva sencilla (riel de 150 cm y comparación con el Hameg HM 203-7):

```bash
python simulacion_induccion.py
```

Instrucciones, aproximaciones y ejemplos en [SIMULACION.md](SIMULACION.md).

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
