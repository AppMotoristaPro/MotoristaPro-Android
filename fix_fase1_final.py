import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- 1. ÍCONE GENÉRICO (Volante simples em Vector Drawable) ---
icon_xml = """
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#000000"
        android:pathData="M12,2C6.48,2 2,6.48 2,12C2,17.52 6.48,22 12,22C17.52,22 22,17.52 22,12C22,6.48 17.52,2 12,2ZM12,4C15.81,4 19.09,6.66 20.08,10.21L15.35,11.85C14.77,10.74 13.51,10 12,10C10.49,10 9.23,10.74 8.65,11.85L3.92,10.21C4.91,6.66 8.19,4 12,4ZM12,20C8.19,20 4.91,17.34 3.92,13.79L8.65,12.15C8.89,12.63 9.24,13.05 9.66,13.36L8.03,17.88C9.2,18.59 10.56,19 12,19C13.44,19 14.8,18.59 15.97,17.88L14.34,13.36C14.76,13.05 15.11,12.63 15.35,12.15L20.08,13.79C19.09,17.34 15.81,20 12,20Z"/>
</vector>
"""

# --- 2. MANIFESTO ATUALIZADO (Apontando para o novo ícone) ---
manifest_content = """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@drawable/ic_launcher_foreground"
        android:label="Motorista Pro"
        android:roundIcon="@drawable/ic_launcher_foreground"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""

# --- 3. WORKFLOW DO GITHUB (Instalação Manual do Gradle 8.5) ---
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

    # SOLUÇÃO MANUAL: Baixa e configura o Gradle 8.5 diretamente
    # Isso evita erros 503 da Action setup-gradle e incompatibilidade de versão
    - name: Install Gradle 8.5
      run: |
        wget -q https://services.gradle.org/distributions/gradle-8.5-bin.zip -P /tmp
        sudo unzip -q -d /opt/gradle /tmp/gradle-8.5-bin.zip
        echo "GRADLE_HOME=/opt/gradle/gradle-8.5" >> $GITHUB_ENV
        echo "/opt/gradle/gradle-8.5/bin" >> $GITHUB_PATH

    - name: Build with Gradle
      run: gradle assembleDebug --no-daemon --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: app-debug
        path: app/build/outputs/apk/debug/app-debug.apk
"""

print("--- Aplicando Correção Final Fase 1 ---")

# Criar ícone
create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", icon_xml)

# Atualizar manifesto
create_file("app/src/main/AndroidManifest.xml", manifest_content)

# Atualizar CI
create_file(".github/workflows/android.yml", workflow_content)

print("\nArquivos atualizados.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Fix: Gradle Manual e Icone'")
print("3. git push")


