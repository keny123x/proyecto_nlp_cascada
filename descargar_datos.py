import os
import pandas as pd

# Rest-Mex 2025: reseñas reales de TripAdvisor (turismo en México), licencia CC BY 4.0
URL = "https://huggingface.co/datasets/vg055/Rest-Mex2025/resolve/main/Rest-Mex_2025_train.csv"
N_POR_CLASE = 500  # 500 negativas + 500 positivas = 1,000 reseñas balanceadas

def reparar_codificacion(texto):
    """El CSV original mezcla filas UTF-8 y Latin-1: repara las que quedaron mal leídas."""
    if not isinstance(texto, str):
        return ''
    for _ in range(3):  # algunas filas vienen doblemente codificadas
        try:
            texto = texto.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return texto

print("🔄 Descargando reseñas REALES de hoteles en español (Rest-Mex 2025)...")

try:
    os.makedirs('data', exist_ok=True)
    df = pd.read_csv(URL, encoding='latin-1')

    # 1. Solo reseñas de hoteles
    df = df[df['Type'] == 'Hotel']

    # 2. Estrellas -> sentimiento binario (3 estrellas = neutral, se descarta)
    df = df[df['Polarity'] != 3]
    df['sentimiento'] = (df['Polarity'] >= 4).astype(int)

    # 3. Texto completo = título + reseña, sin vacíos ni duplicados
    df['texto'] = df['Title'].map(reparar_codificacion) + '. ' + df['Review'].map(reparar_codificacion)
    df = df.drop_duplicates(subset='texto')

    # 4. Muestra balanceada y reproducible
    df = df.groupby('sentimiento').sample(N_POR_CLASE, random_state=42)
    df = df[['texto', 'sentimiento']].sample(frac=1, random_state=42)

    df.to_csv('data/resenas.csv', index=False, encoding='utf-8')
    print("\n✅ ¡Completado! Archivo 'data/resenas.csv' creado con éxito.")
    print(f"📊 Distribución de clases (0=Negativo, 1=Positivo):\n{df['sentimiento'].value_counts()}")
except Exception as e:
    print(f"❌ Ocurrió un error al descargar los datos reales: {e}")
