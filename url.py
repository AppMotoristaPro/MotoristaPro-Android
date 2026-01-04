import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÃO ---
BACKUP_ROOT = Path("backup_automatico")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
COMMIT_MSG = "Fix: Apontar WebView para URL de Producao"

# --- URL OFICIAL IDENTIFICADA NOS SEUS ARQUIVOS ---
# Se sua URL mudou, edite apenas a linha abaixo:
PRODUCTION_URL = "https://motorista-pro-app.onrender.com"

# --- ARQUIVO ALVO ---
MAIN_ACTIVITY_PATH = "app/src/main/java/com/motoristapro/android/MainActivity.kt"

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {command}")
        sys.exit(1)

def main():
    print(f"🚀 Ajustando URL de Produção Android... [{TIMESTAMP}]")
    
    file_path = Path(MAIN_ACTIVITY_PATH)
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return

    # 1. Ler conteúdo atual
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Substituir a URL (garantindo que aponta para a home ou monitoramento)
    # Procura pela linha do webView.loadUrl e substitui
    import re
    new_line = f'        webView.loadUrl("{PRODUCTION_URL}")'
    content_fixed = re.sub(r'webView\.loadUrl\(".*?"\)', new_line, content)

    # 3. Salvar
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_fixed)
    
    print(f"✅ URL atualizada para: {PRODUCTION_URL}")

    # 4. Git
    print("\n☁️ Sincronizando...")
    try:
        run_command("git add .")
        subprocess.run(f'git commit -m "{COMMIT_MSG}"', shell=True)
        run_command("git push")
        print("✅ Sucesso!")
    except: pass

    # 5. Limpeza
    try: os.remove(__file__)
    except: pass

if __name__ == "__main__":
    main()

