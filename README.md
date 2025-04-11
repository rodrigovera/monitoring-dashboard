# 📊 Stack de Monitoreo con FastAPI + Prometheus + Grafana + Loki

Este proyecto implementa una solución de monitoreo local utilizando:

- ⚙️ **FastAPI** como aplicación base.
- 📈 **Prometheus** para recolección de métricas.
- 📊 **Grafana** para visualización.
- 📦 **Loki + Promtail** para centralización de logs en tiempo real.

---

## 🚀 ¿Qué monitorea?

- 🔥 **Métricas del sistema**: uso de CPU, RAM y Disco (via `psutil`).
- 🌐 **Métricas HTTP**: número de peticiones, errores, etc.
- 🧾 **Logs de errores**: centralizados y visualizados desde archivos `.json` y `.log`.

---

## 📁 Estructura del proyecto

```
.
├── fastapi/                    # App principal FastAPI
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
├── grafana/                    # Dashboards y datasources
│   └── provisioning/
│       ├── dashboards/
│       │   ├── dashboards.json
│       │   └── dashboards.yml
│       └── datasource/
│           └── datasource.yml
├── loki-config/                # Configuración de Loki
│   └── loki-config.yml
├── logs/                       # Logs generados
│   ├── error.json
│   └── error.log
├── prometheus/                 # Configuración de Prometheus
│   └── prometheus.yml
├── promtail/                   # Configuración de Promtail
│   └── logs/
│       └── error.json
├── docker-compose.yml          # Stack completo
├── config.yml                  # Config opcional
└── position.yaml               # Posición de lectura de Promtail
```

---

## 🐳 Cómo ejecutar

1. Clona el repositorio:

```bash
git clone https://github.com/rodrigovera/monitoring-stack.git
cd monitoring-stack
```

2. Levanta los servicios con Docker Compose:

```bash
docker-compose up --build
```

3. Accede a:

- 🔧 **FastAPI**: [http://localhost:8000](http://localhost:8000)
- 📊 **Grafana**: [http://localhost:3000](http://localhost:3000)
  - Usuario: `admin`
  - Contraseña: `admin`
- 🔍 Endpoints útiles:
  - `/metrics`: métricas del sistema
  - `/cause_error`: genera un error intencional para ver logs

---

## ✨ Screenshots

_(Opcional: puedes agregar capturas de tu dashboard en acción aquí)_

---

## 📌 Notas

- Asegúrate de tener Docker y Docker Compose instalados.
- Los logs y dashboards están preconfigurados para mostrar información automáticamente.
- Si vas a desplegar en producción o en la nube, cambia credenciales por defecto y configura volúmenes persistentes de manera segura.

---

## 📬 Contacto

Cualquier sugerencia o mejora es bienvenida.  
_Proyecto desarrollado por [Rodrigo Vera](https://github.com/rodrigovera)._
