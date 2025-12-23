import os
import shutil

# --- CONFIGURAÇÃO ---
POSSIBLE_ICONS = [
    "icon.png", 
    "logo.png", 
    "favicon.png", 
    "android-chrome-192x192.png", 
    "android-chrome-512x512.png",
    "apple-touch-icon.png"
]

# Caminho corrigido: agora aponta para 'app/static/icons'
SITE_ICONS_PATH = "../motoristaproteste/app/static/icons"
ANDROID_DEST_PATH = "app/src/main/res/drawable/ic_launcher_foreground.png"
ANDROID_XML_TO_DELETE = "app/src/main/res/drawable/ic_launcher_foreground.xml"

print(f"--- Procurando ícone em: {SITE_ICONS_PATH} ---")

found_icon = None

# 1. Tenta encontrar o arquivo
if os.path.exists(SITE_ICONS_PATH):
    files = os.listdir(SITE_ICONS_PATH)
    
    # Procura na lista de prioridade
    for icon_name in POSSIBLE_ICONS:
        full_path = os.path.join(SITE_ICONS_PATH, icon_name)
        if os.path.exists(full_path):
            found_icon = full_path
            print(f"SUCESSO: Encontrado '{icon_name}'!")
            break
            
    # Se não achou, tenta qualquer PNG
    if not found_icon:
        print("Aviso: Nomes padrão não encontrados. Procurando qualquer PNG...")
        for f in files:
            if f.endswith(".png"):
                found_icon = os.path.join(SITE_ICONS_PATH, f)
                print(f"Encontrado arquivo provável: {f}")
                break
else:
    print(f"ERRO: A pasta {SITE_ICONS_PATH} não existe.")
    print("Verifique se o caminho da pasta icons está correto.")
    exit(1)

# 2. Copia e Configura
if found_icon:
    os.makedirs(os.path.dirname(ANDROID_DEST_PATH), exist_ok=True)
    
    # Remove XML conflitante
    if os.path.exists(ANDROID_XML_TO_DELETE):
        os.remove(ANDROID_XML_TO_DELETE)
        print("XML antigo removido.")
        
    shutil.copy2(found_icon, ANDROID_DEST_PATH)
    print(f"Ícone copiado com sucesso!")
    
    # Garante fundo azul
    bg_xml = """<?xml version="1.0" encoding="utf-8"?>
<drawable xmlns:android="http://schemas.android.com/apk/res/android">
    <color android:color="#2563EB"/>
</drawable>"""
    
    with open("app/src/main/res/drawable/ic_launcher_background.xml", "w") as f:
        f.write(bg_xml)
    
    print("\n--- TUDO PRONTO! ---")
    print("Execute:")
    print("1. git add .")
    print("2. git commit -m 'UI: Sync Icon from Static/Icons'")
    print("3. git push")

else:
    print("\nERRO: Nenhum arquivo .png encontrado dentro de app/static/icons.")


