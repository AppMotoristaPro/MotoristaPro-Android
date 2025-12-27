import os
import shutil
import time
import re
import subprocess
import sys

# --- CONFIGURAÇÕES ---
SOURCE_DIR = "/storage/emulated/0/Download"
RES_DIR = "app/src/main/res"
OCR_SERVICE_PATH = "app/src/main/java/com/motoristapro/android/OcrService.kt"
GRADLE_FILE = "app/build.gradle.kts"

# Nomes dos arquivos esperados
ICON_SQUARE = "ic_launcher.png"
ICON_ROUND = "ic_launcher_round.png"

# Pastas de destino
DENSITIES = ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]

def log(msg):
    print(f"\n[🤖] {msg}")

def check_source_files():
    log("1. Verificando arquivos na pasta Download...")
    p1 = os.path.join(SOURCE_DIR, ICON_SQUARE)
    p2 = os.path.join(SOURCE_DIR, ICON_ROUND)
    
    if not os.path.exists(p1) or not os.path.exists(p2):
        print(f"❌ ERRO: Arquivos não encontrados em {SOURCE_DIR}")
        print(f"Certifique-se de ter '{ICON_SQUARE}' e '{ICON_ROUND}' baixados.")
        sys.exit(1)
    return p1, p2

def distribute_icons(src_square, src_round):
    log("2. Distribuindo ícones e limpando conflitos...")
    
    # Remove pasta XML que causa conflito com PNGs
    anydpi_path = os.path.join(RES_DIR, "mipmap-anydpi-v26")
    if os.path.exists(anydpi_path):
        shutil.rmtree(anydpi_path)
        print(f"   ✅ Pasta 'mipmap-anydpi-v26' removida (Conflito resolvido).")
    
    # Copia PNGs para todas as densidades
    for density in DENSITIES:
        dest_dir = os.path.join(RES_DIR, density)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        shutil.copy2(src_square, os.path.join(dest_dir, ICON_SQUARE))
        shutil.copy2(src_round, os.path.join(dest_dir, ICON_ROUND))
    print(f"   ✅ Ícones copiados para {len(DENSITIES)} pastas.")

def fix_code_reference():
    log("3. Corrigindo erro de compilação no código Kotlin...")
    
    if not os.path.exists(OCR_SERVICE_PATH):
        print(f"❌ Erro: Arquivo {OCR_SERVICE_PATH} não encontrado.")
        return

    with open(OCR_SERVICE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # O erro é: Unresolved reference: ic_launcher_foreground
    # Vamos trocar por: ic_launcher (que existe no mipmap)
    
    old_ref = "R.drawable.ic_launcher_foreground"
    new_ref = "R.mipmap.ic_launcher"
    
    # Também tenta corrigir se estiver apontando para mipmap foreground inexistente
    old_ref_2 = "R.mipmap.ic_launcher_foreground"

    fixed_content = content
    if old_ref in content:
        fixed_content = fixed_content.replace(old_ref, new_ref)
        print("   ✅ Substituído R.drawable.ic_launcher_foreground -> R.mipmap.ic_launcher")
    
    if old_ref_2 in content:
        fixed_content = fixed_content.replace(old_ref_2, new_ref)
        print("   ✅ Substituído R.mipmap.ic_launcher_foreground -> R.mipmap.ic_launcher")

    if fixed_content != content:
        with open(OCR_SERVICE_PATH, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
    else:
        print("   ℹ️ Nenhuma substituição necessária ou padrão não encontrado.")

def update_app_version():
    log("4. Atualizando versão do App...")
    
    if not os.path.exists(GRADLE_FILE):
        print(f"❌ Arquivo {GRADLE_FILE} não encontrado.")
        sys.exit(1)

    new_version_code = int(time.time())
    new_version_name = f"2.0.{new_version_code}"
    
    with open(GRADLE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    content_new = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {new_version_code}', content)
    content_new = re.sub(r'versionName\s*=\s*".*"', f'versionName = "{new_version_name}"', content_new)

    with open(GRADLE_FILE, 'w', encoding='utf-8') as f:
        f.write(content_new)
        
    print(f"   ✅ Versão: {new_version_name}")
    return new_version_name

def git_push_auto(version_name):
    log("5. Enviando para o GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        msg = f"Fix: Replace missing icon reference & Bump v{version_name}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("\n🚀 SUCESSO! Código corrigido e enviado.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")

def main():
    s1, s2 = check_source_files()
    distribute_icons(s1, s2)
    fix_code_reference() # <--- A correção crítica está aqui
    v_name = update_app_version()
    git_push_auto(v_name)

if __name__ == "__main__":
    main()


