import os
import re

# Caminho do arquivo build.gradle.kts
gradle_path = "app/build.gradle.kts"

def fix_signing_config():
    if not os.path.exists(gradle_path):
        print(f"❌ {gradle_path} não encontrado.")
        return

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verifica se já tem as configurações de V1 e V2
    if "enableV1Signing" in content and "enableV2Signing" in content:
        print("✅ Configuração de assinatura V1/V2 já está presente.")
        return

    # Procura o bloco signingConfigs release e adiciona as flags
    # Vamos inserir logo após a senha da chave
    search_pattern = r'(keyPassword\s*=\s*"motorista123")'
    replacement = r'\1\n            enableV1Signing = true\n            enableV2Signing = true'
    
    new_content = re.sub(search_pattern, replacement, content)

    if new_content != content:
        with open(gradle_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ build.gradle.kts atualizado: Assinatura V1 e V2 forçadas.")
    else:
        print("⚠️ Não foi possível encontrar o local exato para inserir as flags. Verifique o arquivo manualmente.")

if __name__ == "__main__":
    fix_signing_config()


