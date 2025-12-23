import os
import subprocess

# --- CONFIGURAÇÕES ---
# Caminho relativo do arquivo no projeto Android
file_path = "app/src/main/java/com/motoristapro/android/OcrService.kt"

# TRECHO ANTIGO (Procura exatamente por digitos + separador + 2 digitos)
# Ex: match "10,00" mas falha em "10"
old_snippet = r'val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+[.,][0-9]{2})").matcher(cleanText)'

# NOVO TRECHO (Aceita digitos, e opcionalmente separador + 0 a 2 digitos)
# Ex: match "10", "10,5", "10,00"
new_snippet = r'val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)").matcher(cleanText)'

def run_git_commands():
    try:
        print("\n--- 📦 Git: Adicionando arquivos... ---")
        subprocess.run("git add .", shell=True, check=True)
        
        print("--- 📝 Git: Commitando... ---")
        commit_msg = "Fix: Melhoria no OCR para aceitar valores inteiros (ex: R$ 10)"
        subprocess.run(f'git commit -m "{commit_msg}"', shell=True, check=True)
        
        print("--- 🚀 Git: Enviando (Push)... ---")
        subprocess.run("git push", shell=True, check=True)
        
        print("\n✅ Processo concluído com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante os comandos Git. Verifique se você configurou o git config user.email/name ou se tem conexão.")
        exit(1)

def update_file():
    if not os.path.exists(file_path):
        print(f"❌ Erro: Arquivo não encontrado em: {file_path}")
        print("Certifique-se de estar rodando este script na pasta raiz do projeto (MotoristaPro-Android).")
        exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verificação simples para ver se já foi aplicado
    if new_snippet in content:
        print("⚠️ O código já parece estar atualizado.")
        choice = input("Deseja forçar o git push mesmo assim? (s/n): ")
        if choice.lower() == 's':
            run_git_commands()
        return

    if old_snippet not in content:
        print("❌ Erro: Não consegui encontrar a linha de código antiga para substituir.")
        print("Pode ser que o arquivo tenha sido modificado manualmente antes.")
        exit(1)

    # Realiza a substituição
    new_content = content.replace(old_snippet, new_snippet)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Arquivo {file_path} atualizado com a nova Regex de dinheiro.")
    run_git_commands()

if __name__ == "__main__":
    print("🤖 Iniciando automação MotoristaPro...")
    update_file()


