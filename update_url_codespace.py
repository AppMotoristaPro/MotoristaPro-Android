import os
import re

# --- CONFIGURAÇÃO ---
NEW_URL = "https://special-orbit-97rqq6999x66c956v-5000.app.github.dev"

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def update_file(filename, processor):
    path = find_file(filename)
    if not path:
        print(f"❌ {filename} não encontrado.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = processor(content)
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ URL atualizada em {filename}")
    else:
        print(f"ℹ️ Nenhuma alteração necessária em {filename}")

def main():
    print(f"🚀 Atualizando App para: {NEW_URL}")

    # 1. MainActivity.kt (WebView)
    def proc_main(c):
        # Substitui qualquer URL dentro de webView.loadUrl
        return re.sub(r'webView\.loadUrl\("https?://[^"]*"\)', f'webView.loadUrl("{NEW_URL}")', c)
    update_file("MainActivity.kt", proc_main)

    # 2. LoginActivity.kt (API)
    def proc_login(c):
        # Substitui a base da API_URL mantendo o /api/mobile_login
        return re.sub(r'private val API_URL = "https?://[^"]*/api/mobile_login"', f'private val API_URL = "{NEW_URL}/api/mobile_login"', c)
    update_file("LoginActivity.kt", proc_login)

    # 3. RobotActivity.kt (Links externos)
    def proc_robot(c):
        # Substitui link de /assinar
        c = re.sub(r'Uri\.parse\("https?://[^"]*/assinar"\)', f'Uri.parse("{NEW_URL}/assinar")', c)
        # Substitui link da home (qualquer outro link http que não termine em assinar)
        # Regex cuidadoso para não pegar /assinar de novo se rodar varias vezes, mas o de cima ja trata
        # Vamos substituir qualquer Uri.parse("http...") que NÃO seja o /assinar, assumindo ser a home
        # Mas para simplificar, vamos substituir chamadas específicas conhecidas dos scripts anteriores
        
        # Substitui chamadas genéricas para a raiz
        c = c.replace('Uri.parse("https://motoristapro.onrender.com")', f'Uri.parse("{NEW_URL}")')
        
        # Tenta pegar URLs antigas de codespace se houver
        c = re.sub(r'Uri\.parse\("https://.*\.app\.github\.dev"\)', f'Uri.parse("{NEW_URL}")', c)
        
        return c
    update_file("RobotActivity.kt", proc_robot)

    # 4. Incrementar Versão
    print("\n🔄 Incrementando versão do App...")
    os.system("python3 auto_version.py")
    
    print("\n✅ PRONTO! URL Atualizada.")
    print("👉 Agora rode: ./gradlew assembleDebug")

if __name__ == "__main__":
    main()


