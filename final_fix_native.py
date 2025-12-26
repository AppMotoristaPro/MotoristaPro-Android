import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Reconstruído: {path}")

def main():
    print("🚑 Aplicando Correção Definitiva (Gradle + Main + Database)...")

    # ==============================================================================
    # 1. BUILD.GRADLE.KTS (Blindado)
    # ==============================================================================
    gradle_content = """plugins {
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

// Força o Kapt a ser tolerante a erros de tipo
kapt {
    correctErrorTypes = true
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.cardview:cardview:1.0.0")
    
    // ML Kit
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.1")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1")
    
    // Room (Versão 2.6.1)
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
}
"""
    write_file("app/build.gradle.kts", gradle_content)

    # ==============================================================================
    # 2. MAIN ACTIVITY (Com Imports Corretos)
    # ==============================================================================
    main_activity = """package com.motoristapro.android

import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import androidx.lifecycle.lifecycleScope
import com.motoristapro.android.data.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.NumberFormat
import java.util.Locale

class MainActivity : AppCompatActivity() {

    private lateinit var tvTotalGanho: TextView
    private lateinit var tvTotalCorridas: TextView
    private lateinit var tvTotalKm: TextView
    private lateinit var tvEmptyHistory: TextView
    
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvTotalGanho = findViewById(R.id.tvTotalGanho)
        tvTotalCorridas = findViewById(R.id.tvTotalCorridas)
        tvTotalKm = findViewById(R.id.tvTotalKm)
        tvEmptyHistory = findViewById(R.id.tvEmptyHistory)

        findViewById<CardView>(R.id.btnLancar)?.setOnClickListener {
            startActivity(Intent(this, AddDailyActivity::class.java))
        }

        findViewById<CardView>(R.id.btnRobo)?.setOnClickListener {
            checkPermissionsAndStart()
        }

        refreshDashboard()
    }

    override fun onResume() {
        super.onResume()
        refreshDashboard()
    }

    private fun refreshDashboard() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val db = AppDatabase.getDatabase(applicationContext)
                // Usando lista direta em vez de Flow para simplificar e evitar erros de compilação
                val lista = db.diarioDao().getAllList() 
                
                var totalGanho = 0.0
                var totalKm = 0.0
                var totalCorridas = 0
                
                for (item in lista) {
                    totalGanho += item.ganhoBruto
                    totalKm += item.kmPercorrido
                    totalCorridas += item.qtdCorridas
                }

                withContext(Dispatchers.Main) {
                    val ptBr = Locale("pt", "BR")
                    tvTotalGanho.text = NumberFormat.getCurrencyInstance(ptBr).format(totalGanho)
                    tvTotalKm.text = String.format("%.0f km", totalKm)
                    tvTotalCorridas.text = totalCorridas.toString()
                    
                    if (lista.isNotEmpty()) {
                        tvEmptyHistory.text = "Último: R$ ${lista[0].ganhoBruto}"
                    }
                }
            } catch (e: Exception) { e.printStackTrace() }
        }
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
        val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(mpManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION) {
            if (resultCode == RESULT_OK && data != null) {
                val serviceIntent = Intent(this, OcrService::class.java).apply {
                    putExtra("RESULT_CODE", resultCode)
                    putExtra("RESULT_DATA", data)
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    startForegroundService(serviceIntent)
                } else {
                    startService(serviceIntent)
                }
                moveTaskToBack(true)
            }
        }
    }
}
"""
    write_file("app/src/main/java/com/motoristapro/android/MainActivity.kt", main_activity)

    # ==============================================================================
    # 3. DIARIO DAO (Simplificado para evitar erro de Cursor)
    # ==============================================================================
    # Removemos o Flow por enquanto e usamos List direta suspensa
    diario_dao = """package com.motoristapro.android.data.dao

import androidx.room.*
import com.motoristapro.android.data.entities.DiarioEntity

@Dao
interface DiarioDao {
    @Query("SELECT * FROM diarios WHERE isDeleted = 0 ORDER BY data DESC")
    suspend fun getAllList(): List<DiarioEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(diario: DiarioEntity): Long
}
"""
    write_file("app/src/main/java/com/motoristapro/android/data/dao/DiarioDao.kt", diario_dao)

    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("\n🚀 Enviando Correção Definitiva...")
    os.system("git add .")
    os.system('git commit -m "Fix: Resolve imports and simplify Room DAO"')
    os.system("git push")

if __name__ == "__main__":
    main()


