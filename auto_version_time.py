import re
import os
import time

gradle_path = "app/build.gradle.kts"

def update_version():
    if not os.path.exists(gradle_path):
        print(f"❌ {gradle_path} não encontrado.")
        return

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Gera um código único baseado no tempo (Ex: 1735150000)
    # Isso garante que sempre aumenta
    timestamp_code = int(time.time())
    
    # Atualiza versionCode
    new_content = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {timestamp_code}', content)
    
    # Atualiza versionName para algo legível (Ex: 2.0.TIMESTAMP)
    new_content = re.sub(r'versionName\s*=\s*".*?"', f'versionName = "2.0.{timestamp_code}"', new_content)

    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Versão atualizada para: {timestamp_code}")

if __name__ == "__main__":
    update_version()


