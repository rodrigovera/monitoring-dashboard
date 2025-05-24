import os
import json
import logging
import psutil
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from database import create_clients_table, insert_client
from database import get_db_connection
import httpx
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import asyncio
from fastapi.responses import Response
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://20.127.192.215:5173"],  # o usa ["*"] durante pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Métricas personalizadas que reflejan el estado del cliente
cpu_gauge = Gauge("custom_cpu_percent", "CPU usage (%) of client")
memory_gauge = Gauge("custom_memory_percent", "RAM usage (%) of client")
disk_gauge = Gauge("custom_disk_usage_percent", "Disk usage (%) of client")

create_clients_table()

CLIENTE_ACTUAL = 3  # Cliente por defecto

@app.post("/seleccionar-cliente")
def seleccionar_cliente(cliente_id: int):
    global CLIENTE_ACTUAL
    CLIENTE_ACTUAL = cliente_id
    return {"message": f"Cliente activo actualizado a {cliente_id}"}

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(actualizar_metricas_cliente())
    iniciar_pushgateway()

def iniciar_pushgateway():
    try:
        subprocess.Popen([
            "docker", "run", "-d",
            "--name", "pushgateway",
            "-p", "9091:9091",
            "prom/pushgateway"
        ])
        print("🚀 Push Gateway iniciado correctamente")
    except Exception as e:
        print(f"❌ Error al iniciar Push Gateway: {e}")

async def actualizar_metricas_cliente():
    global CLIENTE_ACTUAL
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT api_url FROM clients WHERE id = ?", (CLIENTE_ACTUAL,))
            cliente = cursor.fetchone()
            conn.close()

            if cliente:
                metrics_url = f"{cliente['api_url'].rstrip('/')}/metrics"
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(metrics_url)
                    if response.status_code == 200:
                        data = response.json()
                        cpu_gauge.set(data.get("cpu_percent", 0))
                        memory_gauge.set(data.get("memory_percent", 0))
                        disk_gauge.set(data.get("disk_usage", 0))
                        print(f"📈 Métricas actualizadas del cliente {CLIENTE_ACTUAL}")
        except Exception as e:
            print(f"❌ Error actualizando métricas del cliente {CLIENTE_ACTUAL}: {e}")
        await asyncio.sleep(10)

@app.get("/prometheus-metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Dashboard de Monitoreo"}

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_path = os.path.join(log_dir, 'errors.log')
log_json_path = os.path.join(log_dir, 'errors.json')

logging.basicConfig(
    filename=log_path,
    filemode="a",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_json_error(request: Request, error: Exception):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "url": str(request.url),
        "error": str(error)
    }
    try:
        with open(log_json_path, "a") as log_file:
            json.dump(log_entry, log_file)
            log_file.write("\n")
    except Exception as log_error:
        logging.error(f"❌ ERROR al escribir en errors.json: {log_error}")

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    print(f"🟡 Middleware activado para: {request.method} {request.url}")
    try:
        response = await call_next(request)
        print(f"🟢 Respuesta sin errores: {response.status_code}")
        return response
    except Exception as e:
        print(f"🔴 Middleware capturó un error: {e}")
        log_json_error(request, e)
        raise

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    print(f"❌ Capturado en exception_handler: {exc}")
    log_json_error(request, exc)
    return JSONResponse(content={"detail": "Internal Server Error"}, status_code=500)

@app.get("/metrics")
def get_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent
    }

@app.get("/cause_error")
def cause_error(request: Request):
    error = HTTPException(status_code=500, detail="Este es un error simulado para pruebas de logging")
    log_json_error(request, error)
    raise error

class ClienteRegistro(BaseModel):
    nombre: str
    email: str
    api_url: str
    token: str | None = None

@app.post("/clientes/register")
def registrar_cliente(cliente: ClienteRegistro):
    insert_client(
        cliente.nombre,
        cliente.email,
        cliente.api_url,
        cliente.token
    )
    return {"message": f"Cliente '{cliente.nombre}' registrado exitosamente en la base de datos"}

@app.get("/clientes")
def listar_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    rows = cursor.fetchall()
    conn.close()

    clientes = []
    for row in rows:
        clientes.append({
            "id": row["id"],
            "nombre": row["nombre"],
            "email": row["email"],
            "api_url": row["api_url"],
            "token": row["token"],
            "fecha_registro": row["fecha_registro"]
        })
    return clientes

@app.get("/clientes/{cliente_id}/metrics")
async def obtener_metrics_cliente(cliente_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()
    conn.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    api_url = cliente["api_url"]
    metrics_url = f"{api_url.rstrip('/')}/metrics"

    print(f"📡 Consultando métricas para cliente {cliente_id}")
    print(f"🔗 URL objetivo: {metrics_url}")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(metrics_url)

        response.raise_for_status()

        if 'application/json' in response.headers.get('content-type', ''):
            return response.json()
        else:
            return JSONResponse(content={"metrics": response.text})

    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"No se pudo obtener /metrics del cliente: {str(e)}")

@app.get("/logs")
async def obtener_logs_loki(limit: int = 10, query: str = Query("error")):
    loki_url = "http://loki:3100/loki/api/v1/query_range"
    loki_query = f'{{job="errors"}} |= "{query}"'

    params = {
        "query": loki_query,
        "limit": limit
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(loki_url, params=params)
        response.raise_for_status()

        data = response.json()
        logs = []

        for stream in data.get("data", {}).get("result", []):
            for entry in stream.get("values", []):
                timestamp_ns, log_line = entry
                timestamp = datetime.fromtimestamp(int(timestamp_ns) / 1e9, tz=timezone.utc)
                logs.append({
                    "timestamp": timestamp.isoformat(),
                    "log": log_line.strip()
                })

        return logs

    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar Loki: {str(e)}")
