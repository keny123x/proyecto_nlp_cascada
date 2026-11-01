// Cambia esta URL al desplegar el backend. No se almacenan reseñas en el navegador.
export const API_URL = 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${API_URL}${path}`, {...options, signal: controller.signal});
    const data = await response.json();
    if (!response.ok) {
      const details = data.detalles?.map((detail) => detail.mensaje).join(' ');
      throw new Error(details || data.error || `El servidor respondió con código ${response.status}.`);
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('La API tardó demasiado. Inténtalo nuevamente.');
    if (error instanceof TypeError) throw new Error('No se pudo conectar con la API. Comprueba que FastAPI esté iniciado en el puerto 8000.');
    throw error;
  } finally { clearTimeout(timeout); }
}

export const getStatus = () => request('/status');
export const getMetrics = () => request('/metrics');
export const predictBatch = (textos) => request('/predict/lote', {
  method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({textos}),
});
export const predict = (texto) => request('/predict', {
  method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({texto}),
});
