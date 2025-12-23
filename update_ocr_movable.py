import os
import shutil

# Configuração
SEARCH_DIR = "../motoristaproteste" # Pasta do site
TARGET_FILE = "icon-512.png"
ANDROID_DEST = "app/src/main/res/drawable/ic_launcher_foreground.png"

print(f"--- Procurando por {TARGET_FILE} em {SEARCH_DIR}... ---")

found_path = None

# Busca recursiva (profunda)
for root, dirs, files in os.walk(SEARCH_DIR):
    if TARGET_FILE in files:
        found_path = os.path.join(root, TARGET_FILE)
        break

if found_path:
    print(f"SUCESSO: Ícone encontrado em: {found_path}")
    
    # Garante diretório de destino
    os.makedirs(os.path.dirname(ANDROID_DEST), exist_ok=True)
    
    # Remove conflito XML se existir
    xml_conflict = "app/src/main/res/drawable/ic_launcher_foreground.xml"
    if os.path.exists(xml_conflict):
        os.remove(xml_conflict)
        print("XML conflitante removido.")

    # Copia
    shutil.copy2(found_path, ANDROID_DEST)
    print("Ícone aplicado ao APK com sucesso!")
    
    # Garante fundo azul
    bg_xml = """<?xml version="1.0" encoding="utf-8"?>
<drawable xmlns:android="http://schemas.android.com/apk/res/android">
    <color android:color="#2563EB"/>
</drawable>"""
    with open("app/src/main/res/drawable/ic_launcher_background.xml", "w") as f:
        f.write(bg_xml)

    print("\nExecute: git add . && git commit -m 'Icon: Fixed 512px' && git push")
else:
    print(f"ERRO: O arquivo {TARGET_FILE} não foi encontrado em nenhuma pasta do site.")


