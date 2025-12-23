import os

# Configurações
OUTPUT_FILE = "PROJETO_ANDROID_COMPLETO.txt"
PROJECT_DIR = "."  # Diretório atual

# Pastas e arquivos para IGNORAR (para não poluir o txt com binários ou lixo)
IGNORE_DIRS = {
    '.git', '.gradle', '.idea', 'build', 'captures', 
    'gradle', '.github' # Opcional: ignorar config do github se quiser
}
IGNORE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.webp', '.ico', '.jar', '.zip', '.apk', '.class', '.dex'
}
IGNORE_FILES = {
    'local.properties', '.DS_Store', 'gradlew', 'gradlew.bat', OUTPUT_FILE, 
    'preparar_envio_android.py' # Ignora o próprio script
}

def is_ignored(path):
    """Verifica se o caminho deve ser ignorado."""
    parts = path.split(os.sep)
    for p in parts:
        if p in IGNORE_DIRS:
            return True
    return False

def collect_files():
    """Percorre o projeto e coleta o conteúdo dos arquivos."""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write(f"Projeto Android Exportado: {os.path.abspath(PROJECT_DIR)}\n")
        outfile.write("==================================================\n\n")

        for root, dirs, files in os.walk(PROJECT_DIR):
            # Filtra diretórios ignorados para não entrar neles
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_DIR)
                
                # Checagens de ignorar
                if file in IGNORE_FILES:
                    continue
                if any(file.endswith(ext) for ext in IGNORE_EXTENSIONS):
                    continue
                if is_ignored(rel_path):
                    continue

                # Escreve no arquivo final
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        content = infile.read()
                        
                        outfile.write(f"\n==================== INICIO ARQUIVO: {rel_path} ====================\n")
                        outfile.write(content)
                        outfile.write(f"\n==================== FIM ARQUIVO: {rel_path} ====================\n")
                        print(f"Adicionado: {rel_path}")
                except Exception as e:
                    print(f"Erro ao ler {rel_path}: {e}")

    print(f"\n--- Concluído! ---")
    print(f"Todo o código foi salvo em: {OUTPUT_FILE}")

if __name__ == "__main__":
    collect_files()


