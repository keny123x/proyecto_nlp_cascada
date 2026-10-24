import os
import pandas as pd

print("🔄 Descargando 1,000 reseñas REALES en español...")
url = "https://githubusercontent.com"

try:
    os.makedirs('data', exist_ok=True)
    df = pd.read_csv(url)
    df = df[['texto', 'sentimiento']].head(1000)
    df.to_csv('data/resenas.csv', index=False, encoding='utf-8')
    print("\n✅ ¡Completado! Archivo 'data/resenas.csv' creado con éxito.")
    print(f"📊 Distribución de clases reales (0=Negativo, 1=Positivo):\n{df['sentimiento'].value_counts()}")
except Exception as e:
    print(f"❌ Ocurrió un error al descargar los datos reales: {e}")
