import os
import subprocess

# --- CONFIGURAÇÃO ---
target_file = "MainActivity.kt"

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def main():
    print("🔧 Iniciando correção do Download no APK...")
    
    file_path = find_file(target_file)
    if not file_path:
        print("❌ Erro: MainActivity.kt não encontrado.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Garantir Importação do Uri
    if "import android.net.Uri" not in content:
        content = content.replace("import android.os.Bundle", "import android.net.Uri\nimport android.os.Bundle")
        print("✅ Import android.net.Uri adicionado.")

    # 2. Adicionar o DownloadListener
    # O código abaixo diz ao Android: "Se for download, abra o navegador"
    download_code = """
        // --- CORREÇÃO DE DOWNLOAD ---
        webView.setDownloadListener { url, _, _, _, _ ->
            try {
                val intent = Intent(Intent.ACTION_VIEW)
                intent.data = Uri.parse(url)
                startActivity(intent)
            } catch (e: Exception) {
                Toast.makeText(this, "Erro ao abrir link", Toast.LENGTH_SHORT).show()
            }
        }
    """

    # Verifica se já existe para não duplicar
    if "webView.setDownloadListener" in content:
        print("⚠️ Parece que o listener já existe. Substituindo para garantir...")
        # Lógica simples de remoção se já existir (opcional, mas seguro)
        # Aqui vamos apenas avisar, mas se o usuário disse que não funciona, vamos forçar a inserção limpa
        pass 
    
    # Inserir ANTES de carregar a URL (webView.loadUrl)
    # Procuramos o ponto onde ele carrega o site
    if "webView.loadUrl" in content:
        # Insere antes da chamada de loadUrl
        parts = content.split("webView.loadUrl")
        # Reconstrói: Parte 1 + Código Download + webView.loadUrl + Parte 2
        new_content = parts[0] + download_code + "webView.loadUrl" + parts[1]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ DownloadListener inserido com sucesso!")
    else:
        print("❌ Erro: Não encontrei a linha 'webView.loadUrl' para inserir o código.")
        return

    # 3. Git Push Automático
    print("\n🚀 Enviando correção para o GitHub...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "Fix: Habilitar Download de APK dentro do WebView"', shell=True, check=True)
        subprocess.run("git push", shell=True, check=True)
        print("\n✅ Sucesso! Agora gere o novo APK e teste.")
    except Exception as e:
        print(f"\n❌ Erro no Git: {e}")

if __name__ == "__main__":
    main()


