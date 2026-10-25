# Experimento: corriente inducida por un carro en un plano inclinado

## 1. Resumen del experimento

El experimento busca estudiar cómo cambia la corriente inducida en un circuito cuando se modifica la velocidad con la que un carro se aproxima a una región de campo magnético.

El montaje consiste en un carro de masa \(m\) que se mueve sobre un plano inclinado un ángulo \(\theta\). La distancia recorrida por el carro antes de llegar a la zona de interacción electromagnética se mantiene fija, mientras que el ángulo \(\theta\) del plano se modifica entre mediciones. Al variar \(\theta\), cambia la componente de la gravedad paralela al plano y, por tanto, la aceleración y la velocidad con la que el carro llega a la región de la bobina.

La bobina de Helmholtz se mantiene con una geometría y una orientación fijas durante todo el experimento. La señal eléctrica inducida se registra mediante un osciloscopio.

La **variable independiente** será el ángulo de inclinación del plano,

\[
\theta,
\]

mientras que la **variable dependiente** será la señal de corriente inducida,

\[
I(t;\theta),
\]

o alguna magnitud obtenida de ella, por ejemplo su valor máximo \(I_{\max}(\theta)\), si ese es el observable utilizado para comparar las distintas mediciones.

El problema se modelará inicialmente como un sistema unidimensional, tomando un eje \(x\) paralelo al plano inclinado.

---

## 2. Objetivo general

Estudiar experimentalmente la relación entre el ángulo de inclinación \(\theta\) del plano, la velocidad del carro al alcanzar la región de interacción magnética y la corriente inducida medida por el osciloscopio.

En forma esquemática, el experimento estudia la cadena

\[
\boxed{
\theta
\longrightarrow
a(\theta)
\longrightarrow
v(\theta)
\longrightarrow
\frac{d\Phi_B}{dt}
\longrightarrow
\mathcal{E}
\longrightarrow
I
}
\]

donde \(\Phi_B\) es el flujo magnético y \(\mathcal{E}\) es la fuerza electromotriz inducida.

---

# 3. Marco teórico

## 3.1. Dinámica del carro sobre el plano inclinado

Se considera un eje \(x\) paralelo al plano inclinado y orientado en el sentido del movimiento del carro.

El peso del carro es

\[
\vec{P}=m\vec{g}.
\]

La componente del peso paralela al plano es

\[
P_x = mg\sin\theta.
\]

Si inicialmente se desprecia el rozamiento y cualquier otra fuerza paralela al movimiento, la segunda ley de Newton da

\[
ma = mg\sin\theta.
\]

Por lo tanto,

\[
\boxed{a(\theta)=g\sin\theta}.
\]

En este modelo ideal la masa del carro se cancela, por lo que la aceleración no depende de \(m\).

Si en el montaje existen fuerzas de resistencia mecánica apreciables, el modelo deberá modificarse. Por ejemplo, para una fuerza resistiva \(F_r\) opuesta al movimiento,

\[
ma = mg\sin\theta-F_r,
\]

y entonces

\[
a = g\sin\theta-\frac{F_r}{m}.
\]

La forma exacta de \(F_r\) dependerá del mecanismo dominante de rozamiento.

---

## 3.2. Movimiento unidimensional del carro

Suponiendo aceleración constante y utilizando únicamente el eje paralelo al plano, la posición del carro está descrita por

\[
x(t)=x_0+v_0t+\frac{1}{2}a t^2,
\]

mientras que su velocidad es

\[
v(t)=v_0+at.
\]

Como la distancia recorrida \(L\) será fija para todas las mediciones, resulta especialmente útil la ecuación cinemática

\[
v_f^2=v_0^2+2aL.
\]

Utilizando

\[
a=g\sin\theta,
\]

se obtiene

\[
\boxed{
v_f(\theta)=
\sqrt{v_0^2+2gL\sin\theta}
}.
\]

Si el carro parte aproximadamente desde el reposo,

\[
v_0\simeq0,
\]

entonces

\[
\boxed{
v_f(\theta)=\sqrt{2gL\sin\theta}
}.
\]

Esta expresión muestra que aumentar el ángulo del plano aumenta la velocidad con la que el carro alcanza la región de interacción magnética.

---

## 3.3. Flujo magnético

El flujo magnético a través de una superficie \(S\) se define como

\[
\Phi_B =
\int_S \vec{B}\cdot d\vec{A}.
\]

Si el campo pudiera considerarse aproximadamente uniforme sobre una superficie plana,

\[
\Phi_B = BA\cos\alpha,
\]

donde

- \(B\) es el módulo del campo magnético,
- \(A\) es el área efectiva de la espira o circuito,
- \(\alpha\) es el ángulo entre el campo magnético y el vector normal a la superficie.

En el montaje experimental la geometría y la inclinación de la bobina se mantienen fijas. Por lo tanto, la variación temporal del flujo se deberá principalmente al movimiento relativo del carro respecto de la región magnética.

En general puede escribirse el flujo como una función de la posición:

\[
\Phi_B=\Phi_B(x).
\]

La forma explícita de \(\Phi_B(x)\) dependerá de la geometría concreta del montaje y de la distribución espacial del campo magnético.

---

## 3.4. Ley de Faraday-Lenz

La ley de Faraday establece que la fuerza electromotriz inducida es

\[
\boxed{
\mathcal{E}=-N\frac{d\Phi_B}{dt}
}
\]

para una bobina de \(N\) espiras.

El signo negativo representa la ley de Lenz: la corriente inducida aparece en un sentido tal que se opone al cambio de flujo que la produce.

Como en este experimento el flujo cambia debido al movimiento del carro, puede utilizarse la regla de la cadena:

\[
\frac{d\Phi_B}{dt}
=
\frac{d\Phi_B}{dx}
\frac{dx}{dt}.
\]

Como

\[
\frac{dx}{dt}=v,
\]

se obtiene

\[
\boxed{
\mathcal{E}
=
-N\frac{d\Phi_B}{dx}v
}.
\]

Esta relación es especialmente importante para el experimento porque conecta directamente la parte mecánica con la parte electromagnética.

---

## 3.5. Relación entre velocidad y corriente inducida

Si el circuito donde se mide la corriente puede aproximarse como puramente resistivo, con resistencia efectiva \(R\), la ley de Ohm permite escribir

\[
I=\frac{\mathcal{E}}{R}.
\]

Por tanto,

\[
\boxed{
I
=
-\frac{N}{R}
\frac{d\Phi_B}{dx}
v
}.
\]

La corriente inducida depende entonces de dos factores principales:

1. la rapidez con que el carro atraviesa la región de variación del flujo magnético;
2. la variación espacial del flujo, \(d\Phi_B/dx\), determinada por la geometría y el campo del montaje.

Si la geometría, la bobina, la resistencia y la trayectoria permanecen fijas entre experimentos, el factor

\[
-\frac{N}{R}\frac{d\Phi_B}{dx}
\]

estará determinado principalmente por la posición. El cambio controlado entre mediciones será la velocidad producida al modificar \(\theta\).

---

## 3.6. Dependencia esperada con el ángulo del plano

Para una distancia fija \(L\) y un carro que parte aproximadamente del reposo,

\[
v_f(\theta)=\sqrt{2gL\sin\theta}.
\]

Combinando esta expresión con la ley de Faraday,

\[
I
=
-\frac{N}{R}
\frac{d\Phi_B}{dx}
v,
\]

se espera que una mayor inclinación produzca una mayor velocidad y, en consecuencia, una mayor rapidez de cambio del flujo magnético.

Bajo la aproximación adicional de que el factor espacial \(d\Phi_B/dx\) relevante para el máximo de la señal es el mismo en todas las mediciones, se obtiene como predicción cualitativa

\[
I_{\max}\propto v_f.
\]

Por lo tanto,

\[
\boxed{
I_{\max}(\theta)
\propto
\sqrt{\sin\theta}
}
\]

para el modelo ideal con \(v_0=0\).

Esta proporcionalidad es una hipótesis experimental que puede ponerse a prueba mediante los datos obtenidos.

---

## 3.7. Forma temporal de la señal

El osciloscopio no necesariamente mostrará una corriente constante. En general registrará una señal

\[
I(t;\theta)
=
-\frac{N}{R}
\frac{d\Phi_B}{dx}\bigg|_{x=x(t)}
v(t).
\]

La forma de la curva depende de cómo cambia el flujo magnético con la posición.

Por esta razón, para comparar distintos ángulos pueden utilizarse observables como

\[
I_{\max},
\]

el tiempo durante el cual aparece la señal, el ancho temporal del pulso o, si corresponde, el voltaje medido en una resistencia conocida y convertido posteriormente a corriente.

---

# 4. Variables experimentales

### Variable independiente

\[
\boxed{\theta}
\]

Ángulo de inclinación del plano.

### Variable dependiente

\[
\boxed{I(t;\theta)}
\]

Corriente inducida registrada a partir de la señal del osciloscopio.

Para realizar una comparación escalar entre experimentos puede utilizarse, por ejemplo,

\[
\boxed{I_{\max}(\theta)}.
\]

### Variables que deberían mantenerse controladas

- Distancia \(L\) recorrida por el carro.
- Masa y configuración del carro.
- Posición y orientación de la bobina.
- Geometría del circuito.
- Número de espiras \(N\).
- Resistencia efectiva \(R\).
- Condición inicial de liberación del carro.
- Trayectoria del carro respecto de la bobina.
- Configuración y escala del osciloscopio.

---

# 5. Hipótesis de trabajo

Si se aumenta el ángulo de inclinación \(\theta\), aumenta la componente de la gravedad paralela al plano,

\[
mg\sin\theta,
\]

por lo que el carro adquiere una mayor velocidad antes de llegar a la región de interacción magnética.

Una mayor velocidad produce una variación temporal más rápida del flujo magnético,

\[
\left|\frac{d\Phi_B}{dt}\right|,
\]

lo que, de acuerdo con la ley de Faraday, aumenta la magnitud de la fuerza electromotriz inducida y, para un circuito con resistencia aproximadamente constante, la magnitud de la corriente inducida.

El modelo ideal predice aproximadamente

\[
\boxed{
I_{\max}(\theta)
\propto
\sqrt{\sin\theta}
}.
\]

---

# 6. Observaciones sobre el modelo

Este marco teórico corresponde a una primera aproximación unidimensional. Para comparar cuantitativamente el modelo con los datos experimentales puede ser necesario incorporar posteriormente:

- rozamiento del carro;
- resistencia de rodadura;
- inductancia propia del circuito;
- resistencia interna de la bobina y de los instrumentos;
- distribución espacial real del campo magnético;
- orientación exacta entre la bobina, el campo y la trayectoria;
- posibles cambios en la velocidad durante la región de interacción;
- incertidumbre en \(\theta\), \(L\), corriente y tiempo.

En particular, antes de obtener una expresión completamente explícita para \(I(t;\theta)\) será necesario especificar cómo depende el flujo magnético \(\Phi_B\) de la posición \(x\) en el montaje real.
