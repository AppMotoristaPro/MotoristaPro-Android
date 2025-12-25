import re
import os
import time

gradle_path = "app/build.gradle.kts"

def increment_version():
    if not os.path.exists(gradle_path):
        print(f"❌ {gradle_path} não encontrado.")
        return

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Timestamp atual (segundos desde 1970)
    # Ex: 1703480000. Isso garante unicidade.
    ts = int(time.time())
    
    # Atualiza versionCode
    new_content = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {ts}', content)
    
    # Atualiza versionName (Data legível ou simples)
    new_content = re.sub(r'versionName\s*=\s*".*?"', f'versionName = "2.0.{ts}"', new_content)

    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Versão definida para Timestamp: {ts}")

if __name__ == "__main__":
    increment_version()
