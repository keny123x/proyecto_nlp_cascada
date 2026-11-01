import os

# Raíz del repositorio (una carpeta arriba de api/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Archivos que exporta el Integrante 2 (Nicolás)
RUTA_MODELO = os.getenv('RUTA_MODELO', os.path.join(BASE_DIR, 'src', 'models', 'pipeline_modelo.pkl'))
RUTA_METRICAS = os.getenv('RUTA_METRICAS', os.path.join(BASE_DIR, 'src', 'models', 'metricas.json'))

# Orígenes que pueden llamar a la API desde el navegador, separados por coma
ORIGENES_PERMITIDOS = [o.strip() for o in os.getenv('ORIGENES_PERMITIDOS', '*').split(',') if o.strip()]

# Límites de las reseñas
MAX_CARACTERES = int(os.getenv('MAX_CARACTERES', '2000'))

# Archivo donde guardar el registro de peticiones (vacío = solo consola)
LOG_ARCHIVO = os.getenv('LOG_ARCHIVO', '')
