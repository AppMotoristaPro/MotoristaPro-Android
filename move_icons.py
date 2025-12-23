import os
import shutil

# --- CONFIGURAÇÕES ---
# Caminho da pasta Download no Android (acessível via Termux)
source_dir = "/sdcard/Download"

# Arquivos que vamos procurar
files = ["ic_launcher.png", "ic_launcher_round.png"]

# Pastas de destino no projeto Android
dest_folders = [
    "app/src/main/res/mipmap-mdpi",
    "app/src/main/res/mipmap-hdpi",
    "app/src/main/res/mipmap-xhdpi",
    "app/src/main/res/mipmap-xxhdpi",
    "app/src/main/res/mipmap-xxxhdpi"
]

def move_icons():
    print("📦 Iniciando transferência de ícones...")

    # Verifica se os arquivos existem na pasta Download
    for filename in files:
        source_path = os.path.join(source_dir, filename)
        
        if not os.path.exists(source_path):
            print(f"❌ ERRO: O arquivo '{filename}' não foi encontrado em {source_dir}")
            print("   Certifique-se de ter renomeado os arquivos na pasta Download para:")
            print("   - ic_launcher.png")
            print("   - ic_launcher_round.png")
            return

    # Copia para todas as pastas
    count = 0
    for folder in dest_folders:
        # Cria a pasta se não existir (segurança)
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        for filename in files:
            src = os.path.join(source_dir, filename)
            dst = os.path.join(folder, filename)
            
            try:
                shutil.copy2(src, dst)
                print(f"✅ Copiado {filename} -> {folder}")
                count += 1
            except Exception as e:
                print(f"❌ Erro ao copiar para {folder}: {e}")

    print(f"\n🎉 Concluído! {count} arquivos copiados/substituídos.")
    print("Agora execute o script 'update_full.py' para atualizar o código do balão.")

if __name__ == "__main__":
    move_icons()


