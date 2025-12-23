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
        print(f"Deletado (Conflito): {path}")

print("--- Configurando Ícone Personalizado (PNG) ---")

# 1. REMOVER O XML VETORIAL ANTIGO (Causa do conflito "Duplicate resources")
# O Android dá erro se existirem ic_launcher_foreground.xml E ic_launcher_foreground.png na mesma pasta
delete_if_exists("app/src/main/res/drawable/ic_launcher_foreground.xml")
delete_if_exists("app/src/main/res/drawable-v24/ic_launcher_foreground.xml")

# 2. CONFIGURAR FUNDO (Mantemos o azul da marca, ou podes mudar aqui)
background_xml = """
<?xml version="1.0" encoding="utf-8"?>
<drawable xmlns:android="http://schemas.android.com/apk/res/android">
    <color android:color="#2563EB"/> <!-- Azul Marca -->
</drawable>
"""
create_file("app/src/main/res/drawable/ic_launcher_background.xml", background_xml)

# 3. VERIFICAR SE O PNG EXISTE
png_path = "app/src/main/res/drawable/ic_launcher_foreground.png"
if os.path.exists(png_path):
    print(f"SUCESSO: Encontrei o seu ícone em {png_path}")
else:
    print("AVISO CRÍTICO: Não encontrei 'ic_launcher_foreground.png' na pasta 'app/src/main/res/drawable/'")
    print("Por favor, mova o seu arquivo de imagem para lá antes de fazer o push, senão o build falhará.")

# 4. XML ADAPTATIVO (Liga o Fundo XML com a tua Imagem PNG)
adaptive_icon_xml = """
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""

# Cria para a pasta padrão de ícones adaptativos
create_file("app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml", adaptive_icon_xml)
create_file("app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml", adaptive_icon_xml)

print("\nConfiguração concluída.")
print("Passos finais:")
print("1. Certifique-se que seu PNG está em 'app/src/main/res/drawable/ic_launcher_foreground.png'")
print("2. Execute: git add .")
print("3. Execute: git commit -m 'Icon: Custom PNG'")
print("4. Execute: git push")


