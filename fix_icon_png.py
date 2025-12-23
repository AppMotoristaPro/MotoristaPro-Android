import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Criado/Atualizado: {path}")

def delete_if_exists(path):
    if os.path.exists(path):
        os.remove(path)
        print(f"Deletado: {path}")

print("--- Configurando Ícone PNG ---")

# 1. REMOVER O XML VETORIAL (Causa do conflito)
delete_if_exists("app/src/main/res/drawable/ic_launcher_foreground.xml")
delete_if_exists("app/src/main/res/drawable-v24/ic_launcher_foreground.xml")

# 2. GARANTIR FUNDO AZUL
background_xml = """
<?xml version="1.0" encoding="utf-8"?>
<drawable xmlns:android="http://schemas.android.com/apk/res/android">
    <color android:color="#2563EB"/> <!-- Azul Marca -->
</drawable>
"""
create_file("app/src/main/res/drawable/ic_launcher_background.xml", background_xml)

# 3. VERIFICAR SE O PNG EXISTE (Opcional: Cria placeholder se não existir para não quebrar build)
# Se você já colocou seu PNG lá, este passo não fará mal pois só cria se não existir.
png_path = "app/src/main/res/drawable/ic_launcher_foreground.png"
if not os.path.exists(png_path):
    print("AVISO: ic_launcher_foreground.png não encontrado.")
    print("O build pode falhar se você não fizer upload da sua imagem PNG para:")
    print(png_path)
    # Não crio arquivo binário aqui para não corromper.
else:
    print("OK: ic_launcher_foreground.png detectado.")

# 4. RESTAURAR XML ADAPTATIVO (aponta para o drawable genérico)
adaptive_icon_xml = """
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""
create_file("app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml", adaptive_icon_xml)
create_file("app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml", adaptive_icon_xml)

print("\nConfiguração de ícone PNG concluída.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Fix: Switch to PNG Icon'")
print("3. git push")


