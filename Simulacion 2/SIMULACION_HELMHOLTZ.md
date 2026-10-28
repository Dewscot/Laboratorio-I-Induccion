# Simulación de inducción: bobinas a los lados del riel

**Archivo:** `simulacion_induccion_helmholtz.py`

## Ejecutar

Desde la carpeta del proyecto en VS Code:

```bash
python simulacion_induccion_helmholtz.py
```

No requiere instalar paquetes adicionales si el entorno ya tiene **NumPy** y **Matplotlib**.

Para generar archivos sin abrir la ventana:

```bash
python simulacion_induccion_helmholtz.py --exportar --angulo 17.5 --vueltas 10
python simulacion_induccion_helmholtz.py --comparar
```

La simulación genera PNG, CSV y JSON en `resultados_simulacion_helmholtz/`. Se trata de **predicciones** del modelo; **no son mediciones experimentales**.

Para verificar cálculos:

```bash
python -m unittest -v test_simulacion_helmholtz
```

## Geometría del nuevo montaje

- **Vista superior:** hay una bobina de Helmholtz a cada lado del riel. El eje común de las bobinas apunta **a través** del riel, de una bobina hacia la otra, perpendicular al sentido de avance del carrito.
- Las bobinas se mantienen fijas. El riel se inclina **girando alrededor del centro geométrico** entre las bobinas, y continúa pasando por dicho centro y por el **plano medio** entre ambas.
- La **espira captadora móvil** tiene un plano vertical y longitudinal, es decir, paralelo al plano vertical del riel. Su **normal** está orientada según el eje de Helmholtz, de modo que no cambia la proyección del campo por el mero hecho de inclinar el riel.
- La espira captadora se aproxima por un **rectángulo** sin núcleo y con varias vueltas equivalentes. Si finalmente les prestan una bobina circular, habrá que modificar la integral de área y actualizar las dimensiones.

Si en la realidad el riel gira alrededor de un extremo, y no alrededor del centro entre las bobinas, el carrito puede alejarse del centro al inclinarlo. El modelo actual **no contempla ese desplazamiento**. Tampoco modela un cambio de orientación de la espira fuera del plano medio.

## Física modelada

El carrito parte desde el reposo y se mueve con

\[
a=g\sin\theta, \qquad s(t)=\tfrac12 at^2,\qquad v(t)=at.
\]

Para el campo se calcula numéricamente la **componente transversal** de `B` en el plano medio de dos anillos coaxiales de radio `R` separados una distancia `D`, con corrientes iguales y del mismo sentido. Se integra la ley de Biot–Savart a lo largo de los anillos, normalizando el resultado para que en el centro sea el `B0` introducido por el usuario.

Luego se integra el campo **sobre el área de la espira rectangular**, y se obtiene la fem y el voltaje de carga:

\[
\Phi_B(s)=\iint_{S(s)}\vec B\cdot d\vec S,\qquad
\mathcal E(t)=-N_e\frac{d\Phi_B}{ds}v(t),\qquad
V_R\simeq\frac{R_{\mathrm{ef}}}{r_e+R_{\mathrm{ef}}}\mathcal E.
\]

La resistencia efectiva `R_ef` incluye la carga en paralelo con la impedancia de entrada idealizada del osciloscopio.

## Campos ajustables

| Parámetro | Significado |
|---|---|
| Campo central `B0` (mT) | Supuesto o medición del campo en el centro; **no se calcula automáticamente** desde corriente y vueltas de las bobinas grandes |
| Radio `R` (cm) | Radio de los aros de Helmholtz |
| Separación `D` (cm) | Distancia entre ambos aros; para Helmholtz ideal, `D = R` |
| Vueltas captadoras | Número de vueltas de la **espira que viaja sobre el carrito** |
| Ancho/largo captador | Dimensiones de la espira rectangular en su propio plano |
| Resistencias | Resistencia propia de la espira y carga sobre la que se mide tensión |
| Sonda | Atenuación ×1 / ×10 |
| Inclinación | Modifica la velocidad ideal mediante `sin(theta)` |

Las medidas iniciales (radio 15 cm, 10 vueltas, campo central de 1 mT, espira de 10×10 cm) son **solo ejemplos**, no características confirmadas del laboratorio.

## Qué se debe esperar

No existe un borde artificial de campo uniforme: su variación es suave. La curva `B_perp(s)` es aproximadamente plana cerca del centro y disminuye hacia los extremos. En puntos lejanos puede cambiar de signo, ya que el campo magnético retorna fuera de las bobinas; eso puede originar rasgos pequeños adicionales en el voltaje.

En el modelo, el pico principal antes del centro y el posterior tienen signos opuestos. El signo absoluto depende de la orientación elegida para la normal y de las conexiones reales del osciloscopio.

Si se conserva toda la geometría al inclinar el riel, el modelo predice aproximadamente

\[
U_{\rm pk}\propto\sqrt{\sin\theta}.
\]

**Importante:** este resultado requiere que la trayectoria y la orientación de la espira sean equivalentes para todos los ángulos. Si cambia el centro de cruce o la posición vertical respecto de las bobinas, esta relación puede dejar de cumplirse.

## Limitaciones experimentales

La simulación no contempla fricción, inercia de las ruedas, frenado magnético, inductancia y capacitancia del circuito móvil, fuerzas por los cables, estructura real de las bobinas ni ruido/interferencias. El indicador en divisiones del Hameg HM203-7 es una referencia de escala de visualización, **no una garantía de que pueda detectarse el pulso**. Deben hacer una prueba real de amplitud, ruido y disparo.
