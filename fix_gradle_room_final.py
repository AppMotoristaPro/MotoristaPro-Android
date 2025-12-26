import os

def main():
    print("🚑 Blindando build.gradle.kts para corrigir erros do Room/KAPT...")
    
    gradle_path = "app/build.gradle.kts"
    
    # Configuração Robusta
    # - Usa Room 2.6.1 (Compatível com Kotlin 1.8/1.9)
    # - Adiciona kapt { correctErrorTypes = true }
    # - Define Java 17
    
    new_gradle = """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")
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
        
        // Corrige erro de schema do Room
        javaCompileOptions {
            annotationProcessorOptions {
                arguments += mapOf("room.schemaLocation" to "$projectDir/schemas")
            }
        }
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

// Configuração essencial para corrigir erros de "Unresolved reference" no KAPT
kapt {
    correctErrorTypes = true
}

dependencies {
    // Android Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.cardview:cardview:1.0.0")
    
    // ML Kit (OCR do Robô)
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    
    // Coroutines (Processamento em segundo plano)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Lifecycle (ViewModel, LiveData)
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.6.2")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.lifecycle:lifecycle-service:2.6.2")
    
    // ROOM DATABASE (Versão 2.6.1 - A mais compatível com SDK 34)
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1") // Importante para Coroutines (suspend)
    kapt("androidx.room:room-compiler:2.6.1")
}
"""

    if os.path.exists(gradle_path):
        with open(gradle_path, 'w', encoding='utf-8') as f:
            f.write(new_gradle)
        print("✅ build.gradle.kts reescrito com sucesso.")
    else:
        print("❌ Erro: Arquivo build.gradle.kts não encontrado.")

    # Limpeza de Cache do Gradle (Força re-download)
    print("\n🧹 Limpando cache de build...")
    os.system("./gradlew clean")
    
    # Incrementa versão
    os.system("python3 auto_version.py")
    
    # Enviar correção
    print("\n🚀 Enviando para GitHub...")
    os.system("git add .")
    os.system('git commit -m "Fix: Upgrade Room to 2.6.1 and Enable Kapt Error Correction"')
    os.system("git push")
    
    print("\n👉 Agora tente compilar: ./gradlew assembleDebug")

if __name__ == "__main__":
    main()


