### 📊 Proyecto Destacado: Pipeline de Datos con Gobierno y Calidad (Data Governance)

Diseñé e implementé un entorno local completo de Ingeniería de Datos enfocado en la trazabilidad, linaje y validación automatizada de calidad (Quality Gates) antes de la ingesta del negocio.

#### 🛠️ Arquitectura y Tecnologías Utilizadas
* **Contenedores y Orquestación:** Docker & Docker Compose para el despliegue multi-servicio en aislamiento.
* **Almacenamiento (Data Lakehouse):** PostgreSQL (capas `bronze` y `silver`).
* **Calidad de Datos:** Soda Core (validaciones automáticas mediante archivos de configuración YAML).
* **Gobierno de Datos y Linaje:** Marquez API & Marquez UI (OpenLineage) para el rastreo y monitoreo de metadatos de los Jobs.
* **Control de Versiones:** Git & GitHub (Migración y sincronización del entorno de trabajo entre múltiples estaciones físicas).

#### 🚀 Flujo de Trabajo del Laboratorio
1. **Despliegue de Infraestructura:** Configuración y levantamiento de servicios backend (`marquez-server` en puerto `5001`, `postgres` en puerto `5432`) e interfaz gráfica (`marquez-web` en puerto `3000`).
2. **Control de Calidad Preventivo (Quality Gate):** Ejecución del pipeline de procesamiento (`pipeline.py`). El validador **Soda Core** interceptó el flujo detectando de forma automatizada anomalías críticas en los datos crudos (registros duplicados en `id_venta` y valores negativos en `precio_total`).
3. **Validación en Gobierno de Datos:** Análisis visual en la interfaz de **Marquez UI** para examinar el grafo de linaje de datos (*Data Lineage*). Se constató el registro oficial del estado **FAILED** y cómo el sistema bloqueó la creación de la capa limpia (`ventas_silver`) para proteger la integridad del repositorio final.

#### 📁 Evidencias del Proyecto
Las capturas de pantalla del comportamiento del sistema, logs de error de la terminal y los diagramas de flujo interactivos están completamente documentados y respaldados en la carpeta de evidencias de este repositorio.
