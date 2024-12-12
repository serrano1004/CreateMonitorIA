from openai import OpenAI
import requests
import json

client = OpenAI(api_key="")
GRAFANA_API_URL = "http://localhost:3000/api/dashboards/db"  # Reemplaza <GRAFANA_HOST> con la URL de tu Grafana
GRAFANA_API_TOKEN = ""

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
            {"role": "system", "content": "Eres experto en Grafana y Prometheus. Todas las respuestas deben ser un JSON perfectamente formateado para la API de Grafana. Asegúrate de que las comillas, llaves y corchetes estén correctamente cerrados."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7)

        # Obtén el texto de la respuesta
        ia_result = response.choices[0].message.content.strip()
        print(f"Respuesta de OpenAI: {ia_result}")  # Imprime la respuesta para debug

         # Valida y carga el JSON
        try:
            alert_json = json.loads(ia_result)  # Intenta cargar el JSON generado
        except json.JSONDecodeError as json_error:
            print(f"Error al decodificar JSON: {json_error}")
            return {"error": f"El JSON generado por OpenAI no es válido: {ia_result}"}

        # Crea el monitor en Grafana
        grafana_result = create_monitor_in_grafana(alert_json)

        return grafana_result

    except Exception as e:
        print(f"Error processing prompt with OpenAI: {e}")
        return {"error": f"An error occurred while processing the prompt with OpenAI: {e}"}

def create_monitor_in_grafana(alert_json):
    try:
        headers = {
            "Authorization": f"Bearer {GRAFANA_API_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(GRAFANA_API_URL, json=alert_json, headers=headers)
        response.raise_for_status()  # Lanza un error si la solicitud falla
        return {"status": "success", "message": "Monitor successfully created in Grafana"}
    except requests.exceptions.RequestException as e:
        print(f"Error creating monitor in Grafana: {e}")
        return {"status": "error", "message": f"Failed to create monitor in Grafana: {e}"}

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