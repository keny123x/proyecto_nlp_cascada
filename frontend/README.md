# Opinómetro · Analizador conectado (versión local completa)

HTML, CSS y JavaScript modular, sin instalación de paquetes. Desde la raíz:

```powershell
python -m http.server 5173 --bind 127.0.0.1 --directory frontend
```

Abrir http://127.0.0.1:5173. No abrir index.html directamente con file://.

## Alcance de esta versión

- Portada original con burbujas y órbitas animadas mediante CSS.
- Diseño adaptable, navegación por teclado y movimiento reducido.
- Ejemplos de reseñas, contador, limpieza y pestañas individual/lotes.
- Recorrido NLP real por reseña, con negaciones, stop words y pares palabra/raíz.
- Métricas de la API, matriz de confusión y comparación de experimentos.
- Análisis de hasta 50 reseñas por lote y selección de detalles.

La interfaz consulta `/status`, `/predict`, `/predict/lote` y `/metrics`. Para usarlo, iniciar
FastAPI siguiendo `docs/base_frontend.md`. La URL se configura en
`src/services/api.js` y por defecto es `http://127.0.0.1:8000`.
La tarjeta de resultado y el laboratorio comienzan vacíos. La API proporciona
las probabilidades y todas las etapas NLP. Se identifica modo real/simulado,
y se advierte si el formulario cambia tras la última predicción.

`src/styles.css` concentra los tokens visuales y estilos; `src/main.js` coordina
las interacciones, `src/services/api.js` las peticiones y
`src/components/result.js` los estados y resultados, y
`src/components/laboratory.js` el recorrido NLP y su reproducción. Las fuentes de Google
tienen alternativas locales sans-serif. `batch.js` gestiona la tabla de lotes y
`metrics.js` el panel de evaluación; `dom.js` contiene elementos seguros compartidos.

## Verificación del bloque 1

Revisado en navegador a 1440 y 390 píxeles: sin desbordamiento horizontal.
Comprobados carga de ejemplos y contador, limpieza, cambio individual/lotes y
selección de etapas NLP. Sin errores de consola capturados. JavaScript validado
con `node --check`. La conexión real con FastAPI queda para el bloque 2.

## Verificación del bloque 2

En navegador contra FastAPI: validación de vacío, ejemplo negativo (98,8 %),
ejemplo positivo (99,1 %), aviso al editar el texto tras obtener un resultado,
API desconectada y API iniciada sin modelo (modo simulado explícito, 90/10).
El botón se desactiva durante la petición; limpiar invalida una respuesta en
curso. Las peticiones tienen límite de espera de 20 segundos. Las respuestas
se muestran como texto, sin interpretar HTML del usuario.


## Verificación del bloque 3

Comprobados contra la API real: normalización de signos/URLs/números, tokens,
stop words eliminadas, conservación de no/nunca y pares palabra/raíz. Verificados
reproducción y pausa, avance/retroceso, aviso al editar, reinicio al limpiar y
estado vacío cuando solo se ingresan stop words. Todos los textos de la API se
insertan mediante textContent; no se interpretan como HTML. La reproducción
visual recorre datos ya recibidos y no representa ejecución del servidor en vivo.


## Verificación del bloque 4

Lote real de tres reseñas, conteos por clase, probabilidades y selección de una
fila con actualización de resultado/NLP. Límite de 50 reseñas validado antes de
enviar; máximo 2000 caracteres por reseña y líneas en blanco omitidas.
Métricas reales: exactitud, F1 ponderado, 200 muestras de prueba, matriz de
confusión (187 aciertos / 13 errores), cuatro experimentos y configuración final.
Probados también artefacto de métricas ausente (modo simulado y campos no
disponibles) y API desconectada con reintento. Las métricas no dependen de las
reseñas ingresadas por el usuario.


## Acabado y verificación final

Navegación fija con las tres secciones en móvil; control para pausar movimiento,
respeto de prefers-reduced-motion y atajo Ctrl+Enter. Fuentes alternativas si
Google Fonts no carga. Los porcentajes ilustrativos ya no están en el HTML.
Comprobación del backend con iniciar.ps1 tests: 22 pruebas aprobadas (un aviso
no bloqueante de deprecación de Starlette/httpx). JavaScript validado con
node --check. Comandos de instalación e inicio: README de la raíz.

La versión permanece local, pendiente de revisión, commits y pull request.


## Transformación visual palabra por palabra

Cada etapa del laboratorio ilumina y amplía las palabras en secuencia. Las
stop words se atenúan y tachan; las negaciones se conservan en coral y el
stemming muestra el par palabra/raíz. Se puede pausar, repetir el paso, elegir
velocidad y reproducir el recorrido completo. Cambiar de etapa, limpiar o enviar
otra reseña cancela la secuencia anterior. La reproducción espera a que termine
cada etapa antes de avanzar. Con movimiento reducido o pausa global se muestran
todos los datos sin animación. No se modifica ni recalcula el NLP en JavaScript.


### Diferencia entre normalización y tokenización

La normalización conserva una frase continua. Anima los snapshots que expone
Python en `pasos.normalizacion_etapas`: minúsculas, retirada de URLs, tildes,
signos/números/emojis y espacios. Los fragmentos eliminados desaparecen y se
recompone la frase. No aparecen casillas de tokens en esta etapa.

La tokenización parte de la frase normalizada: las palabras viajan, en orden,
hacia casillas inicialmente vacías. Sus destinos usan los tokens de la API.
Ambas escenas respetan pausa, velocidad, repetición y movimiento reducido.
La API conserva los campos previos; el nuevo campo es adicional y opcional.
Pruebas del backend tras esta ampliación: 23 aprobadas.
