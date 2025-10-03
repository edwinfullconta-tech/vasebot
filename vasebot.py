from flask import Flask, request, render_template_string, session, redirect, url_for
import pandas as pd
import os

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

# === Plantilla HTML principal ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VASEbot – Asistente Tributario</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            text-align: center;
            background-color: #f7f7f7;
        }
        h1 { color: #0A6A66; }
        form, .card {
            margin: 20px auto;
            max-width: 700px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: white;
            text-align: left;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }
        .card-pregunta, .card-respuesta {
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-top: 15px;
            padding: 0;
        }
        .card-pregunta h3 {
            background-color: #004085;
            border-bottom: 1px solid #ccc;
            padding: 10px;
            margin: 0;
            color: #ffffff;
        }
        .card-respuesta h3 {
            background-color: #6c757d;
            border-bottom: 1px solid #ccc;
            padding: 10px;
            margin: 0;
            color: #ffffff;
        }
        .card-pregunta p, .card-respuesta p {
            padding: 10px;
            margin: 0;
            font-style: normal;
        }
        select, input, button {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #0A6A66;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover { background-color: #09524f; }
        ul { padding-left: 20px; }
        li { margin: 8px 0; }
        a.link-pregunta {
            text-decoration: none;
            color: #0A6A66;
            font-weight: bold;
        }
        .logout {
            display: inline-block;
            padding: 8px 16px;
            background-color: #d9534f;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 20px;
        }
        .highlight { background-color: yellow; font-weight: bold; }
        /* Botón flotante WhatsApp */
        .whatsapp-float {
            position: fixed;
            width: 55px;
            height: 55px;
            bottom: 20px;
            right: 20px;
            background-color: #25D366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            z-index: 1000;
            transition: transform 0.2s;
        }
        .whatsapp-float:hover { transform: scale(1.1); }
        .whatsapp-float img { width: 32px; height: 32px; }
        /* Adaptación móviles */
        @media (max-width: 600px) {
            body { margin: 10px; }
            form, .card { padding: 12px; }
            select, input, button { font-size: 16px; }
            h1 { font-size: 22px; }
            .whatsapp-float { width: 50px; height: 50px; bottom: 15px; right: 15px; }
            .whatsapp-float img { width: 28px; height: 28px; }
        }
    </style>
</head>
<body>
    <h1>VASEbot 🤝</h1>
    <p>Tu asistente tributario en línea</p>

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
            <p>Puedes escribirnos directamente al WhatsApp</p>
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
</body>
</html>
"""

# === Pantalla de Login ===
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - VASEbot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; background-color: #f7f7f7; }
        .login-box {
            margin: 50px auto;
            max-width: 400px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }
        input, button { width: 90%; padding: 10px; margin-top: 10px; border-radius: 5px; border: 1px solid #ccc; }
        button { background-color: #0275d8; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #025aa5; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Acceso a VASEbot</h2>
        <form method="post">
            <input type="text" name="usuario" placeholder="Usuario" required><br>
            <input type="password" name="clave" placeholder="Clave" required><br>
            <button type="submit">Ingresar</button>
        </form>
        {% if error %}<p style="color: red; margin-top: 10px;">{{ error }}</p>{% endif %}
    </div>
</body>
</html>
"""

# === Rutas ===
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)