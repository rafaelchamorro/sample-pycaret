# 🚀 Arquitectura MLOps: PyCaret + Azure Container Registry + Azure Web App

Esta guía describe la arquitectura de grado de producción implementada para el ciclo de vida de Machine Learning (MLOps) del proyecto PyCaret Insurance Cost Prediction.

---

## 🏛️ Diagrama del Flujo CI/CD

```mermaid
flowchart TD
    subgraph CI["1. Continuous Integration (GitHub Actions)"]
        A[Git Push / PR en main] --> B[Checkout & Setup Python 3.11]
        B --> C[Instalar Dependencias]
        C --> D[Quality Gate: Pytest]
        D -->|Validar Modelo| E[test_model.py: PyCaret Pipeline]
        D -->|Validar API| F[test_api.py: /health & /predict_api]
    end

    subgraph Package["2. Container Registry (ACR)"]
        E & F -->|Tests Aprobados| G[Docker Buildx Setup]
        G --> H[Login seguro en Azure Container Registry]
        H --> I[Build & Tag: sha y latest]
        I --> J[Push a <acr_name>.azurecr.io/pycaret-insurance-app]
    end

    subgraph CD["3. Continuous Deployment (Azure)"]
        J --> K[azure/webapps-deploy@v3]
        K --> L[Azure Web App for Containers]
        L --> M[Configuración WEBSITES_PORT=5000]
        M --> N[Smoke Test: Validar /health HTTP 200]
    end
```

---

## 🔑 Secretos Requeridos en GitHub Actions
En tu repositorio de GitHub (`Settings > Secrets and variables > Actions > Repository secrets`):

| Secreto GitHub | Descripción | Dónde obtenerlo en Azure Portal |
|---|---|---|
| `ACR_LOGIN_SERVER` | URL del registro (ej. `acrpycaretmlops.azurecr.io`) | ACR > Overview > Login server |
| `ACR_USERNAME` | Nombre de usuario administrador del ACR | ACR > Access keys > Username |
| `ACR_PASSWORD` | Contraseña del usuario administrador del ACR | ACR > Access keys > password |
| `AZURE_WEBAPP_NAME` | Nombre de tu App Service (ej. `app-pycaret-mlops`) | App Services > Name |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Contenido XML del perfil de publicación | Web App > Overview > "Download publish profile" |

---

## 🧪 Pruebas Automatizadas de Calidad (Quality Gate)
Antes de construir la imagen Docker, el runner ejecuta:
- **`tests/test_model.py`**:
  - Verifica la integridad física del artefacto serializado `deployment_20260516.pkl`.
  - Carga el pipeline con `pycaret.regression.load_model` y ejecuta inferencia con un payload de prueba.
  - Asegura que el valor predicho sea un costo válido positivo.
- **`tests/test_api.py`**:
  - Valida el endpoint de monitoreo y health check (`GET /health`).
  - Valida la respuesta del formulario HTML (`GET /`).
  - Valida el endpoint REST de producción (`POST /predict_api`) asegurando formato JSON y tipo de datos numéricos.

---

## 🎭 Automatización y Captura de Evidencias con Playwright

Hemos implementado un script especializado en `automation/document_azure_setup.py`:
- **Conexión CDP (Recomendada):** Se acopla a tu Google Chrome abierto con Azure sin requerir volver a ingresar credenciales ni 2FA.
- **Generación de Markdown:** Guarda capturas en `docs/screenshots/` y actualiza automáticamente `docs/EVIDENCIAS_PASO_A_PASO.md`.
