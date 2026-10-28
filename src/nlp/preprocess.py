import re
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

nltk.download('stopwords', quiet=True)

class NLPPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('spanish'))
        palabras_negacion = {'no', 'ni', 'tampoco', 'nunca', 'jamas', 'nada', 'pero'}
        self.stop_words = self.stop_words - palabras_negacion
        self.stemmer = SnowballStemmer('spanish')
        self.lemas_comunes = {
            "buenisimo": "bueno", "buenisima": "bueno", "buenos": "bueno", "buenas": "bueno",
            "malisimo": "malo", "malisima": "malo", "malos": "malo", "malas": "malo",
            "excelentes": "excelente", "pesimos": "pesimo", "pesima": "pesimo"
        }

    def limpiar_texto_base(self, texto: str) -> list:
        if not isinstance(texto, str) or texto.strip() == "":
            return []
        texto = texto.lower()
        texto = re.sub(r'https?://\S+|www\.\S+', '', texto)
        texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        texto = re.sub(r'[^a-z\s]', '', texto)
        tokens = texto.split()
        tokens_limpios = [w for w in tokens if w not in self.stop_words]
        return tokens_limpios

    def aplicar_stemming(self, texto: str) -> str:
        tokens = self.limpiar_texto_base(texto)
        return " ".join([self.stemmer.stem(w) for w in tokens])

    def aplicar_lematizacion(self, texto: str) -> str:
        tokens = self.limpiar_texto_base(texto)
        return " ".join([self.lemas_comunes.get(w, w) for w in tokens])

if __name__ == "__main__":
    preprocesador = NLPPreprocessor()
    prueba = "¡¡PÉSIMO servicio, NO lo recomiendo para nada!!"
    print("--- VALIDACIÓN INTEGRANTE 1 ---")
    print("Original: ", prueba)
    print("Stemming: ", preprocesador.aplicar_stemming(prueba))
