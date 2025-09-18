from flask import Flask, render_template_string, request
import pandas as pd

# Cargar Excel con las preguntas y respuestas
faq_df = pd.read_excel("faq_tributarias.xlsx")

# Plantilla HTML básica
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VASEbot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        h1 { color: #2C3E50; }
        .chat-box { width: 100%; max-width: 600px; }
        .question, .answer { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .question { background-color: #D6EAF8; text-align: right; }
        .answer { background-color: #E8F8F5; text-align: left; }
        .disclaimer { font-size: 12px; color: #7D3C98; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🤖 VASEbot - Tu asistente tributario</h1>
    <form method="post">
        <input type="text" name="pregunta" placeholder="Haz tu consulta aquí..." style="width:400px; padding:5px;" required>
        <button type="submit">Consultar</button>
    </form>

    {% if pregunta %}
        <div class="chat-box">
            <div class="question"><b>Tú:</b> {{ pregunta }}</div>
            <div class="answer"><b>VASEbot:</b> {{ respuesta }}</div>
        </div>
    {% endif %}

    <div class="disclaimer">⚠ Verifique siempre la normativa vigente.</div>
</body>
</html>
"""

# Crear la app Flask
app = Flask(__name__)

def buscar_respuesta(pregunta):
    for _, row in faq_df.iterrows():
        if str(row["Pregunta"]).lower() in pregunta.lower():
            return row["Respuesta"]
    return "Lo siento, no encontré una coincidencia clara."

@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""
    pregunta = ""
    if request.method == "POST":
        pregunta = request.form["pregunta"]
        respuesta = buscar_respuesta(pregunta)
    return render_template_string(HTML_TEMPLATE, pregunta=pregunta, respuesta=respuesta)

# ⚠️ Importante: Render necesita que la app quede expuesta así
app = app