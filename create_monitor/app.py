from openai import OpenAI

client = OpenAI(api_key="TU-API-KEY")

  # Asegúrate de usar tu clave API

from flask import Flask, request, render_template, jsonify

# Configuración de la clave API de OpenAI
  # Reemplaza esto con tu clave API

app = Flask(__name__)

app = Flask(__name__)

# Función para procesar el prompt con OpenAI
def process_prompt(prompt):
    try:
        # Realizamos la solicitud a la API de OpenAI usando el endpoint de chat
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # O usa "gpt-4" si tienes acceso
        messages=[
            {"role": "system", "content": "Eres experto en Graffana y Prometheus. Además de experto en json y python y yaml. Todas las respuestas que me des las quiero formateadas en json sacando los parametros necesarios para que las entienda la API de grafana y prometheus y me cree el monitor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7)

        # Obtén el texto de la respuesta
        ia_result = response.choices[0].message.content.strip()

        return {"result": ia_result}

    except Exception as e:
        print(f"Error al procesar el prompt con OpenAI: {e}")
        return {"error": "Ocurrió un error al procesar el prompt con OpenAI"}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form.get('prompt')  # Usa get() para evitar el KeyError
        if prompt:
            result = process_prompt(prompt)  # Llama al servicio de OpenAI para procesar el prompt
            return jsonify(result)  # Devolvemos el JSON con la respuesta procesada
        else:
            return jsonify({"error": "Prompt not received"}), 400

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)