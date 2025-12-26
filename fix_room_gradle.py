import os

def main():
    print("🚑 Reparando build.gradle.kts para baixar o Room corretamente...")
    
    gradle_path = "app/build.gradle.kts"
    
    # Conteúdo Blindado do Gradle
    # Usamos versões explícitas e compatibilidade Java 17 (Padrão novo)
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
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    
    // Atualizado para Java 17 (Recomendado para Gradle 8+)
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
    // Android Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.cardview:cardview:1.0.0")
    
    // ML Kit (OCR)
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-service:2.6.1")
    
    // ROOM DATABASE (Definição Explícita)
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    
    // Lifecycle Components
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.6.1")
}
"""

    if os.path.exists(gradle_path):
        with open(gradle_path, 'w', encoding='utf-8') as f:
            f.write(new_gradle)
        print("✅ build.gradle.kts reescrito com sucesso.")
    else:
        print("❌ Erro: Arquivo build.gradle.kts não encontrado.")

    # Incrementar versão para garantir novo build limpo
    print("\n🔄 Incrementando versão...")
    os.system("python3 auto_version.py")
    
    # Enviar para GitHub
    print("\n🚀 Enviando correção...")
    os.system("git add .")
    os.system('git commit -m "Fix: Build Gradle Room Dependencies & Java 17"')
    os.system("git push")

if __name__ == "__main__":
    main()


