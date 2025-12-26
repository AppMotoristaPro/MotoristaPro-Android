import os

def main():
    print("🔄 Restaurando script de versionamento...")
    
    code = r"""import re
import os
import time

gradle_path = "app/build.gradle.kts"

def increment_version():
    if not os.path.exists(gradle_path):
        print(f"❌ {gradle_path} não encontrado.")
        return

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Timestamp para garantir versão sempre maior
    ts = int(time.time())
    
    # Atualiza versionCode
    new_content = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {ts}', content)
    
    # Atualiza versionName
    new_content = re.sub(r'versionName\s*=\s*".*?"', f'versionName = "2.0.{ts}"', new_content)

    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Versão definida para Timestamp: {ts}")

if __name__ == "__main__":
    increment_version()
"""
    with open("auto_version.py", "w", encoding='utf-8') as f:
        f.write(code)
    
    print("✅ auto_version.py criado com sucesso.")
    
    # Roda uma vez para garantir
    os.system("python3 auto_version.py")

if __name__ == "__main__":
    main()


