import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# ==========================
# CONFIGURACIÓN DEL BOT
# ==========================
DISCLAIMER = "Verifique siempre la normativa vigente."
EXCEL_FILE = "faq_tributarias.xlsx"

# ==========================
# CARGA DE PREGUNTAS Y MODELO
# ==========================
print("=============================")
print("   Bienvenido a VASEbot")
print("   Tu asistente tributario")
print("=============================")

# Leer Excel
df = pd.read_excel(EXCEL_FILE)

# Verificar columnas necesarias
required_cols = {"Pregunta", "Respuesta", "Fuente"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"El Excel debe tener las columnas: {required_cols}")

# Inicializar motor de embeddings
modelo = SentenceTransformer("all-MiniLM-L6-v2")

# Inicializar base de datos vectorial
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="faq_tributarias")

# Insertar preguntas y variantes
ids, textos, metadatas = [], [], []
for i, row in df.iterrows():
    pregunta = str(row["Pregunta"])
    respuesta = str(row["Respuesta"])
    fuente = str(row["Fuente"])

    ids.append(str(i))
    textos.append(pregunta)
    metadatas.append({"respuesta": respuesta, "fuente": fuente})

collection.add(documents=textos, ids=ids, metadatas=metadatas)

# ==========================
# LOOP DE CONVERSACIÓN
# ==========================
while True:
    user_input = input("\nTú: ")
    if user_input.lower() in ["salir", "exit", "quit"]:
        print("VASEbot: ¡Hasta pronto! 👋")
        break

    # Buscar en base vectorial
    resultados = collection.query(
        query_texts=[user_input],
        n_results=1
    )

    if resultados["documents"] and resultados["metadatas"][0]:
        respuesta = resultados["metadatas"][0][0]["respuesta"]
        fuente = resultados["metadatas"][0][0]["fuente"]

        print(f"\nVASEbot: {respuesta}")
        print(f"Fuente: {fuente}")
        print(f"{DISCLAIMER}")
    else:
        print("\nVASEbot: No encontré una coincidencia clara. Reformula tu consulta.")