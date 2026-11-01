# Reseñas de demostración para que el Frontend (Integrante 4) tenga botones de prueba.
# Incluyen casos con tildes, mayúsculas, signos, URLs y negaciones para lucir el paso a paso del NLP.
EJEMPLOS = [
    {
        "categoria": "hotel",
        "sentimiento_esperado": "Positivo",
        "texto": "¡Excelente hotel! Las habitaciones estaban limpísimas y el personal fue muy amable.",
    },
    {
        "categoria": "hotel",
        "sentimiento_esperado": "Negativo",
        "texto": "El hotel estaba sucio y NO lo recomiendo para nada.",
    },
    {
        "categoria": "restaurante",
        "sentimiento_esperado": "Positivo",
        "texto": "La comida estuvo deliciosa y el servicio fue rápido. ¡Volveremos pronto!",
    },
    {
        "categoria": "restaurante",
        "sentimiento_esperado": "Negativo",
        "texto": "Esperamos 45 minutos y la sopa llegó fría. Pésima atención.",
    },
    {
        "categoria": "producto",
        "sentimiento_esperado": "Positivo",
        "texto": "Compré este celular en www.tienda.com y funciona perfecto, muy buena calidad.",
    },
    {
        "categoria": "producto",
        "sentimiento_esperado": "Negativo",
        "texto": "El producto llegó roto y nunca respondieron mis mensajes.",
    },
]
