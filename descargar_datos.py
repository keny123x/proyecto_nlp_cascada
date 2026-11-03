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
  def limpiar_texto_nlp_avanzado(texto):
    """
    Módulo de preprocesamiento de NLP e Ingeniería de Características.
    Normaliza el texto, elimina ruido numérico, caracteres especiales y espacios múltiples.
    """
    texto = reparar_codificacion(texto)
    if not isinstance(texto, str):
        return ""
    
    # 1. Pasar a minúsculas para unificar el vocabulario (evita duplicar "Hotel" y "hotel")
    texto = texto.lower()
    
    # 2. Eliminar números que no aportan valor semántico al análisis de sentimiento
    import re
    texto = re.sub(r'\d+', '', texto)
    
    # 3. Remover caracteres especiales y puntuación residual, conservando letras, eñes y tildes
    texto = re.sub(r'[^\w\sáéíóúñ]', '', texto)
    
    # 4. Limpiar espacios en blanco múltiples remanentes
    texto = re.sub(r'\s+', ' ', texto).strip()
    
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
    df['texto'] = df['Title'].map(limpiar_texto_nlp_avanzado) + '. ' + df['Review'].map(limpiar_texto_nlp_avanzado)

    df = df.drop_duplicates(subset='texto')

    # 4. Muestra balanceada y reproducible
    df = df.groupby('sentimiento').sample(N_POR_CLASE, random_state=42)
    df = df[['texto', 'sentimiento']].sample(frac=1, random_state=42)

    df.to_csv('data/resenas.csv', index=False, encoding='utf-8')
    print("\n✅ ¡Completado! Archivo 'data/resenas.csv' creado con éxito.")
    print(f"📊 Distribución de clases (0=Negativo, 1=Positivo):\n{df['sentimiento'].value_counts()}")
except Exception as e:
    print(f"❌ Ocurrió un error al descargar los datos reales: {e}")
