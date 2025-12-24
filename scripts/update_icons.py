import os
import shutil

# --- CONFIGURAÇÃO ---
DOWNLOAD_DIR = "/sdcard/Download"
PROJECT_RES_DIR = "app/src/main/res"

ICONS = {
    "ic_launcher.png": "ic_launcher.png",
    "ic_launcher_round.png": "ic_launcher_round.png"
}

TARGET_FOLDERS = [
    "mipmap-mdpi",
    "mipmap-hdpi",
    "mipmap-xhdpi",
    "mipmap-xxhdpi",
    "mipmap-xxxhdpi"
]

def update_icons():
    print("🎨 Iniciando atualização de ícones...")

    # 1. Verifica se a pasta Download existe e tem os arquivos
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"❌ Erro: Pasta {DOWNLOAD_DIR} não encontrada.")
        print("   Execute 'termux-setup-storage' e tente novamente.")
        return

    missing_files = []
    for icon in ICONS.keys():
        if not os.path.exists(os.path.join(DOWNLOAD_DIR, icon)):
            missing_files.append(icon)
    
    if missing_files:
        print(f"❌ Erro: Arquivos não encontrados na pasta Download: {', '.join(missing_files)}")
        return

    # 2. Copia para todas as pastas mipmap
    count = 0
    for folder in TARGET_FOLDERS:
        dest_dir = os.path.join(PROJECT_RES_DIR, folder)
        
        # Cria a pasta se não existir
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        for src_name, dst_name in ICONS.items():
            src_path = os.path.join(DOWNLOAD_DIR, src_name)
            dst_path = os.path.join(dest_dir, dst_name)
            
            try:
                shutil.copy2(src_path, dst_path)
                print(f"✅ Copiado {src_name} -> {folder}")
                count += 1
            except Exception as e:
                print(f"❌ Erro ao copiar para {folder}: {e}")

    # 3. Remove a pasta conflituosa (anydpi)
    # O Android 8+ prioriza essa pasta. Se ela existir com XMLs padrão,
    # seus PNGs novos serão ignorados.
    anydpi_path = os.path.join(PROJECT_RES_DIR, "mipmap-anydpi-v26")
    if os.path.exists(anydpi_path):
        print(f"🗑️ Removendo pasta conflitante: {anydpi_path}")
        try:
            shutil.rmtree(anydpi_path)
            print("✅ Pasta removida com sucesso. Agora o Android usará seus PNGs.")
        except Exception as e:
            print(f"⚠️ Não foi possível remover a pasta anydpi: {e}")
    else:
        print("ℹ️ Pasta anydpi não encontrada (Isso é bom).")

    print(f"\n🎉 Concluído! {count} arquivos atualizados.")
    print("Agora recompile seu APK para ver os novos ícones.")

if __name__ == "__main__":
    update_icons()


