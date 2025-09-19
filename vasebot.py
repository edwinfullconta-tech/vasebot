from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
import os
from difflib import get_close_matches

# === Configuración de Flask ===
app = Flask(__name__)
app.secret_key = "vasebot_secret_key"  # Cambia por algo más seguro en producción

# === Usuario único de prueba ===
USUARIO_PRUEBA = "piloto"
CLAVE_PRUEBA = "VASE1234"

# === Cargar Excel con ruta absoluta ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "faq_tributarias.xlsx")
df = pd.read_excel(EXCEL_FILE)

# === Interfaz del chat con bienvenida y logout ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>VASEbot – Asistente Tributario</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
    <h1>VASEbot 🤝</h1>
    <p>Hola <strong>{{ usuario }}</strong>, tu asistente tributario en línea.</p>
    <form method="post">
        <label for="pregunta">Haz tu consulta:</label><br><br>
        <input type="text" id="pregunta" name="pregunta" style="width: 400px;" required>
        <button type="submit">Preguntar</button>
    </form>
    <form method="get" action="{{ url_for('logout') }}" style="margin-top:20px;">
        <button type="submit" style="background-color:#e74c3c; color:white; padding:8px 16px; border:none; border-radius:4px;">Cerrar sesión</button>
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

# === Interfaz de login ===
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login VASEbot</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px;">
    <h2>Login VASEbot</h2>
    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="post">
        <label>Usuario:</label><br>
        <input type="text" name="username" required><br><br>
        <label>Contraseña:</label><br>
        <input type="password" name="password" required><br><br>
        <button type="submit">Ingresar</button>
    </form>
</body>
</html>
"""

# === Función para buscar respuesta ===
def buscar_respuesta(pregunta):
    preguntas = df["Pregunta"].tolist()
    coincidencias = get_close_matches(pregunta, preguntas, n=1, cutoff=0.5)
    if coincidencias:
        fila = df[df["Pregunta"] == coincidencias[0]].iloc[0]
        return f"{fila['Respuesta']}<br><br><strong>Fuente:</strong> {fila['Fuente']}", fila.get("Disclaimer", "Verifique siempre la normativa vigente.")
    else:
        return "Lo siento, no encontré una coincidencia clara.", "Verifique siempre la normativa vigente."

# === Ruta de login ===
@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("home"))

    error = ""
    if request.method == "POST":
        usuario = request.form["username"]
        clave = request.form["password"]
        if usuario == USUARIO_PRUEBA and clave == CLAVE_PRUEBA:
            session["username"] = usuario
            return redirect(url_for("home"))
        else:
            error = "Usuario o contraseña incorrectos."
    return render_template_string(LOGIN_TEMPLATE, error=error)

# === Ruta principal del chat ===
@app.route("/home", methods=["GET", "POST"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    usuario = session["username"]
    respuesta, disclaimer = "", ""
    pregunta = ""

    if request.method == "POST":
        pregunta = request.form["pregunta"]
        respuesta, disclaimer = buscar_respuesta(pregunta)

    return render_template_string(HTML_TEMPLATE, pregunta=pregunta, respuesta=respuesta, disclaimer=disclaimer, usuario=usuario)

# === Ruta de logout ===
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# === Ejecutar en Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)