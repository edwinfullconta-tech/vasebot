from flask import Flask, request, render_template_string, session, redirect, url_for
import pandas as pd
import os

=== Configuración de Flask ===

app = Flask(name)
app.secret_key = "clave_secreta_super_segura" # Necesario para manejar sesiones

=== Cargar Excel con ruta absoluta ===

BASE_DIR = os.path.dirname(os.path.abspath(file))
EXCEL_FILE = os.path.join(BASE_DIR, "faq_tributarias.xlsx")
df = pd.read_excel(EXCEL_FILE)

=== Usuario y clave de prueba ===

USUARIO = "demo"
CLAVE = "1234"

=== Plantilla HTML principal ===

HTML_TEMPLATE = """

{% if not tema and not pregunta and not resultados %}
    <div class="card">
        <h3>Bienvenido</h3>
        <p>Consulta aquí tus dudas tributarias seleccionando un tema o buscando por palabra clave.</p>
    </div>
{% endif %}

<!-- Formulario búsqueda -->
<form method="post">
    <label><strong>Selecciona un tema:</strong></label>
    <select name="tema">
        <option value="">-- Elige un tema --</option>
        {% for t in temas %}
            <option value="{{t}}" {% if tema == t %}selected{% endif %}>{{t}}</option>
        {% endfor %}
    </select>
    <br><br>
    <label><strong>O busca por palabra clave:</strong></label>
    <input type="text" name="keyword" placeholder="Escribe palabra clave o frase...">
    <button type="submit">Buscar</button>
</form>

{% if resultados %}
    <div class="card">
        <h3>Resultados de búsqueda</h3>
        <ul>
            {% for r in resultados[:5] %}
                <li>
                    <a class="link-pregunta" href="{{ url_for('home', tema=r['Tema'], pregunta=r['Index']) }}">
                        {{ r['Pregunta']|safe }}
                    </a>
                    <p>{{ r['Preview']|safe }}</p>
                </li>
            {% endfor %}
        </ul>
        {% if resultados|length > 5 %}
            <form method="post">
                <input type="hidden" name="keyword" value="{{ keyword }}">
                <button type="submit">Ver más resultados</button>
            </form>
        {% endif %}
    </div>
{% elif keyword %}
    <div class="card">
        <h3>Sin resultados</h3>
        <p>No encontramos coincidencias para "<strong>{{ keyword }}</strong>".</p>
        <p>Puedes escribirnos directamente al WhatsApp:</p>
        <a href="https://chat.whatsapp.com/BRoZPkxHmsGG9JrZSF9tNb?mode=ems_share_t" target="_blank">
            Escríbenos al WhatsApp
        </a>
    </div>
{% endif %}

{% if tema and not pregunta %}
    <div class="card">
        <h3>Preguntas sobre: {{ tema }}</h3>
        <ul>
            {% for p in preguntas_tema %}
                <li>
                    <a class="link-pregunta" href="{{ url_for('home', tema=tema, pregunta=loop.index0) }}">
                        {{ p }}
                    </a>
                </li>
            {% endfor %}
        </ul>
    </div>
{% endif %}

{% if pregunta %}
    <div class="card card-pregunta">
        <h3>Pregunta</h3>
        <p>{{ pregunta }}</p>
    </div>
    <div class="card card-respuesta">
        <h3>Respuesta</h3>
        <p>{{ respuesta|safe }}</p>
        {% if fuente %}<p><strong>Fuente:</strong> {{ fuente }}</p>{% endif %}
        <p><em>{{ disclaimer }}</em></p>
    </div>
{% endif %}

<a href="{{ url_for('logout') }}" class="logout">Cerrar sesión</a>

<!-- Botón flotante de WhatsApp -->
<a href="https://chat.whatsapp.com/BRoZPkxHmsGG9JrZSF9tNb?mode=ems_share_t" 
   class="whatsapp-float" target="_blank" title="Escríbenos al WhatsApp">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp">
</a>

=== Pantalla de Login ===

LOGIN_TEMPLATE = """

=== Rutas ===

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

@app.route("/", methods=["GET", "POST"])
def home():
if "usuario" not in session:
return redirect(url_for("login"))

tema = request.args.get("tema")
pregunta_idx = request.args.get("pregunta")
pregunta = respuesta = fuente = disclaimer = None
preguntas_tema = []
resultados = []
keyword = request.form.get("keyword", "") if request.method == "POST" else None

temas = sorted(df["Tema"].dropna().unique().tolist())

# === Buscar por palabra clave ===
if keyword:
    kw = keyword.lower()
    for idx, row in df.iterrows():
        if kw in str(row["Pregunta"]).lower() or kw in str(row["Respuesta"]).lower():
            resultados.append({
                "Tema": row["Tema"],
                "Index": df[df["Tema"] == row["Tema"]].reset_index().index[
                    df[df["Tema"] == row["Tema"]]["Pregunta"] == row["Pregunta"]
                ][0],
                "Pregunta": row["Pregunta"].replace(keyword, f"<span class='highlight'>{keyword}</span>"),
                "Preview": (row["Respuesta"][:120] + "...").replace(keyword, f"<span class='highlight'>{keyword}</span>")
            })

# === Filtrar por tema ===
if request.method == "POST" and not keyword:
    tema = request.form["tema"]
    return redirect(url_for("home", tema=tema))

if tema and pregunta_idx is None:
    preguntas_tema = df[df["Tema"] == tema]["Pregunta"].tolist()

if tema and pregunta_idx is not None:
    preguntas_tema = df[df["Tema"] == tema].reset_index(drop=True)
    fila = preguntas_tema.iloc[int(pregunta_idx)]
    pregunta = fila["Pregunta"]
    respuesta = fila["Respuesta"]
    fuente = fila.get("Fuente", "")
    disclaimer = fila.get("Disclaimer", "")

return render_template_string(
    HTML_TEMPLATE,
    temas=temas,
    tema=tema,
    preguntas_tema=preguntas_tema,
    pregunta=pregunta,
    respuesta=respuesta,
    fuente=fuente,
    disclaimer=disclaimer,
    resultados=resultados,
    keyword=keyword,
)


@app.route("/logout")
def logout():
session.pop("usuario", None)
return redirect(url_for("login"))

if name == "main":
app.run(host="0.0.0.0", port=5000)