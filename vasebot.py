from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
import os
from difflib import get_close_matches

app = Flask(__name__)
app.secret_key = "vasebot_secret_key"

USUARIO_PRUEBA = "piloto"
CLAVE_PRUEBA = "VASE1234"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "faq_tributarias.xlsx")
df = pd.read_excel(EXCEL_FILE)

# === Plantilla base con estilos ===
BASE_STYLE = """
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f8f9fa;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
    }
    .container {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        max-width: 600px;
        width: 100%;
        text-align: center;
    }
    h1, h2 {
        color: #2c3e50;
    }
    input[type=text], input[type=password] {
        width: 80%;
        padding: 10px;
        margin: 8px 0;
        border: 1px solid #ccc;
        border-radius: 6px;
    }
    button {
        background-color: #3498db;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
    }
    button:hover {
        background-color: #2980b9;
    }
    .logout {
        background-color: #e74c3c;
        margin-top: 15px;
    }
    .logout:hover {
        background-color: #c0392b;
    }
    .respuesta {
        background-color: #ecf0f1;
        padding: 15px;
        border-radius: 8px;
        text-align: left;
        margin-top: 15px;
    }
</style>
"""

# === Interfaz del chat ===
HTML_TEMPLATE = BASE_STYLE + """
<div class="container">
    <h1>VASEbot 🤝</h1>
    <p>Hola <strong>{{ usuario }}</strong>, tu asistente tributario en línea.</p>
    <form method="post">
        <input type="text" id="pregunta" name="pregunta" placeholder="Escribe tu consulta aquí..." required>
        <br><br>
        <button type="submit">Preguntar</button>
    </form>
    <form method="get" action="{{ url_for('logout') }}">
        <button type="submit" class="logout">Cerrar sesión</button>
    </form>

    {% if pregunta %}
        <div class="respuesta">
            <h3>Tu pregunta:</h3>
            <p><em>{{ pregunta }}</em></p>
            <h3>Respuesta:</h3>
            <p>{{ respuesta|safe }}</p>
            <p><small><em>{{ disclaimer }}</em></small></p>
        </div>
    {% endif %}
</div>
"""

# === Interfaz de login ===
LOGIN_TEMPLATE = BASE_STYLE + """
<div class="container">
    <h2>Login VASEbot</h2>
    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="post">
        <input type="text" name="username" placeholder="Usuario" required><br>
        <input type="password" name="password" placeholder="Contraseña" required><br>
        <button type="submit">Ingresar</button>
    </form>
</div>
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

# === Rutas ===
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

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)