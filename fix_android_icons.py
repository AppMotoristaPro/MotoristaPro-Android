import os
import shutil

# --- CONFIGURAÇÃO ---
# Tenta encontrar a pasta do projeto automaticamente
def find_project_root():
    # Procura por build.gradle.kts ou settings.gradle.kts
    for root, dirs, files in os.walk("."):
        if "settings.gradle.kts" in files:
            return root
    return None

project_root = find_project_root()
if not project_root:
    print("❌ Não encontrei a pasta do projeto Android.")
    print("   Execute este script dentro da pasta 'MotoristaPro-Android'.")
    exit(1)

print(f"📁 Raiz do projeto: {project_root}")

# Caminho da pasta problemática (anydpi)
anydpi_path = os.path.join(project_root, "app/src/main/res/mipmap-anydpi-v26")

# 1. REMOVER A PASTA ANYDPI (Para forçar o uso dos PNGs)
if os.path.exists(anydpi_path):
    print(f"🗑️ Removendo pasta conflitante: {anydpi_path}")
    try:
        shutil.rmtree(anydpi_path)
        print("✅ Pasta removida. O Android agora usará seus PNGs.")
    except Exception as e:
        print(f"❌ Erro ao remover pasta: {e}")
else:
    print("ℹ️ Pasta anydpi não encontrada (ou já removida).")

# 2. RE-COPIAR ÍCONES (Garantia)
download_dir = "/sdcard/Download"
res_path = os.path.join(project_root, "app/src/main/res")
folders = ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]
files = ["ic_launcher.png", "ic_launcher_round.png"]

print("\n📦 Verificando ícones na pasta Download...")
for f in files:
    src = os.path.join(download_dir, f)
    if os.path.exists(src):
        for folder in folders:
            dst_dir = os.path.join(res_path, folder)
            if not os.path.exists(dst_dir): os.makedirs(dst_dir)
            shutil.copy2(src, os.path.join(dst_dir, f))
        print(f"✅ {f} copiado para todas as pastas mipmap.")
    else:
        print(f"⚠️ {f} não encontrado em {download_dir}. Verifique se o nome está correto.")

print("\n🚀 Ícones corrigidos! Agora compile o APK novamente.")


