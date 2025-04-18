from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
import psutil
from datetime import datetime, timezone
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 🔹 Agregar el instrumentador de Prometheus
Instrumentator().instrument(app).expose(app)

# 📌 Endpoints de la API
@app.get("/")
def read_root():
    return {"message": "Bienvenido al Dashboard de Monitoreo"}

# 📌 Configuración de logs en formato JSON
def log_json_error(request: Request, error: Exception):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "url": str(request.url),
        "error": str(error)
    }
    try:
        with open("/app/logs/errors.json", "a") as log_file:
            json.dump(log_entry, log_file)
            log_file.write("\n")  # Asegura que cada entrada sea una nueva línea
    except Exception as log_error:
        logging.error(f"❌ ERROR al escribir en errors.json: {log_error}")

# 📌 Configuración de logging estándar
logging.basicConfig(
    filename="/app/logs/errors.log",
    filemode="a",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 📌 Middleware para capturar errores
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

# 📌 Manejador de excepciones global
@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    print(f"❌ Capturado en exception_handler: {exc}")
    log_json_error(request, exc)
    return JSONResponse(content={"detail": "Internal Server Error"}, status_code=500)

# 📌 Endpoints
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
