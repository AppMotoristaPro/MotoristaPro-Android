import os

def main():
    print("🚑 Corrigindo imports no MainActivity...")
    
    path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"
    
    if not os.path.exists(path):
        print("❌ Erro: MainActivity.kt não encontrado.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # O import que falta
    missing_import = "import android.media.projection.MediaProjectionManager"
    
    if missing_import not in content:
        # Adiciona junto aos outros imports
        if "import android.os.Bundle" in content:
            content = content.replace("import android.os.Bundle", f"import android.os.Bundle\n{missing_import}")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Import adicionado: MediaProjectionManager")
        else:
            print("⚠️ Estrutura do arquivo estranha, não consegui adicionar o import automaticamente.")
    else:
        print("ℹ️ O import já existe.")

    # Git Push
    print("🚀 Enviando correção...")
    os.system('git add .')
    os.system('git commit -m "Fix: Add Missing MediaProjectionManager Import"')
    os.system('git push')

if __name__ == "__main__":
    main()


