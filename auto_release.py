import os
import shutil
import time
import re
import subprocess
import sys

# --- CONFIGURAÇÕES ---
# Caminho dos Downloads no Android via Termux
SOURCE_DIR = "/storage/emulated/0/Download"
# Caminho dos recursos do projeto
RES_DIR = "app/src/main/res"
# Arquivo de build
GRADLE_FILE = "app/build.gradle.kts"

# Nomes dos arquivos esperados
ICON_SQUARE = "ic_launcher.png"
ICON_ROUND = "ic_launcher_round.png"

# Pastas de destino obrigatórias
DENSITIES = ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]

def log(msg):
    print(f"\n[🤖] {msg}")

def check_source_files():
    log("Verificando arquivos na pasta Download...")
    p1 = os.path.join(SOURCE_DIR, ICON_SQUARE)
    p2 = os.path.join(SOURCE_DIR, ICON_ROUND)
    
    if not os.path.exists(p1) or not os.path.exists(p2):
        print(f"❌ ERRO: Não encontrei os ícones na pasta Downloads.")
        print(f"Certifique-se de que '{ICON_SQUARE}' e '{ICON_ROUND}' estão em: {SOURCE_DIR}")
        print("Dica: Rode 'termux-setup-storage' se ainda não deu permissão.")
        sys.exit(1)
    return p1, p2

def distribute_icons(src_square, src_round):
    log("Distribuindo ícones PNG e removendo conflitos...")
    
    # 1. Remover pasta conflituosa (XML)
    anydpi_path = os.path.join(RES_DIR, "mipmap-anydpi-v26")
    if os.path.exists(anydpi_path):
        shutil.rmtree(anydpi_path)
        print(f"✅ Pasta conflituosa removida: {anydpi_path}")
    
    # 2. Copiar para todas as densidades
    for density in DENSITIES:
        dest_dir = os.path.join(RES_DIR, density)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        shutil.copy2(src_square, os.path.join(dest_dir, ICON_SQUARE))
        shutil.copy2(src_round, os.path.join(dest_dir, ICON_ROUND))
        print(f"   -> Copiado para {density}")

def update_app_version():
    log("Atualizando versão do App...")
    
    if not os.path.exists(GRADLE_FILE):
        print(f"❌ Arquivo {GRADLE_FILE} não encontrado.")
        sys.exit(1)

    # Gera um código baseado em timestamp (sempre crescente)
    new_version_code = int(time.time())
    new_version_name = f"2.0.{new_version_code}"
    
    with open(GRADLE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex para substituir versionCode
    content_new = re.sub(
        r'versionCode\s*=\s*\d+', 
        f'versionCode = {new_version_code}', 
        content
    )
    
    # Regex para substituir versionName
    content_new = re.sub(
        r'versionName\s*=\s*".*"', 
        f'versionName = "{new_version_name}"', 
        content_new
    )

    with open(GRADLE_FILE, 'w', encoding='utf-8') as f:
        f.write(content_new)
        
    print(f"✅ Versão atualizada para: {new_version_code}")
    return new_version_name

def git_automate(version_name):
    log("Executando Git automático...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        msg = f"Fix: Icons Update & Bump Version {version_name}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("\n🚀 PUSH REALIZADO COM SUCESSO!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")

def main():
    # 1. Checa se os arquivos existem no celular
    s1, s2 = check_source_files()
    
    # 2. Distribui nas pastas do projeto e deleta a pasta XML
    distribute_icons(s1, s2)
    
    # 3. Muda a versão do Gradle
    v_name = update_app_version()
    
    # 4. Sobe pro GitHub
    git_automate(v_name)

if __name__ == "__main__":
    main()


