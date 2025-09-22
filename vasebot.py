from flask import Flask, request, render_template_string, session, redirect, url_for
import pandas as pd
import os
from difflib import get_close_matches

# === Configuración de Flask ===
app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # Necesario para manejar sesiones

# === Cargar Excel con ruta absoluta ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "faq_tributarias.xlsx")
df = pd.read_excel(EXCEL_FILE)

# === Usuario y clave de prueba ===
USUARIO = "demo"
CLAVE = "1234"

# === Plantilla HTML ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>VASEbot – Asistente Tributario</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px; text-align: center;">
    <h1>VASEbot 🤝</h1>
    <p>Tu asistente tributario en línea</p>

    {% if not pregunta %}
        <div style="margin: 20px auto; max-width: 600px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; text-align: left;">
            <h3>Bienvenido</h3>
            <p>Consulta aquí tus dudas tributarias.</p>
        </div>
    {% endif %}

    <form method="post" style="margin-top: 20px;">
        <label for="pregunta"><strong>Haz tu consulta:</strong></label><br><br>
        <input type="text" id="pregunta" name="pregunta" style="width: 400px; padding: 8px;" required>
        <button type="submit" style="padding: 8px 16px; margin-left: 5px; background-color: #0A6A66; color: white; border: none; border-radius: 4px; cursor: pointer;">
            Preguntar
        </button>
    </form>

    {% if pregunta %}
        <div style="margin: 30px auto; max-width: 600px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: #f1f1f1; text-align: left;">
            <h3>Tu pregunta:</h3>
            <p>{{ pregunta }}</p>
            <h3>Respuesta:</h3>
            <p>{{ respuesta|safe }}</p>
            {% if no_encontrada %}
                <div style="margin-top:20px; padding:15px; border:1px dashed #ccc; border-radius:6px; background-color:#fff;">
                    <p>Aún no tengo la respuesta a tu consulta. Te invito a plantearla en nuestro grupo de WhatsApp en el siguiente enlace:</p>
                    <a href="https://chat.whatsapp.com/BRoZPkxHmsGG9JrZSF9tNb" target="_blank" 
                       style="display:inline-flex; align-items:center; padding:10px 15px; background-color:#25D366; color:white; font-weight:bold; border-radius:6px; text-decoration:none;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
                             alt="WhatsApp" style="width:20px; height:20px; margin-right:8px;">
                        Unirme al grupo
                    </a>
                </div>
            {% endif %}
            <p><em>{{ disclaimer }}</em></p>
        </div>
    {% endif %}

    <br>
    <a href="{{ url_for('logout') }}" style="display: inline-block; padding: 8px 16px; background-color: #d9534f; color: white; text-decoration: none; border-radius: 4px;">
        Cerrar sesión
    </a>
</body>
</html>
"""

# === Pantalla de Login ===
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - VASEbot</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px; text-align: center;">
    <div style="margin: 50px auto; max-width: 400px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
        <h2>Acceso a VASEbot</h2>
        <form method="post">
            <input type="text" name="usuario" placeholder="Usuario" required style="width: 90%; padding: 8px; margin-bottom: 10px;"><br>
            <input type="password" name="clave" placeholder="Clave" required style="width: 90%; padding: 8px; margin-bottom: 10px;"><br>
            <button type="submit" style="padding: 8px 16px; background-color: #0275d8; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Ingresar
            </button>
        </form>
        {% if error %}
            <p style="color: red; margin-top: 10px;">{{ error }}</p>
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
        return fila["Respuesta"], fila.get("Fuente", ""), fila.get("Disclaimer", ""), False
    else:
        return "Lo siento, no encontré una coincidencia clara.", "", "", True

# === Ruta de Login ===
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        if usuario == USUARIO and clave == CLAVE:
            session["usuario"] = usuario
            return redirect(url_for("home"))
        else:
            error = "Usuario o clave incorrectos"
    return render_template_string(LOGIN_TEMPLATE, error=error)

# === Ruta principal ===
@app.route("/", methods=["GET", "POST"])
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))

    respuesta, fuente, disclaimer, no_encontrada = "", "", "", False
    pregunta = ""

    if request.method == "POST":
        pregunta = request.form["pregunta"]
        respuesta, fuente, disclaimer, no_encontrada = buscar_respuesta(pregunta)

        if fuente:
            respuesta += f"<br><br><strong>Fuente:</strong> {fuente}"

    return render_template_string(HTML_TEMPLATE, pregunta=pregunta, respuesta=respuesta, disclaimer=disclaimer, no_encontrada=no_encontrada)

# === Cerrar sesión ===
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# === Ejecutar en Render ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)