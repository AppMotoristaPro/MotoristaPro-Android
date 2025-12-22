import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- 1. WORKFLOW BLINDADO (Curl + Retries) ---
workflow_content = """
name: Android Build

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'

    # CORREÇÃO DE REDE:
    # Usamos curl com 'retry' para tentar 5 vezes se o servidor falhar.
    # Usamos o link direto para a versão 8.2 (mais leve e compatível).
    - name: Install Gradle 8.2 (Robust)
      run: |
        curl -L --retry 5 --retry-delay 10 -o /tmp/gradle.zip https://services.gradle.org/distributions/gradle-8.2-bin.zip
        sudo unzip -q -d /opt/gradle /tmp/gradle.zip
        echo "GRADLE_HOME=/opt/gradle/gradle-8.2" >> $GITHUB_ENV
        echo "/opt/gradle/gradle-8.2/bin" >> $GITHUB_PATH

    - name: Build with Gradle
      run: gradle assembleDebug --no-daemon --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: app-debug
        path: app/build/outputs/apk/debug/app-debug.apk
"""

# --- 2. GARANTIA DO ANDROIDX (Caso tenha se perdido) ---
gradle_properties_content = """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
"""

print("--- Aplicando Fix de Rede e Dependências ---")
create_file(".github/workflows/android.yml", workflow_content)
create_file("gradle.properties", gradle_properties_content)

print("\nArquivos corrigidos.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Fix: Download Robusto e AndroidX'")
print("3. git push")


