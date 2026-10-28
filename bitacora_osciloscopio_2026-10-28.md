# Bitácora: configuración del osciloscopio

Fecha: 28 de octubre de 2026.

## Contexto y decisiones

Se conversó sobre la configuración inicial del Hameg HM 203-7 para observar los pulsos de inducción producidos por el paso de la espira en el experimento del plano inclinado. Se decidió utilizar como máximo un canal: CH I.

Estos son ajustes iniciales propuestos; todavía no se ha confirmado la amplitud ni la duración de la señal experimental.

## Conexión y escalas propuestas

- Conectar CH I en paralelo con la resistencia de carga, con la masa en la referencia del circuito. La masa del osciloscopio está conectada a tierra de protección.
- Utilizar sonda ×1 o conexión directa para aprovechar la amplitud de una señal pequeña.
- Poner el acoplamiento de entrada de CH I en DC para conservar la forma de los pulsos lentos.
- Comenzar en 5 mV/div. Si la señal es muy pequeña, activar MAG ×5 de CH I: la escala efectiva pasa a 1 mV/div.
- Centrar la línea de cero para dejar espacio a pulsos de ambas polaridades.
- Ajustar la sensibilidad para ver la señal completa, idealmente con unas 4–6 divisiones de altura total, sin recortarla.
- Mantener los ajustes finos vertical y temporal en CAL para que las escalas indicadas sean válidas.

## Los dos mandos de TIME/DIV

Se aclaró que el selector grande exterior fija la escala por pasos y el mando pequeño central permite un ajuste fino.

1. Colocar el selector grande en **50 ms/div**: el número 50 de la zona de milisegundos, a la izquierda, entre 20 y 100. No confundirlo con 50 µs.
2. Girar el mando pequeño central al tope hacia la izquierda, sin forzarlo, hasta la posición CAL.
3. Dejar X-MAG ×10 sin pulsar para conservar la escala horizontal indicada.

Los 50 ms/div se propusieron como punto de partida basado en la simulación. Ajustar después para ver completos los pulsos de entrada y salida.

## Botones para trabajar con un solo canal

| Control | Estado propuesto |
| --- | --- |
| CH I/II | Sin pulsar: seleccionar CH I |
| DUAL | Sin pulsar |
| ADD | Sin pulsar |
| X-Y | Sin pulsar |
| X-MAG ×10 | Sin pulsar |
| MAG ×5 de CH I | Pulsar solamente si hace falta más sensibilidad |
| AT/NORM | Sin pulsar (AUTO) para localizar la línea base; pulsar (NORMAL) para disparar con el pulso |
| EXT | Sin pulsar, para utilizar disparo interno |

Para el disparo se propuso fuente CH I y acoplamiento DC. Ajustar LEVEL por encima del ruido y dentro de la amplitud del primer pulso; seleccionar el flanco según su polaridad. En modo NORMAL puede no verse traza mientras no llegue un disparo válido.

## Registro de la señal

El HM 203-7 es analógico y no guarda la traza. Se sugirió grabar la pantalla en vídeo durante los lanzamientos y repetir las mediciones. Medir primero el ruido y la línea base con el mismo cableado y las mismas escalas.

## Imagen guardada

A pedido del usuario se extrajo el esquema del panel frontal del manual y se copió a esta carpeta:

[panel_osciloscopio_HM203-7.png](panel_osciloscopio_HM203-7.png)

La imagen es un esquema de ubicación de los controles del manual; **no muestra los mandos colocados en los ajustes propuestos** ni lleva anotaciones añadidas.

## Fuentes consultadas

- Manual local: `documentos/referencias/Hameg - HM203-7, Manual Esp.pdf`. El esquema del panel se extrajo de la página 23 del PDF.
- [Instrucciones breves del fabricante reproducidas en ManualsLib](https://www.manualslib.com/manual/3288230/Hameg-Hm-203-7.html?page=21): ajuste fino temporal en CAL al tope izquierdo y funcionamiento de los controles.
- `SIMULACION.md`: parámetros iniciales orientativos para el experimento.

## Pendiente de comprobar en el laboratorio

Observar una pasada real para ajustar sensibilidad, base de tiempo, nivel y flanco de disparo. En esta conversación no se aportó una captura de la señal ni se confirmó que los ajustes ya se hubieran aplicado al instrumento.
