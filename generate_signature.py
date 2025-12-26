import os
import subprocess

def main():
    print("🔐 Iniciando Geração de Assinatura Digital (Keystore)...")

    # --- CONFIGURAÇÕES DA CHAVE ---
    KEY_NAME = "motorista.jks"
    KEY_ALIAS = "key0"
    KEY_PASS = "motorista123" # Senha padrão para facilitar sua gestão
    KEY_DNAME = "CN=Motorista Pro, OU=App, O=MotoristaPro, L=Brasil, S=SP, C=BR"
    
    APP_DIR = "app"
    KEY_PATH = os.path.join(APP_DIR, KEY_NAME)

    # 1. GERAR ARQUIVO .JKS (JAVA KEYSTORE)
    # Usamos o keytool que vem com o Java
    print(f"🔨 Criando chave: {KEY_PATH}...")
    
    # Remove se já existir para não dar erro
    if os.path.exists(KEY_PATH):
        os.remove(KEY_PATH)

    cmd = [
        "keytool", "-genkey", "-v",
        "-keystore", KEY_PATH,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-alias", KEY_ALIAS,
        "-storepass", KEY_PASS,
        "-keypass", KEY_PASS,
        "-dname", KEY_DNAME
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Arquivo de chave criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar chave: {e}")
        print("   Verifique se o Java (JDK) está instalado no Termux (pkg install openjdk-17).")
        return

    # 2. CONFIGURAR BUILD.GRADLE PARA USAR A CHAVE
    print("📝 Configurando Gradle para assinar o APK...")
    
    gradle_path = "app/build.gradle.kts"
    if not os.path.exists(gradle_path):
        print("❌ build.gradle.kts não encontrado.")
        return

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Bloco de configuração de assinatura
    signing_config = f"""
    signingConfigs {{
        create("release") {{
            storeFile = file("{KEY_NAME}")
            storePassword = "{KEY_PASS}"
            keyAlias = "{KEY_ALIAS}"
            keyPassword = "{KEY_PASS}"
        }}
    }}
"""

    # Verifica se já tem signingConfigs e remove/substitui ou adiciona
    if "signingConfigs {" not in content:
        # Insere antes de buildTypes
        content = content.replace("buildTypes {", signing_config + "\n    buildTypes {")

    # Configura o buildType 'release' para usar essa assinatura
    if 'signingConfig = signingConfigs.getByName("release")' not in content:
        # Procura o bloco release e adiciona a linha de assinatura
        # Substitui a configuração de release padrão
        content = content.replace(
            'proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")',
            'proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")\n            signingConfig = signingConfigs.getByName("release")'
        )

    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Gradle configurado para Release!")
    print("\n🚀 PROCESSO CONCLUÍDO.")
    print("👉 Para gerar o APK FINAL (Assinado), use este comando:")
    print("   ./gradlew assembleRelease")
    print("\n   (O arquivo ficará em: app/build/outputs/apk/release/app-release.apk)")

if __name__ == "__main__":
    main()


