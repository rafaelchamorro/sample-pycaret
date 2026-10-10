"""
Script de Automatización y Documentación con Playwright
Diseñado para capturar paso a paso la configuración de Azure Container Registry (ACR),
Azure Web App y GitHub Actions utilizando la sesión autenticada de Google Chrome.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext

DOCS_DIR = Path("docs")
SCREENSHOTS_DIR = DOCS_DIR / "screenshots"
DOC_FILE = DOCS_DIR / "EVIDENCIAS_PASO_A_PASO.md"


def init_doc_file(rg_name: str, acr_name: str, webapp_name: str, github_repo: str):
    """Inicializa el archivo Markdown de evidencias."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    header = f"""# 📘 Evidencias de Despliegue MLOps en Azure & GitHub Actions

**Fecha de ejecución:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Repositorio GitHub:** `{github_repo}`  
**Resource Group en Azure:** `{rg_name}`  
**Azure Container Registry (ACR):** `{acr_name}.azurecr.io`  
**Azure Web App:** `https://{webapp_name}.azurewebsites.net`  

---

## 🎯 Resumen del Pipeline MLOps
1. **Calidad y Tests (CI):** Validación del modelo PyCaret (`deployment_20260516.pkl`) y endpoints Flask (`/health`, `/predict_api`) vía Pytest.
2. **Empaquetado y Publicación (ACR):** Creación de imagen Docker multi-etapa y push a Azure Container Registry.
3. **Despliegue Continuo (CD):** Despliegue automático a Azure Web App for Containers y verificación de salud.

---

## 📸 Paso a Paso y Evidencias Documentadas

"""
    with open(DOC_FILE, "w", encoding="utf-8") as f:
        f.write(header)
    print(f"✅ Documento inicializado en: {DOC_FILE}")


def append_evidence(step_num: int, title: str, description: str, screenshot_filename: str):
    """Agrega un paso y su captura al documento Markdown."""
    rel_path = f"screenshots/{screenshot_filename}"
    entry = f"""### Paso {step_num}: {title}
**Descripción:** {description}

![{title}]({rel_path})

---
"""
    with open(DOC_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"  📸 Evidencia registrada: Paso {step_num} -> {screenshot_filename}")


def capture_screenshot(page: Page, filename: str) -> str:
    """Toma una captura de pantalla completa o visible."""
    path = SCREENSHOTS_DIR / filename
    page.screenshot(path=str(path), full_page=False)
    return filename


def connect_or_launch_browser(playwright_instance, mode: str, cdp_url: str):
    """Conecta Playwright a Chrome vía CDP o lanza una instancia de Chrome del sistema."""
    if mode == "cdp":
        print(f"🔌 Intentando conectar vía Chrome DevTools Protocol (CDP) a {cdp_url}...")
        try:
            browser = playwright_instance.chromium.connect_over_cdp(cdp_url)
            print(" Connected exitosamente al Google Chrome activo.")
            return browser, browser.contexts[0]
        except Exception as e:
            print(f"❌ No se pudo conectar vía CDP ({e}).")
            print("💡 Sugerencia: Inicia Google Chrome con el parámetro:")
            print("   chrome.exe --remote-debugging-port=9222")
            print("   O ejecuta este script con `--mode launch`.")
            sys.exit(1)
    else:
        print("🚀 Lanzando Google Chrome del sistema con canal local...")
        user_data = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default")
        # Usamos channel='chrome' para aprovechar la instalación existente
        browser = playwright_instance.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--start-maximized"]
        )
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        return browser, context


def get_or_create_page(context: BrowserContext, target_url_keyword: str = "portal.azure.com") -> Page:
    """Busca una pestaña abierta que coincida con la URL o crea una nueva."""
    for page in context.pages:
        if target_url_keyword in page.url:
            print(f"📑 Encontrada pestaña abierta con: {page.url}")
            page.bring_to_front()
            return page
    
    # Si no existe, crea una nueva
    page = context.new_page()
    return page


def run_documentation(
    rg_name: str,
    acr_name: str,
    webapp_name: str,
    github_repo: str,
    mode: str = "cdp",
    cdp_url: str = "http://localhost:9222",
    interactive: bool = True
):
    """Ejecuta el flujo de documentación paso a paso."""
    init_doc_file(rg_name, acr_name, webapp_name, github_repo)

    with sync_playwright() as p:
        browser, context = connect_or_launch_browser(p, mode, cdp_url)
        page = get_or_create_page(context, "portal.azure.com")

        steps = [
            {
                "step": 1,
                "title": "Portal de Azure y Grupo de Recursos",
                "description": f"Verificación del Resource Group `{rg_name}` que contiene los recursos del proyecto.",
                "url": f"https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups",
                "filename": "01_azure_resource_group.png",
                "prompt": "Navega a la vista de tu Grupo de Recursos en Azure Portal y presiona ENTER..."
            },
            {
                "step": 2,
                "title": "Azure Container Registry (ACR) - Información General",
                "description": f"Panel de control del registro de contenedores `{acr_name}` mostrando el Servidor de Inicio de Sesión (`{acr_name}.azurecr.io`).",
                "url": f"https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.ContainerRegistry%2Fregistries",
                "filename": "02_acr_overview.png",
                "prompt": f"Navega al ACR `{acr_name}` (Overview) y presiona ENTER..."
            },
            {
                "step": 3,
                "title": "Azure Container Registry - Claves de Acceso (Admin User)",
                "description": "Visualización de las credenciales de administrador (Username y Password) configuradas para el login de Docker.",
                "url": None,
                "filename": "03_acr_access_keys.png",
                "prompt": "En el menú izquierdo del ACR, haz clic en 'Claves de acceso' (Access keys) y presiona ENTER..."
            },
            {
                "step": 4,
                "title": "Azure App Service (Web App for Containers)",
                "description": f"Vista general del servicio de aplicaciones `{webapp_name}` configurado para alojar el contenedor Docker.",
                "url": f"https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites",
                "filename": "04_azure_webapp_overview.png",
                "prompt": f"Navega al Web App `{webapp_name}` (Overview) y presiona ENTER..."
            },
            {
                "step": 5,
                "title": "Azure Web App - Configuración y Puerto (WEBSITES_PORT)",
                "description": "Validación de la variable de entorno `WEBSITES_PORT=5000` en la configuración de la aplicación.",
                "url": None,
                "filename": "05_azure_webapp_configuration.png",
                "prompt": "En el menú de la Web App, entra a 'Configuración' (Variables de entorno / App Settings) y presiona ENTER..."
            },
            {
                "step": 6,
                "title": "GitHub Secrets and Variables - Actions",
                "description": f"Configuración de los secretos (`ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`, `AZURE_WEBAPP_NAME`, `AZURE_WEBAPP_PUBLISH_PROFILE`) en el repositorio `{github_repo}`.",
                "url": f"https://github.com/{github_repo}/settings/secrets/actions",
                "filename": "06_github_actions_secrets.png",
                "prompt": "Navega a GitHub > Settings > Secrets and variables > Actions y presiona ENTER..."
            },
            {
                "step": 7,
                "title": "Ejecución del Workflow de GitHub Actions (CI/CD)",
                "description": "Historial de ejecuciones de GitHub Actions mostrando los jobs de validación, construcción y despliegue completados exitosamente.",
                "url": f"https://github.com/{github_repo}/actions",
                "filename": "07_github_actions_pipeline_run.png",
                "prompt": "Navega a la pestaña 'Actions' de GitHub y presiona ENTER..."
            }
        ]

        for s in steps:
            print(f"\n[{s['step']}/7] 📌 {s['title']}")
            if s["url"] and not interactive:
                page.goto(s["url"])
                page.wait_for_timeout(3000)

            if interactive:
                input(f"👉 {s['prompt']} ")
            else:
                time.sleep(2)

            page.bring_to_front()
            time.sleep(1)
            filename = capture_screenshot(page, s["filename"])
            append_evidence(s["step"], s["title"], s["description"], filename)

        print("\n🎉 ¡Documentación completada con éxito!")
        print(f"📄 Reporte generado: {DOC_FILE.resolve()}")
        print(f"🖼️ Capturas guardadas en: {SCREENSHOTS_DIR.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Documentador Playwright para Azure & GitHub Actions MLOps")
    parser.add_argument("--rg-name", default="modeldeploy", help="Nombre del Resource Group en Azure")
    parser.add_argument("--acr-name", default="pycaret1", help="Nombre del Azure Container Registry")
    parser.add_argument("--webapp-name", default="pycaret1", help="Nombre de la Azure Web App")
    parser.add_argument("--github-repo", default="rafaelchamorro/sample-pycaret", help="Usuario/repo de GitHub")
    parser.add_argument("--mode", choices=["cdp", "launch"], default="cdp", help="Modo: cdp (Chrome activo) o launch (nueva ventana)")
    parser.add_argument("--cdp-url", default="http://localhost:9222", help="URL del puerto de depuración de Chrome")
    parser.add_argument("--non-interactive", action="store_true", help="Ejecutar en modo no interactivo automático")

    args = parser.parse_args()

    run_documentation(
        rg_name=args.rg_name,
        acr_name=args.acr_name,
        webapp_name=args.webapp_name,
        github_repo=args.github_repo,
        mode=args.mode,
        cdp_url=args.cdp_url,
        interactive=not args.non_interactive
    )
