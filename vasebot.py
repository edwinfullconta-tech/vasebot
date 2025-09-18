from flask import Flask, request, render_template_string
import pandas as pd
import os
from difflib import get_close_matches

# === Configuración de Flask ===
app = Flask(__name__)

# === Cargar Excel con ruta absoluta ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "faq_tributarias.xlsx")
df = pd.read_excel(EXCEL_FILE)

# === Interfaz simple ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>VASEbot - Asistente Tributario</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
    <h1>VASEbot 🤖</h1>
    <p>Tu asistente tributario en línea</p>
    <form method="post">
        <label for="pregunta">Haz tu consulta:</label><br><br>
        <input type="text" id="pregunta" name="pregunta" style="width: 400px;" required>
        <button type="submit">Preguntar</button>
    </form>

    {% if pregunta %}
        <h3>Tu pregunta:</h3>
        <p>{{ pregunta }}</p>
        <h3>Respuesta:</h3>
        <p>{{ respuesta|safe }}</p>
        <p><em>{{ disclaimer }}</em></p>
    {% endif %}
</body>
</html>
"""

# === Buscar mejor coincidencia ===
def buscar_respuesta(pregunta):
    preguntas = df["Pregunta"].tolist()
    coincidencias = get_close_matches(pregunta, preguntas, n=1, cutoff=0.5)
    if coincidencias:
        fila = df[df["Pregunta"] == coincidencias[0]].iloc[0]
        return fila["Respuesta"], fila["Fuente"], fila["Disclaimer"]
    else:
        return "Lo siento, no encontré una coincidencia clara.", "", ""

# === Ruta principal ===
@app.route("/", methods=["GET", "POST"])
def home():
    respuesta, fuente, disclaimer = "", "", ""
    pregunta = ""

    if request.method == "POST":
        pregunta = request.form["pregunta"]
        respuesta, fuente, disclaimer = buscar_respuesta(pregunta)

        if fuente:
            respuesta += f"<br><br><strong>Fuente:</strong> {fuente}"

    return render_template_string(HTML_TEMPLATE, pregunta=pregunta, respuesta=respuesta, disclaimer=disclaimer)

# === Ejecutar en Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)