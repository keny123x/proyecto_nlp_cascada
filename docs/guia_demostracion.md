# Guía de demostración de Opinómetro

## Preparación

1. Ejecutar instalación del README y comprobar las pruebas.
2. Iniciar API y frontend en dos terminales.
3. Abrir http://127.0.0.1:5173; verificar «MODELO REAL · API CONECTADA».
4. Abrir métricas y comprobar 93,5 % de exactitud y 200 reseñas de prueba.

## Recorrido sugerido para Angela

1. Portada: explicar el análisis de opiniones hoteleras en español.
2. Cargar y analizar el ejemplo negativo. Diferenciar probabilidad por reseña
   de exactitud del modelo sobre el conjunto de prueba.
3. Recorrer normalización, tokens, stop words y stemming. Mostrar las
   negaciones conservadas y explicar que las raíces no son lemas.
4. Usar reproducción y navegación manual. La API ya devolvió todos los datos;
   la animación solo los presenta en secuencia.
5. Editar la reseña: explicar por qué los resultados no cambian hasta enviarla.
6. Analizar dos o tres reseñas en lote y abrir el detalle de una fila.
7. Mostrar matriz de confusión y experimentos. Filas = clase real; columnas =
   predicha. Distinguir experimentos del modelo final optimizado.

## Cómo se conecta

`main.js` envía texto mediante `services/api.js`. FastAPI carga el pipeline y
devuelve JSON. `result.js` presenta probabilidades, `laboratory.js` los pasos,
`batch.js` la tabla y `metrics.js` la evaluación. Los textos del usuario se
insertan con `textContent`, sin ejecutar HTML. CSS controla el diseño y los
movimientos. El navegador no replica la limpieza del modelo.

## Cambios pequeños para practicar

- Mostrar un dato adicional de `/status`.
- Cambiar la presentación de una métrica en `metrics.js`.
- Ajustar los colores mediante variables al inicio de `styles.css`.
- Modificar un ejemplo en `main.js` y justificar su elección.

## Revisión de entrega del equipo

- Revisar cambios locales y registrar commits propios con autoría real.
- Verificar que `CONTRIBUCIONES.md` coincida con el historial.
- Abrir un pull request y obtener revisión antes de integrar.
- Verificar informe, procedencia/licencia de datos, análisis de errores,
  diapositivas y declaración de IA; esta guía no los reemplaza.
- Crear `entrega-final` sobre el commit que el equipo decida entregar.
- Probar una clonación limpia siguiendo el README antes de presentar.

No se han publicado ni integrado los cambios del frontend en la rama principal.
