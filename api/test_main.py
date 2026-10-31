import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import api.main as main
from api.config import MAX_CARACTERES

cliente = TestClient(main.app)


@pytest.fixture
def modo_simulado(monkeypatch):
    """Fuerza la respuesta fija, como si todavía no existiera pipeline_modelo.pkl."""
    monkeypatch.setattr(main, "modelo", None)


requiere_modelo = pytest.mark.skipif(main.modelo is None, reason="pipeline_modelo.pkl no está disponible")


# ---------- GET /status ----------

def test_status_responde_ok():
    r = cliente.get("/status")
    assert r.status_code == 200
    datos = r.json()
    assert datos["estado"] == "ok"
    assert datos["modo"] in ("real", "simulado")
    assert datos["modelo_cargado"] == (datos["modo"] == "real")


def test_status_en_modo_simulado(modo_simulado):
    assert cliente.get("/status").json()["modelo_cargado"] is False


# ---------- GET /metrics ----------

def test_metrics_devuelve_precision():
    r = cliente.get("/metrics")
    assert r.status_code == 200
    datos = r.json()
    assert 0 <= datos["accuracy"] <= 1
    assert "modelo" in datos


# ---------- POST /predict ----------

def test_predict_estructura_de_respuesta():
    r = cliente.post("/predict", json={"texto": "La comida estuvo deliciosa"})
    assert r.status_code == 200
    datos = r.json()
    assert datos["sentimiento"] in ("Positivo", "Negativo")
    assert 0.5 <= datos["probabilidad"] <= 1
    assert datos["porcentaje"].endswith("%")
    assert set(datos["probabilidades"]) == {"Positivo", "Negativo"}


def test_predict_simulado_responde_positivo_90(modo_simulado):
    datos = cliente.post("/predict", json={"texto": "Cualquier reseña"}).json()
    assert datos["sentimiento"] == "Positivo"
    assert datos["probabilidad"] == 0.9
    assert datos["modo"] == "simulado"


def test_predict_paso_a_paso_nlp():
    texto = "¡El Hotel NO es bueno! Visiten https://ejemplo.com 100%"
    pasos = cliente.post("/predict", json={"texto": texto}).json()["pasos"]
    # Paso 1: minúsculas, sin URL, sin signos ni números
    assert pasos["paso1_normalizado"] == "el hotel no es bueno visiten"
    # Paso 2: tokens
    assert pasos["paso2_tokens"] == ["el", "hotel", "no", "es", "bueno", "visiten"]
    # Paso 3: se borran conectores pero se conserva la negación
    assert "el" in pasos["paso3_stopwords_eliminadas"]
    assert "no" in pasos["paso3_sin_stopwords"]
    assert pasos["paso3_negaciones_conservadas"] == ["no"]
    # Paso 4: raíces
    assert len(pasos["paso4_stemming"]) == len(pasos["paso3_sin_stopwords"])
    # Paso 5: veredicto
    assert "% de probabilidad" in pasos["paso5_resultado"]


def test_predict_quita_tildes():
    pasos = cliente.post("/predict", json={"texto": "Pésimo servicio"}).json()["pasos"]
    assert pasos["paso1_normalizado"] == "pesimo servicio"


@requiere_modelo
def test_predict_modelo_real_negativo():
    datos = cliente.post("/predict", json={"texto": "El hotel estaba sucio y NO lo recomiendo para nada"}).json()
    assert datos["sentimiento"] == "Negativo"


@requiere_modelo
def test_predict_modelo_real_positivo():
    datos = cliente.post("/predict", json={"texto": "Excelente servicio, la comida estuvo deliciosa"}).json()
    assert datos["sentimiento"] == "Positivo"


# ---------- Validaciones ----------

@pytest.mark.parametrize("cuerpo, mensaje", [
    ({"texto": ""}, "La reseña no puede estar vacía."),
    ({"texto": "     "}, "La reseña no puede estar vacía."),
    ({"texto": "!!! 123 ???"}, "La reseña debe contener al menos una palabra."),
    ({}, "Este campo es obligatorio."),
    ({"texto": 123}, "El valor debe ser un texto."),
    ({"texto": "a" * (MAX_CARACTERES + 1)}, f"La reseña no puede superar los {MAX_CARACTERES} caracteres."),
])
def test_predict_rechaza_textos_invalidos(cuerpo, mensaje):
    r = cliente.post("/predict", json=cuerpo)
    assert r.status_code == 422
    datos = r.json()
    assert datos["error"] == "Datos inválidos"
    assert datos["detalles"][0]["mensaje"] == mensaje


def test_predict_rechaza_json_invalido():
    r = cliente.post("/predict", content="esto no es json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert r.json()["detalles"][0]["campo"] == "body"


# ---------- POST /predict/lote ----------

def test_lote_cuenta_positivos_y_negativos():
    textos = ["La comida estuvo deliciosa", "El servicio fue pésimo", "Habitación sucia"]
    datos = cliente.post("/predict/lote", json={"textos": textos}).json()
    assert datos["total"] == 3
    assert datos["positivos"] + datos["negativos"] == 3
    assert len(datos["resultados"]) == 3


@pytest.mark.parametrize("textos", [[], ["bien", "   "], ["ok"] * 51])
def test_lote_rechaza_listas_invalidas(textos):
    assert cliente.post("/predict/lote", json={"textos": textos}).status_code == 422


# ---------- GET /ejemplos ----------

def test_ejemplos_lista_completa():
    datos = cliente.get("/ejemplos").json()
    assert len(datos) >= 6
    assert {e["categoria"] for e in datos} == {"hotel", "restaurante", "producto"}


def test_ejemplos_filtra_por_categoria():
    datos = cliente.get("/ejemplos", params={"categoria": "hotel"}).json()
    assert datos and all(e["categoria"] == "hotel" for e in datos)
