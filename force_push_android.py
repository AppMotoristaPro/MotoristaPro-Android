import os
import subprocess

def main():
    print("🚀 Forçando envio do ANDROID para o GitHub...")
    print("⚠️  Isso vai sobrescrever o repositório remoto 'main'.")

    try:
        # 1. Adiciona tudo
        print("📦 Adicionando arquivos...")
        subprocess.run("git add .", shell=True, check=True)

        # 2. Commit
        print("📝 Commitando alterações...")
        try:
            subprocess.run('git commit -m "Force Update Android via Termux"', shell=True, check=False)
        except:
            pass 

        # 3. PUSH FORÇADO (-f) para a branch main
        print(f"☁️ Enviando para o GitHub (Force Push)...")
        # O erro mostrou que a branch é 'main'
        cmd = "git push -f origin main"
        
        subprocess.run(cmd, shell=True, check=True)
        
        print("\n✅ SUCESSO! O GitHub Android foi atualizado.")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao enviar: {e}")
        print("Verifique sua senha/token.")

if __name__ == "__main__":
    main()


