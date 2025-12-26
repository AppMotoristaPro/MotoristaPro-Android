import os
import shutil

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo corrigido: {path}")

def main():
    print("🚑 Iniciando Resgate de Dependências (Room & Gradle)...")

    # ==========================================================================
    # 1. SETTINGS.GRADLE.KTS (Garantir Repositórios)
    # ==========================================================================
    settings_content = """pluginManagement {
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
    write_file("settings.gradle.kts", settings_content)

    # ==========================================================================
    # 2. BUILD.GRADLE.KTS (App - Versões Estáveis)
    # ==========================================================================
    # Mudança Estratégica: Vamos usar Room 2.5.0 que é ultra-estável
    # e garantir que o plugin kotlin-kapt esteja no topo.
    
    app_gradle_content = """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt") // OBRIGATÓRIO
}

android {
    namespace = "com.motoristapro.android"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.motoristapro.android"
        minSdk = 26
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
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    // Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.cardview:cardview:1.0.0")
    
    // OCR
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    
    // Coroutines & Lifecycle
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.6.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.1")
    
    // ROOM DATABASE (Versão 2.5.0 - Estável)
    val room_version = "2.5.0"
    implementation("androidx.room:room-runtime:$room_version")
    implementation("androidx.room:room-ktx:$room_version")
    kapt("androidx.room:room-compiler:$room_version")
}
"""
    write_file("app/build.gradle.kts", app_gradle_content)

    # ==========================================================================
    # 3. VERIFICAR ARQUIVOS DE DADOS
    # ==========================================================================
    # Vamos garantir que o AppDatabase.kt existe e tem os imports certos
    db_path = "app/src/main/java/com/motoristapro/android/data/AppDatabase.kt"
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            c = f.read()
        if "package com.motoristapro.android.data" not in c:
            print("⚠️ Aviso: O pacote do AppDatabase parece errado. Rode o fix_native_architecture.py novamente se persistir.")

    # 4. Incrementar Versão para forçar rebuild no Git Actions
    print("\n🔄 Incrementando versão...")
    os.system("python3 auto_version.py")

    # 5. Git Push
    print("\n🚀 Enviando correções de dependência...")
    os.system("git add .")
    os.system('git commit -m "Fix: Downgrade Room to 2.5.0 for stability & Fix Repos"')
    os.system("git push")
    
    print("\n✅ Concluído! Tente compilar agora.")

if __name__ == "__main__":
    main()


