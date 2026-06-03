import os
import datetime
import time  # 👈 Añadido para el control de tiempo
from uuid import uuid4

import duckdb
import requests
from datetime import datetime, timezone

MARQUEZ_URL = "http://marquez:5000/api/v1/lineage"
JOB_NAME = "clean_ventas_bronze_to_silver"
NAMESPACE = "retail_data_department"
RUN_ID = str(uuid4())
DB_PATH = "./soda/retail_data.db"
SODA_CONF = "./soda/configuration.yml"
SODA_CHECKS = "./soda/ventas_silver_checks.yml"

# 👇 NUEVA FUNCIÓN: Sincronización inteligente de arranque
def wait_for_marquez():
    """Bloquea el pipeline hasta que la API de Marquez esté totalmente lista"""
    heartbeat_url = "http://marquez:5000/api/v1/namespaces"
    print("⏳ Esperando a que el servidor de Marquez esté totalmente operativo...")
    while True:
        try:
            # Intentamos realizar una consulta básica a la API de Marquez
            response = requests.get(heartbeat_url, timeout=2)
            if response.status_code == 200:
                print("✨ ¡Marquez está vivo y escuchando! Iniciando flujo de datos...")
                break
        except requests.RequestException:
            # Si da 'Connection refused' o cualquier error de red, ignoramos y seguimos esperando
            pass
        time.sleep(2)

def emit_openlineage_event(event_type, inputs=None, outputs=None):
    inputs = inputs or []
    outputs = outputs or []
    now = datetime.now(timezone.utc).isoformat()

    event = {
        "eventType": event_type,
        "eventTime": now,
        "run": {"runId": RUN_ID},
        "job": {"namespace": NAMESPACE, "name": JOB_NAME},
        "inputs": inputs,
        "outputs": outputs,
        "producer": "https://github.com/openlineage/practica-clase",
    }
    try:
        response = requests.post(MARQUEZ_URL, json=event, timeout=5)
        if response.status_code in [200, 201, 202]:
            print(f"[Lineage] Evento '{event_type}' enviado con éxito a Marquez.")
    except requests.RequestException as e:
        print(f"No se pudo enviar el evento a Marquez: {e}")

# 🚀 EJECUTAR LA ESPERA ACTIVA ANTES DE PROCESAR NADA
wait_for_marquez()

# --- A partir de aquí, tu código original intacto ---
conn = duckdb.connect(DB_PATH)
try:
    conn.execute("DROP TABLE IF EXISTS ventas_bronze;")
    conn.execute("""
        CREATE TABLE ventas_bronze (
            id_venta VARCHAR,
            cliente_id VARCHAR,
            precio_total DOUBLE,
            fecha_ingesta TIMESTAMP
        );
    """)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO ventas_bronze VALUES (?, ?, ?, ?)", ["V001", "C10", 99.99, now_str])
    conn.execute("INSERT INTO ventas_bronze VALUES (?, ?, ?, ?)", ["V001", "C10", 99.99, now_str])
    conn.execute("INSERT INTO ventas_bronze VALUES (?, ?, ?, ?)", ["V002", "C11", -5.50, now_str])
finally:
    conn.close()

print(f"🚀 Iniciando Pipeline Job: {JOB_NAME} (Run: {RUN_ID})")
input_dataset = [{"namespace": NAMESPACE, "name": "local_lakehouse.ventas_bronze"}]
output_dataset = [{"namespace": NAMESPACE, "name": "local_lakehouse.ventas_silver"}]

emit_openlineage_event("START", inputs=input_dataset)

print("🔍 Ejecutando Quality Gate con Soda Core...")
exit_code = os.system(f"soda scan -d local_lakehouse -c {SODA_CONF} {SODA_CHECKS}")

if exit_code != 0:
    print("❌ ERROR: Los datos de la capa Bronze no superaron el control de calidad.")
    print("🛑 Pipeline detenido de forma preventiva. Registrando fallo en Marquez.")
    emit_openlineage_event("FAIL", inputs=input_dataset)
else:
    print("✅ ÉXITO: Dimensiones de calidad validadas. Procesando a Capa Silver...")
    emit_openlineage_event("COMPLETE", inputs=input_dataset, outputs=output_dataset)