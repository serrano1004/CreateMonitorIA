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
- Ejemplo de prompt: "Create a CPU monitor that alerts when usage exceeds 80% for 5 minutes."

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

## 3. Ejemplo de prompts

### 3.1 Monitoreo del tiempo de inicio de un proceso: 
- "Generate a Prometheus query to monitor the time taken to start a specific process running on the instance localhost:9090. Use the appropriate metric name and filter by the instance and process labels."
### 3.2 Monitoreo de la tasa de errores en consultas de base de datos:
- "Generate a Prometheus query to monitor the error rate for database queries for a service running on the instance localhost:9090. Use the appropriate metric name and filter by the instance and database labels."
### 3.3 Monitoreo de reinicios de contenedores:
- "Generate a Prometheus query to monitor the number of restarts for Docker containers running on the instance localhost:9090. Use the appropriate metric name and filter by the container and instance labels."
### 3.4 Monitoreo de la disponibilidad de una aplicación:
- "Generate a Prometheus query to monitor the uptime of a service running on the instance localhost:9090. Use the appropriate metric name and filter by the instance label."
