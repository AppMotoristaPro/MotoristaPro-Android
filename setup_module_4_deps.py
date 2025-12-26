import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Atualizado: {path}")

def main():
    print("📊 Módulo 4: Configurando Biblioteca de Gráficos...")

    # 1. SETTINGS.GRADLE (Adicionar JitPack)
    settings_path = "settings.gradle.kts"
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # O MPAndroidChart precisa do jitpack
        if "jitpack.io" not in content:
            new_content = content.replace("mavenCentral()", "mavenCentral()\n        maven { url = uri(\"https://jitpack.io\") }")
            write_file(settings_path, new_content)
    
    # 2. BUILD.GRADLE (Adicionar MPAndroidChart)
    gradle_path = "app/build.gradle.kts"
    if os.path.exists(gradle_path):
        with open(gradle_path, 'r') as f:
            content = f.read()
            
        if "MPAndroidChart" not in content:
            dep = '    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")'
            content = content.replace("dependencies {", "dependencies {\n" + dep)
            write_file(gradle_path, content)

    # Limpar e Incrementar
    os.system("./gradlew clean")
    os.system("python3 auto_version.py")
    
    print("🚀 Dependências configuradas! Compile agora para baixar a biblioteca.")

if __name__ == "__main__":
    main()


