from flask import Flask, request, render_template, jsonify
import spacy
from prometheus_client import Gauge

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
metrics = {}

def process_prompt(prompt):
    doc = nlp(prompt)
    metric_name = None
    threshold = None
    alert_condition = None

    # Nuevas palabras clave para el procesamiento
    alert_keywords = ['latency', 'cpu', 'memory', 'use']
    condition_keywords = ['above', 'exceed', 'more', 'below']

    for token in doc:
        if token.text.lower() in alert_keywords:
            metric_name = token.text
        elif token.pos_ == "NUM":
            threshold = float(token.text)
        elif token.text.lower() in condition_keywords:
            alert_condition = token.text

    if metric_name and threshold and alert_condition:
        return {
            "metric_name": metric_name,
            "threshold": threshold,
            "alert_condition": alert_condition
        }
    else:
        print("No se pudo interpretar el prompt.")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form.get('prompt')  # Usa get() para evitar el KeyError
        if prompt:
            result = process_prompt(prompt)
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "No se pudo interpretar el prompt"}), 400
        else:
            return jsonify({"error": "Prompt no recibido"}), 400

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
