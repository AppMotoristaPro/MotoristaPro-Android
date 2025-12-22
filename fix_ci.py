import os

# Conteúdo corrigido do workflow (.github/workflows/android.yml)
# Adicionamos o passo "Setup Gradle" que força a versão 8.4
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

    # CORREÇÃO: Forçar o uso do Gradle 8.4 (compatível com AGP 8.2.0)
    # Isso evita o erro com o Gradle 9.x padrão do servidor
    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v3
      with:
        gradle-version: '8.4'

    - name: Build with Gradle
      run: gradle assembleDebug --no-daemon --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: app-debug
        path: app/build/outputs/apk/debug/app-debug.apk
"""

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

print("--- Aplicando Correção do Gradle Version ---")
create_file(".github/workflows/android.yml", workflow_content)
print("Correção aplicada com sucesso.")


