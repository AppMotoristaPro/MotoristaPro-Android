import os

def create_file(path, content):
    """Cria um arquivo com o conteúdo especificado, garantindo que os diretórios existam."""
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Criado: {path}")

# --- CONTEÚDO DOS ARQUIVOS ---

# 1. .gitignore
gitignore_content = """
*.iml
.gradle
/local.properties
/.idea/
.DS_Store
/build
/captures
.externalNativeBuild
.cxx
local.properties
"""

# 2. settings.gradle.kts
settings_gradle_content = """
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "MotoristaPro-Android"
include(":app")
"""

# 3. build.gradle.kts (Raiz)
root_build_gradle_content = """
// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}
"""

# 4. app/build.gradle.kts (Módulo App)
app_build_gradle_content = """
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.motoristapro.android"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.motoristapro.android"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
}
"""

# 5. AndroidManifest.xml
manifest_content = """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@android:drawable/ic_menu_compass"
        android:label="Motorista Pro"
        android:roundIcon="@android:drawable/ic_menu_compass"
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

# 6. Regras de Backup (XMLs auxiliares para evitar erros de build)
backup_rules_content = """
<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <include domain="sharedpref" path="."/>
    <include domain="database" path="."/>
</full-backup-content>
"""

data_extraction_rules_content = """
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <include domain="sharedpref" path="."/>
        <include domain="database" path="."/>
    </cloud-backup>
    <device-transfer>
        <include domain="sharedpref" path="."/>
        <include domain="database" path="."/>
    </device-transfer>
</data-extraction-rules>
"""

# 7. MainActivity.kt
main_activity_content = """
package com.motoristapro.android

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import android.view.Gravity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Criando a UI via código para simplificar esta fase inicial
        val textView = TextView(this)
        textView.text = "Motorista Pro Android\\nFase 1: Setup Completo!\\n\\nAguardando Webview e OCR..."
        textView.textSize = 24f
        textView.gravity = Gravity.CENTER
        
        setContentView(textView)
    }
}
"""

# 8. GitHub Actions Workflow
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

    # Como não temos o gradle wrapper gerado no script python, usamos o gradle do ambiente
    # mas forçamos a geração do wrapper para garantir consistência ou rodamos direto
    - name: Build with Gradle
      run: gradle assembleDebug --no-daemon --stacktrace

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: app-debug
        path: app/build/outputs/apk/debug/app-debug.apk
"""

# --- EXECUÇÃO ---

print("--- Iniciando Setup Fase 1: MotoristaPro-Android ---")

# Criar arquivos raiz
create_file(".gitignore", gitignore_content)
create_file("settings.gradle.kts", settings_gradle_content)
create_file("build.gradle.kts", root_build_gradle_content)

# Criar arquivos do app
create_file("app/build.gradle.kts", app_build_gradle_content)
create_file("app/src/main/AndroidManifest.xml", manifest_content)
create_file("app/src/main/res/xml/backup_rules.xml", backup_rules_content)
create_file("app/src/main/res/xml/data_extraction_rules.xml", data_extraction_rules_content)

# Criar código fonte
create_file("app/src/main/java/com/motoristapro/android/MainActivity.kt", main_activity_content)

# Criar workflow do GitHub Actions
create_file(".github/workflows/android.yml", workflow_content)

print("\n--- Setup Finalizado ---")
print("Agora execute:")
print("1. git add .")
print("2. git commit -m 'Setup Fase 1'")
print("3. git push")
print("Depois verifique a aba 'Actions' no seu repositório GitHub.")


