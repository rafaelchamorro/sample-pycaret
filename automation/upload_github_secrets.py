"""
Script de automatización para configurar y encriptar los secretos de GitHub Actions
utilizando libsodium SealedBox y las credenciales activas de Azure y Git.
"""

import os
import json
import base64
import subprocess
import requests
from nacl import encoding, public

REPO = "rafaelchamorro/sample-pycaret"

def get_git_token():
    """Obtiene el token de autenticación desde el Git Credential Manager."""
    try:
        proc = subprocess.Popen(
            ["git", "credential", "fill"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, _ = proc.communicate("protocol=https\nhost=github.com\n")
        for line in out.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception as e:
        print(f"No se pudo obtener token de git: {e}")
    return os.environ.get("GITHUB_TOKEN")

def get_public_key(token: str):
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()

def encrypt_secret(public_key_str: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_secret(secret_name: str, secret_value: str, key_id: str, public_key_str: str, token: str):
    encrypted_value = encrypt_secret(public_key_str, secret_value)
    url = f"https://api.github.com/repos/{REPO}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in (201, 204):
        print(f"[OK] Secreto '{secret_name}' guardado exitosamente.")
    else:
        print(f"[ERROR] Al guardar '{secret_name}': {res.status_code} - {res.text}")

def main():
    token = get_git_token()
    if not token:
        print("[ERROR] No se pudo encontrar el token de GitHub.")
        return

    print("Obteniendo credenciales de Azure...")
    acr_res = subprocess.check_output("az acr credential show --name pycaret1", shell=True)
    acr_data = json.loads(acr_res)
    acr_username = acr_data["username"]
    acr_password = acr_data["passwords"][0]["value"]
    acr_server = "pycaret1.azurecr.io"

    print("Obteniendo perfil de publicación de Azure Web App...")
    publish_xml = subprocess.check_output(
        "az webapp deployment list-publishing-profiles --name pycaret1 --resource-group gr_mmrr --xml",
        shell=True,
        text=True
    ).strip()

    secrets = {
        "ACR_LOGIN_SERVER": acr_server,
        "ACR_USERNAME": acr_username,
        "ACR_PASSWORD": acr_password,
        "AZURE_WEBAPP_NAME": "pycaret1",
        "AZURE_WEBAPP_PUBLISH_PROFILE": publish_xml
    }

    print(f"Obteniendo llave pública del repositorio {REPO}...")
    pub_info = get_public_key(token)
    key_id = pub_info["key_id"]
    public_key = pub_info["key"]

    print(f"Guardando {len(secrets)} secretos en GitHub Actions...")
    for name, value in secrets.items():
        set_secret(name, value, key_id, public_key, token)

    print("\n[EXITO] Todos los secretos fueron configurados en GitHub!")

if __name__ == "__main__":
    main()
