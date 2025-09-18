from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

APP_TITLE = "VASEbot"
DISCLAIMER = "Verifique siempre la normativa vigente."
EXCEL_FILE = "faq_tributarias.xlsx"
THRESHOLD = 0.70   # umbral de similitud (ajusta si quieres más/menos estricto)
TOP_K = 3          # cuántas sugerencias mostrar si no hay confianza suficiente

# -------------------------
# Plantilla HTML simple
# -------------------------
HTML_PAGE = """
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>{{title}}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      body{font-family:Arial,Helvetica,sans-serif; margin:0; padding:0; background:#f4f6f8;}
      .header{background:#0b5ed7;color:white;padding:16px 20px;}
      .container{max-width:800px;margin:20px auto;padding:0 10px;}
      .chat{background:white;border-radius:8px;padding:12px;min-height:300px;box-shadow:0 2px 6px rgba(0,0,0,0.08);}
      .messages{height:360px; overflow:auto; padding:8px; border:1px solid #eee; border-radius:6px; background:#fff;}
      .msg.user{ text-align:right; margin:8px 0;}
      .msg.bot{ text-align:left; margin:8px 0;}
      .bubble{display:inline-block;padding:10px 14px;border-radius:14px; max-width:80%;}
      .bubble.user{background:#0b5ed7;color:white;}
      .bubble.bot{background:#e9ecef;color:#111;}
      .input-row{display:flex; margin-top:12px;}
      input[type="text"]{flex:1;padding:10px;border-radius:6px;border:1px solid #ccc;font-size:14px;}
      button{margin-left:8px;padding:10px 14px;border-radius:6px;border:none;background:#0b5ed7;color:white;cursor:pointer;}
      .meta{font-size:12px;color:#666;margin-top:6px;}
      a.small{font-size:12px;color:#0b5ed7;}
    </style>
  </head>
  <body>
    <div class="header">
      <strong>{{title}}</strong> — Tu asistente tributario
    </div>
    <div class="container">
      <div class="chat">
        <div class="messages" id="messages"></div>

        <div class="input-row">
          <input id="q" type="text" placeholder="Escribe tu pregunta tributaria..." />
          <button id="send">Enviar</button>
        </div>
        <div class="meta">Nota: {{disclaimer}}</div>
      </div>
    </div>

    <script>
      const messagesEl = document.getElementById('messages');
      const qEl = document.getElementById('q');
      const btn = document.getElementById('send');

      function addMessage(text, who='bot') {
        const div = document.createElement('div');
        div.className = 'msg ' + (who==='user' ? 'user' : 'bot');
        const span = document.createElement('div');
        span.className = 'bubble ' + (who==='user' ? 'user' : 'bot');
        span.innerText = text;
        div.appendChild(span);
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }

      btn.onclick = async () => {
        const q = qEl.value.trim();
        if(!q) return;
        addMessage(q, 'user');
        qEl.value = '';
        addMessage('Consultando...', 'bot');
        // send to server
        try {
          const res = await fetch('/ask', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({question: q})
          });
          const data = await res.json();
          // remove last "Consultando..." bubble
          messagesEl.removeChild(messagesEl.lastChild);

          if(data.answer) {
            addMessage(data.answer + "\\n\\nFuente: " + data.source + "\\n" + data.disclaimer, 'bot');
          } else {
            addMessage("No encontré una coincidencia clara. ¿Quizás quisiste decir alguna de estas preguntas?\\n" + data.suggestions.join('\\n'), 'bot');
          }
        } catch(err) {
          // remove last "Consultando..."
          messagesEl.removeChild(messagesEl.lastChild);
          addMessage("Error en la conexión al servidor.", 'bot');
          console.error(err);
        }
      };

      // enviar con Enter
      qEl.addEventListener('keydown', function(e){
        if(e.key === 'Enter') btn.click();
      });
    </script>
  </body>
</html>
"""

# -------------------------
# App Flask
# -------------------------
app = Flask(__name__)

# Cargar y preparar datos + modelo al iniciar la app (solo una vez)
print("Cargando datos y modelo... (puede tardar unos segundos la primera vez)")
if not os.path.exists(EXCEL_FILE):
    raise FileNotFoundError(f"No encontré '{EXCEL_FILE}' en {os.getcwd()}. Coloca el Excel en la misma carpeta que este script.")

df = pd.read_excel(EXCEL_FILE)
if not {"Pregunta", "Respuesta", "Fuente"}.issubset(df.columns):
    raise ValueError("El Excel debe tener las columnas: Pregunta, Respuesta, Fuente")

questions = df["Pregunta"].astype(str).tolist()
answers = df["Respuesta"].astype(str).tolist()
sources = df["Fuente"].astype(str).tolist()

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(questions, convert_to_numpy=True)
# normalizar embeddings para acelerar cálculo de coseno
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
embeddings_normed = embeddings / np.where(norms==0, 1e-9, norms)

print(f"Preguntas cargadas: {len(questions)}")
print("Modelo listo. Inicia el servidor y abre http://127.0.0.1:5000/ en tu navegador.")

def cosine_sim(a, b):
    # a: vector 1-D, b: matrix (N x D) or vector
    a_norm = a / (np.linalg.norm(a) + 1e-9)
    if b.ndim == 1:
        b_norm = b / (np.linalg.norm(b) + 1e-9)
        return float(np.dot(a_norm, b_norm))
    else:
        b_norm = b  # already normalized
        return np.dot(b_norm, a_norm)

@app.route("/")
def index():
    return render_template_string(HTML_PAGE, title=APP_TITLE, disclaimer=DISCLAIMER)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    q = (data.get("question") or "").strip()
    if not q:
        return jsonify({"answer": None, "suggestions": []})

    q_emb = model.encode([q], convert_to_numpy=True)[0]
    # normalizar query
    q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-9)

    # similitudes (coseno)
    sims = np.dot(embeddings_normed, q_emb)  # vector de shape (N,)
    top_idx = np.argsort(-sims)[:TOP_K]
    best_idx = top_idx[0]
    best_score = float(sims[best_idx])

    if best_score < THRESHOLD:
        # sugerencias en texto (las preguntas más parecidas)
        suggestions = [questions[i] for i in top_idx.tolist() if i < len(questions)]
        return jsonify({"answer": None, "suggestions": suggestions})
    else:
        answer = answers[best_idx]
        source = sources[best_idx]
        return jsonify({
            "answer": answer,
            "source": source,
            "disclaimer": DISCLAIMER,
            "score": best_score
        })

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render asigna un puerto
    app.run(host="0.0.0.0", port=port)