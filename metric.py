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
