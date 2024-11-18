# CreateMonitorIA
Creando monitores a partir de prompts.

## 1. Configuración Inicial
Instalación de Prometheus y Grafana: 
- Configura Prometheus con los targets que quieres monitorear (p. ej., servidores, aplicaciones, o contenedores) en el archivo prometheus.yml.

```bash
global:
  scrape_interval: 15s  # Intervalo para capturar métricas

scrape_configs:
  - job_name: "mi_servicio"
    static_configs:
      - targets: ["localhost:9090"]  # Cambia esto a la URL del servicio que quieres monitorear
```
 - Puedes instalar Prometheus y Grafana en contenedores Docker o en un servidor dedicado. Recuerda usar la misma red. 

```bash
docker network create monitoring
docker run -d --name prometheus --network monitoring -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
docker run -d --name=grafana -p 3000:3000 --network monitoring grafana/grafana
```
Integración de Grafana con Prometheus:
 - Abre Grafana en tu navegador en http://localhost:3000 (ajusta la URL según tu configuración).
 - Inicia sesión (la configuración predeterminada suele ser usuario admin y contraseña admin en instalaciones nuevas).
 - En Grafana, añade Prometheus como fuente de datos (Settings > Data Sources > Add data source > selecciona Prometheus).
 - Configuración de Permisos (Opcional): Si usas un ambiente compartido, asegúrate de configurar los permisos para manejar las alertas y visualizaciones.
 - En la página de configuración de la fuente de datos, en el campo URL, ingresa la dirección de Prometheus. Si estás ejecutando Prometheus en la misma máquina, la URL será http://localhost:9090.
 - En la sección HTTP settings, asegúrate de que esté seleccionado Access como Server (si Grafana y Prometheus están en la misma red).
 - Haz clic en Save & Test para verificar que la conexión es exitosa

Para que Prometheus pueda monitorear un servicio, este servicio debe exponer sus métricas en un formato que Prometheus pueda entender. En general, esto significa que el servicio necesita exponer las métricas en texto plano en una URL accesible, habitualmente en la ruta /metrics. Este es el formato de datos que Prometheus espera y que utiliza para recopilar y almacenar las métricas.

Aquí te detallo el proceso para asegurarte de que el servicio expone las métricas en el formato adecuado para Prometheus:

#### Paso 1: Confirmar el EndPoint /metrics del Servicio
Verifica si tu servicio ya expone métricas:
- Algunos servicios y aplicaciones ya vienen con un endpoint /metrics configurado para Prometheus. Por ejemplo, algunos servidores web, bases de datos y servicios de nube ofrecen métricas en /metrics.
- Si tu servicio no expone métricas en esta URL, tendrás que hacer uno de los siguientes pasos:
 1. Incorporar un cliente de Prometheus en el código de tu aplicación.
 2. Utilizar un exportador para convertir las métricas de tu servicio al formato Prometheus.

Prueba el Endpoint:
Accede a http://<tu_servicio>:<puerto>/metrics en tu navegador o usando curl para verificar si se exponen las métricas. Por ejemplo:
```bash
curl http://localhost:9090/metrics
```
Si el endpoint está configurado correctamente, deberías ver una lista de métricas en formato de texto plano, como este ejemplo:
```bash
# HELP go_gc_duration_seconds A summary of the pause duration of garbage collection cycles.
# TYPE go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 0.0001343
go_gc_duration_seconds{quantile="0.25"} 0.0001512
go_gc_duration_seconds{quantile="0.5"} 0.0002153
go_gc_duration_seconds{quantile="0.75"} 0.0003802
go_gc_duration_seconds{quantile="1"} 0.0027316
```
#### Paso 2: Usar un Cliente de Prometheus en tu Aplicación
Si tu aplicación no tiene soporte para Prometheus, puedes integrar un cliente de Prometheus en el código. Existen bibliotecas para varios lenguajes:
 - Python: prometheus_client
 - Java: simpleclient
 - Go: prometheus
 - Node.js: prom-client

Ejemplo: Configurar un Cliente de Prometheus en Python
Este ejemplo en Python muestra cómo usar la biblioteca prometheus_client para exponer métricas en /metrics:
Instala la biblioteca:
```bash
pip install prometheus_client
```
Código para exponer métricas:
- Configura el cliente para recolectar y exponer métricas en /metrics.
```Python
from prometheus_client import start_http_server, Summary
import random
import time

# Creamos una métrica de resumen para medir la latencia.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorador para medir el tiempo de ejecución
@REQUEST_TIME.time()
def process_request():
    time.sleep(random.random())

if __name__ == '__main__':
    # Inicia el servidor en el puerto 8000
    start_http_server(8000)
    while True:
        process_request()
```
Este script expone las métricas en http://localhost:8000/metrics.

## 2. Procesamiento del Prompt
### 2.1 Herramienta de Procesamiento de Lenguaje Natural (NLP):
- Utiliza un modelo NLP (como OpenAI o spaCy) para interpretar el prompt.
- Si optas por OpenAI, puedes usar su API para convertir prompts en estructuras de datos JSON que representen las métricas y configuraciones deseadas.
- Ejemplo de prompt: "Crea un monitor de CPU que alerte cuando el uso supere el 80% durante 5 minutos."

#### 2.1.1 Configuración del Entorno de Desarrollo
Instala las Dependencias:
1. Necesitarás instalar las siguientes herramientas:
 - Python: Lenguaje para manejar la lógica del procesamiento.
 - Flask: Para crear una interfaz web simple.
 - NLTK o spaCy: Para el procesamiento de lenguaje natural.
 - Prometheus Client: Para gestionar las métricas.
2. Ejecuta: 
```bash 
pip install flask spacy prometheus_client
```
3. Si eliges spaCy para el procesamiento NLP, asegúrate de descargar el modelo de lenguaje:
```bash 
python -m spacy download en_core_web_sm
```
Diseñar la Interfaz de Usuario en Flask
 - Crea una interfaz web donde se pueda introducir el prompt. Este prompt debe ser una oración en lenguaje natural que describe la métrica y las condiciones de alerta.
 - Crear la Estructura del Proyecto:
```bash
  create_monitor/
├── app.py
├── templates/
│   └── index.html
└── static/
    └── style.css
```
Interpretar el Prompt en Datos para Prometheus
 - Procesar el Prompt:
  1. Usa el modelo spaCy cargado para extraer entidades clave como el nombre de la métrica, el umbral, y la condición (por encima o por debajo del umbral).
  2. Por ejemplo, si el prompt es "Alert me if CPU usage goes above 80%", el código extraerá "CPU usage" como métrica, 80 como umbral, y above como condición.
 - Crear la Estructura de Datos:
  1. La función process_prompt convierte el prompt en un diccionario
```json
{
  "metric_name": "CPU usage",
  "threshold": 80.0,
  "alert_condition": "above"
}
```
Almacenar y Gestionar las Métricas en Prometheus
 - Crear Métrica en Prometheus:
  1. Usa la biblioteca prometheus_client para definir una métrica con el nombre extraído:
```Python
if metric_name not in metrics:
    metrics[metric_name] = Gauge(metric_name, f'Métrica para {metric_name}')
```
 - Establecer Condiciones de Alerta:
  1. A partir de aquí, podrás configurar una alerta en Prometheus usando esta métrica y las condiciones de alerta definidas en el prompt.
 - Probar el Sistema:
  1. Ejecuta el servidor Flask y prueba el prompt desde la interfaz web en http://localhost:5000.
  2. Envía distintos prompts y verifica si los datos se procesan correctamente.

### 2.2 Extracción de Parámetros del Prompt:
- Define un script para extraer los detalles específicos del prompt (métrica, umbrales, duración, etc.).
- Código de ejemplo en Python para procesar el prompt:
```Python
import openai

def process_prompt(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Extract the monitoring details from the following text: {prompt}",
        max_tokens=100
    )
    return response["choices"][0]["text"]
```
- Configura OpenAI para interpretar y mapear frases como "alerta de CPU" a metric: cpu_usage, "80%" a threshold: 80, y "5 minutos" a duration: 5m.

## 3. Generación de Configuración para Prometheus
### 3.1 Mapeo de Prompt a Configuración YAML
- Usa los parámetros extraídos para construir un archivo de reglas de Prometheus en formato YAML.
- Código de ejemplo para generar una alerta a partir de los datos extraídos:

```Python
def generate_prometheus_alert(metric, threshold, duration):
    alert = f"""
    groups:
    - name: example
      rules:
      - alert: {metric}_HighUsage
        expr: {metric} > {threshold}
        for: {duration}
        labels:
          severity: critical
        annotations:
          summary: "High utilization of {metric}"
          description: "Usage of {metric} has exceeded {threshold}% for the last {duration}."
    """
    with open("alert.rules.yml", "w") as file:
        file.write(alert)
```
### 3.2 Carga de Configuración en Prometheus
- Añade el archivo alert.rules.yml en el directorio de Prometheus y recarga la configuración:
```bash
docker exec prometheus kill -HUP 1
```

## 4. Creación de Panel y Alerta en Grafana desde el Prompt
### 4.1 API de Grafana:
- Configura un script que llame a la API de Grafana para crear un panel de visualización de métricas y una alerta.
- Código en Python para crear un panel en Grafana:

```Python
import requests

def create_grafana_panel(metric, threshold, duration):
    grafana_api_url = "http://localhost:3000/api/dashboards/db"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_GRAFANA_API_KEY"
    }
    dashboard_config = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": f"{metric} Dashboard",
            "panels": [
                {
                    "type": "graph",
                    "title": f"{metric} Usage",
                    "targets": [{"expr": f"{metric}"}],
                    "alert": {
                        "conditions": [
                            {
                                "evaluator": {"params": [threshold], "type": "gt"},
                                "operator": {"type": "and"},
                                "query": {"params": ["A", "5m", "now"]},
                                "reducer": {"type": "avg"},
                                "type": "query"
                            }
                        ],
                        "name": f"{metric} High Usage",
                        "frequency": "1m"
                    }
                }
            ],
            "schemaVersion": 16
        }
    }
    response = requests.post(grafana_api_url, json=dashboard_config, headers=headers)
    print(response.json())
```
- Este código configura un panel de Grafana que visualiza la métrica especificada y configura una alerta cuando la métrica supera el umbral.

## 5. Automatización y Pruebas
### 5.1 Automatización
- Puedes empaquetar el proceso en un script principal que tome el prompt, genere las reglas y llame a las APIs de Prometheus y Grafana.
- Ejemplo de función principal:

```Python
def main():
    prompt = "Create a CPU monitor that alerts when usage exceeds 80% for 5 minutes."
    details = process_prompt(prompt)
    metric, threshold, duration = details["metric"], details["threshold"], details["duration"]

    # Crear alerta de Prometheus
    generate_prometheus_alert(metric, threshold, duration)

    # Crear panel de Grafana
    create_grafana_panel(metric, threshold, duration)
```
### 5.2 Pruebas y Ajustes:
- Realiza pruebas con diferentes prompts para asegurar que las configuraciones de monitorización generadas sean precisas.
- Ajusta el modelo NLP para interpretar adecuadamente las variaciones en los prompts.

## 6. Integración con Prometheus y Alertas (Configuración de Alertmanager)
Configura Prometheus y crea una alerta en alert.rules usando las métricas generadas:
```yaml
groups:
  - name: example_alert
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage > 80  # Usa los datos generados
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "El uso de CPU está sobre el 80%"
          description: "El uso de CPU ha excedido el umbral definido."
```
Con estos pasos, tienes una interfaz que convierte un prompt en una métrica de Prometheus con alertas configuradas.

El archivo alert.rules es donde se definen las reglas de alerta para Prometheus. Generalmente, este archivo se coloca en una ubicación específica que luego se referencia en el archivo de configuración principal de Prometheus (prometheus.yml).

### 6.1 Pasos para Crear alert.rules
1. Ubicación del Archivo alert.rules:
- Puedes crear el archivo alert.rules en la misma carpeta donde tienes el archivo prometheus.yml, para mantener la configuración centralizada.
- Por ejemplo, si tu archivo prometheus.yml está en /path/to/prometheus/, puedes colocar alert.rules en esa misma carpeta.

2. Contenido de alert.rules: Crea el archivo alert.rules y agrega tus reglas de alerta. Por ejemplo:
```yaml
groups:
  - name: example_alert
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage > 80  # Condición para activar la alerta
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CPU usage is high"
          description: "CPU usage has exceeded the 80% threshold."
```
3. Configurar prometheus.yml para Incluir alert.rules: En el archivo prometheus.yml, añade una sección para cargar las reglas de alerta:
```yaml
rule_files:
  - /path/to/prometheus/alert.rules
```
Asegúrate de reemplazar /path/to/prometheus/ con la ruta real de tu archivo alert.rules.

4. Reiniciar Prometheus: Después de configurar las alertas, reinicia Prometheus para que cargue las nuevas reglas:
```bash
docker restart prometheus
```

### 6.2 Ejemplo Completo del archivo prometheus.yml
Un ejemplo de cómo se vería el archivo prometheus.yml con la configuración de alertas:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

rule_files:
  - /path/to/prometheus/alert.rules  # Ruta al archivo de reglas de alerta
```
### 6.3 Verificación
Una vez que has reiniciado Prometheus, puedes verificar que las reglas de alerta se hayan cargado correctamente accediendo a la interfaz web de Prometheus en http://localhost:9090 y navegando a Alerts. Ahí podrás ver las reglas de alerta activas y sus estados actuales.