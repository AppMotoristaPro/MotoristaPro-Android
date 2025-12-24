import re
import os

# Caminho do arquivo gradle
gradle_path = "app/build.gradle.kts"

def increment_version():
    if not os.path.exists(gradle_path):
        print(f"❌ Arquivo não encontrado: {gradle_path}")
        return False

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex para encontrar versionCode
    # Procura por: versionCode = 1 ou versionCode=1
    vc_pattern = r'versionCode\s*=\s*(\d+)'
    match_vc = re.search(vc_pattern, content)
    
    if match_vc:
        current_vc = int(match_vc.group(1))
        new_vc = current_vc + 1
        content = re.sub(vc_pattern, f'versionCode = {new_vc}', content)
        print(f"🆙 VersionCode: {current_vc} -> {new_vc}")
    else:
        print("⚠️ Não encontrei versionCode no arquivo.")

    # Regex para encontrar versionName
    # Procura por: versionName = "1.0"
    vn_pattern = r'versionName\s*=\s*"(\d+\.\d+)"'
    match_vn = re.search(vn_pattern, content)
    
    if match_vn:
        current_vn = match_vn.group(1)
        # Tenta incrementar o último número (ex: 1.0 -> 1.1)
        parts = current_vn.split('.')
        if len(parts) >= 2:
            try:
                last_num = int(parts[-1])
                parts[-1] = str(last_num + 1)
                new_vn = ".".join(parts)
                content = re.sub(vn_pattern, f'versionName = "{new_vn}"', content)
                print(f"🆙 VersionName: {current_vn} -> {new_vn}")
            except:
                pass
    
    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(content)
        return True

if __name__ == "__main__":
    print("🔄 Incrementando versão do Android...")
    if increment_version():
        print("✅ Versão atualizada! Pode compilar o APK.")
    else:
        print("❌ Falha ao atualizar versão.")


