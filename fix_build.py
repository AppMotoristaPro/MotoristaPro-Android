import os
import subprocess

# Nome do arquivo alvo
target_file_name = "OcrService.kt"

def find_file():
    """Encontra o arquivo OcrService.kt automaticamente"""
    print(f"🔍 Procurando '{target_file_name}'...")
    for root, dirs, files in os.walk("."):
        if target_file_name in files:
            return os.path.join(root, target_file_name)
    return None

def fix_code(file_path):
    print("\n🛠️ Aplicando correção de sintaxe Kotlin...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Mapeamento de Correções (Linha Errada -> Linha Certa)
    # Adicionamos escapes duplos (\\) onde havia apenas um (\)
    corrections = [
        (
            r'val pm = Pattern.compile("(?:r\$|rs|\$)\s*([0-9]+(?:[.,][0-9]{0,2})?)").matcher(cleanText)',
            r'val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)").matcher(cleanText)'
        ),
        (
            r'val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\s*(km|m)(?!in)").matcher(cleanText)',
            r'val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)").matcher(cleanText)'
        ),
        (
            r'val tm = Pattern.compile("([0-9]+)\s*h\s*(?:([0-9]+)\s*min)?").matcher(cleanText)',
            r'val tm = Pattern.compile("([0-9]+)\\s*h\\s*(?:([0-9]+)\\s*min)?").matcher(cleanText)'
        ),
        (
            r'val mm = Pattern.compile("([0-9]+)\s*min").matcher(cleanText)',
            r'val mm = Pattern.compile("([0-9]+)\\s*min").matcher(cleanText)'
        )
    ]

    fixed_content = content
    count = 0
    
    for bad, good in corrections:
        if bad in fixed_content:
            fixed_content = fixed_content.replace(bad, good)
            count += 1

    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ {count} erros de sintaxe corrigidos com sucesso!")
        return True
    else:
        print("⚠️ Nenhuma linha problemática encontrada. O arquivo pode já estar corrigido ou diferente do esperado.")
        # Verificação extra: se já tem escape duplo, está ok
        if '\\\\s' in content:
            print("   (Parece que o código já possui os escapes corretos '\\\\s')")
        return False

def git_push():
    print("\n🚀 Enviando correção para o GitHub...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "Fix: Erro de compilação (Illegal escape in Regex)"', shell=True, check=True)
        subprocess.run("git push", shell=True, check=True)
        print("\n✅ Correção enviada!")
    except Exception as e:
        print(f"\n❌ Erro no Git: {e}")

if __name__ == "__main__":
    file_path = find_file()
    if file_path:
        print(f"📁 Arquivo encontrado: {file_path}")
        if fix_code(file_path):
            git_push()
        else:
            choice = input("Deseja forçar o git push mesmo assim? (s/n): ")
            if choice.lower() == 's':
                git_push()
    else:
        print("❌ Arquivo OcrService.kt não encontrado. Verifique se está na pasta do projeto.")


