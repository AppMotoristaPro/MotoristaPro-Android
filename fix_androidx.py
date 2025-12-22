import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Criado/Atualizado: {path}")

# --- CONTEÚDO DO GRADLE.PROPERTIES ---
gradle_properties_content = """
# Project-wide Gradle settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8

# AndroidX package structure to make it clearer which packages are bundled with the
# Android operating system, and which are packaged with your app's APK
# https://developer.android.com/topic/libraries/support-library/androidx-rn
android.useAndroidX=true

# Automatically convert third-party libraries to use AndroidX
android.enableJetifier=true
"""

print("--- Aplicando Correção AndroidX ---")
create_file("gradle.properties", gradle_properties_content)

print("\nArquivo gradle.properties criado.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Fix: Enable AndroidX'")
print("3. git push")


