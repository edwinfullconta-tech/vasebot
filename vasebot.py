from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
import os
from difflib import get_close_matches

# === Configuración de Flask ===
app = Flask(__name__)
app.secret_key = "clave_secreta_prueba"  # Necesario para manejar sesiones

# === Usuario y clave de prueba ===
USUARIO = "admin"
CLAVE = "1234"

# === Cargar Excel con ruta absoluta ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "faq_tributarias.xlsx")
df = pd.read_excel(EXCEL_FILE)

# === Plantilla Login ===
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - VASEbot</title>
</head>
<body style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: Arial, sans-serif;">
    <div style="text-align: center; border: 1px solid #ccc; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h2>Acceso a VASEbot</h2>
        <form method="post">
            <input type="text" name="usuario" placeholder="Usuario" required style="padding: 10px; margin: 10px; width: 80%;"><br>
            <input type="password" name="clave" placeholder="Contraseña" required style="padding: 10px; margin: 10px; width: 80%;"><br>
            <button type="submit" style="background-color: #0A6A66; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Ingresar</button>
        </form>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

# === Plantilla Principal ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>VASEbot - Asistente Tributario</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px; display: flex; justify-content: center;">
    <div style="max-width: 600px; width: 100%;">
        <h1 style="text-align: center;">VASEbot</h1>
        <p style="text-align: center;">Asistente Tributario en línea</p>
        <p style="text-align: center; font-style: italic; color: #555;">Bienvenido a VASEbot, tu espacio confiable para resolver dudas tributarias.</p>

        <form method="post" style="text-align: center; margin-top: 20px;">
            <input type="text" id="pregunta" name="pregunta" placeholder="Escribe tu consulta aquí..." 
                   style="width: 80%; padding: 10px;" required>
            <button type="submit" 
                    style="background-color: #0A6A66; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                Enviar
            </button>
        </form>

        {% if pregunta %}
            <div style="margin-top: 30px; text-align: left;">
                <h3>Tu pregunta:</h3>
                <p>{{ pregunta }}</p>
                <h3>Respuesta:</h3>
                <p>{{ respuesta|safe }}</p>
                {% if disclaimer %}
                    <p><em>{{ disclaimer }}</em></p>
                {% endif %}
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
        return fila["Respuesta"], fila.get("Fuente", ""), fila.get("Disclaimer", "")
    else:
        return "Lo siento, no encontré una coincidencia clara.", "", ""

# === Ruta de Login ===
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        if usuario == USUARIO and clave == CLAVE:
            session["usuario"] = usuario
            return redirect(url_for("home"))
        else:
            error = "Usuario o contraseña incorrectos."
    return render_template_string(LOGIN_TEMPLATE, error=error)

# === Ruta principal ===
@app.route("/", methods=["GET", "POST"])
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))

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