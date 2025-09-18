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

# === Interfaz mejorada ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>VASEbot - Asistente Tributario</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px; background-color:#f0f2f5;">
    <div style="max-width:700px; margin:auto; padding:20px; background-color:white; border-radius:10px; box-shadow:0px 0px 10px rgba(0,0,0,0.1);">
        <h1 style="text-align:center; color:#2c3e50;">VASEbot 🤖</h1>
        <p style="text-align:center; color:#34495e;">Tu asistente tributario en línea</p>

        <form method="post" style="text-align:center; margin-top:20px;">
            <input type="text" id="pregunta" name="pregunta" style="width: 400px; padding:8px; border-radius:5px; border:1px solid #ccc;" required>
            <button type="submit" style="padding:8px 15px; margin-left:10px; border-radius:5px; border:none; background-color:#3498db; color:white; cursor:pointer;">Preguntar</button>
        </form>

        {% if pregunta %}
            <div style="margin-top:30px;">
                <h3>Tu pregunta:</h3>
                <p>{{ pregunta }}</p>
                
                <h3>Respuesta:</h3>
                <div style="border:1px solid #ccc; padding:15px; background-color:#f9f9f9; border-radius:8px;">
                    {{ respuesta|safe }}
                    {% if disclaimer %}
                        <p style="margin-top:10px;"><em>{{ disclaimer }}</em></p>
                    {% endif %}
                </div>
            </div>
        {% endif %}
    </div>
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