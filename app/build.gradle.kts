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
        versionCode = 1766770769
        versionName = "2.0.1766770769"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    
    signingConfigs {
        create("release") {
            storeFile = file("motorista.jks")
            storePassword = "motorista123"
            keyAlias = "key0"
            keyPassword = "motorista123"
            enableV1Signing = true
            enableV2Signing = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("release")
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
    implementation("androidx.core:core-ktx:1.9.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.10.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // ML Kit (OCR) - Único essencial
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
}
