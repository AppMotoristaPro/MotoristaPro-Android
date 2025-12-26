import os
import shutil

# --- CONFIGURAÇÃO ---
SITE_URL = "https://motorista-pro-app.onrender.com"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Restaurado: {path}")

def delete_path(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        print(f"🗑️ Deletado: {path}")

def main():
    print("☢️ INICIANDO RESET TOTAL PARA WEBVIEW SIMPLES...")

    base_src = "app/src/main/java/com/motoristapro/android"
    base_res = "app/src/main/res/layout"

    # ==============================================================================
    # 1. LIMPEZA DE ARQUIVOS NATIVOS (Fases 1, 2, 3, 4)
    # ==============================================================================
    files_to_delete = [
        f"{base_src}/AddDailyActivity.kt",
        f"{base_src}/HistoryActivity.kt",
        f"{base_src}/HistoryAdapter.kt",
        f"{base_src}/HomeActivity.kt",
        f"{base_src}/LoginActivity.kt",
        f"{base_src}/RobotActivity.kt",
        f"{base_src}/data", # Pasta inteira do banco de dados
        f"{base_res}/activity_add_daily.xml",
        f"{base_res}/activity_history.xml",
        f"{base_res}/activity_home.xml",
        f"{base_res}/activity_login.xml",
        f"{base_res}/activity_robot.xml",
        f"{base_res}/item_dynamic_row.xml",
        f"{base_res}/item_history.xml"
    ]

    for f in files_to_delete:
        delete_path(f)

    # ==============================================================================
    # 2. RESTAURAR GRADLE (Básico)
    # ==============================================================================
    gradle_content = """plugins {
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
    implementation("androidx.core:core-ktx:1.9.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.10.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // Mantemos ML Kit para o OCR (O único nativo que sobra)
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
}
"""
    write_file("app/build.gradle.kts", gradle_content)

    # ==============================================================================
    # 3. RESTAURAR MANIFESTO
    # ==============================================================================
    manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="Motorista Pro"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar"
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service 
            android:name=".OcrService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="mediaProjection" />

    </application>
</manifest>
"""
    write_file("app/src/main/AndroidManifest.xml", manifest_content)

    # ==============================================================================
    # 4. RESTAURAR LAYOUT (activity_main.xml com WebView)
    # ==============================================================================
    main_layout = """<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</RelativeLayout>
"""
    write_file(f"{base_res}/activity_main.xml", main_layout)

    # ==============================================================================
    # 5. RESTAURAR KOTLIN (MainActivity.kt Simples)
    # ==============================================================================
    main_kt = f"""package com.motoristapro.android

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.webkit.CookieManager
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.media.projection.MediaProjectionManager
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {{

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    // Ponte para o Site chamar o Robô
    inner class WebAppInterface(private val mContext: Context) {{
        @JavascriptInterface
        fun startRobot() {{
            checkPermissionsAndStart()
        }}
    }}

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        
        // Configurações Web
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        // UserAgent para evitar bloqueio do Google
        webView.settings.userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 MotoristaProApp"

        // Cookies
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }}

        // Interface JS
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        // Cliente Web (Para não abrir no Chrome)
        webView.webViewClient = object : WebViewClient() {{
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {{
                if (url != null && (url.startsWith("whatsapp:") || url.startsWith("geo:") || url.startsWith("tel:"))) {{
                    try {{ startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }} catch(e:Exception){{}}
                    return true
                }}
                return false
            }}
        }}

        // Carrega o Site
        webView.loadUrl("{SITE_URL}")
    }}

    private fun checkPermissionsAndStart() {{
        if (!Settings.canDrawOverlays(this)) {{
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }}
        val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(mpManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
    }}

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {{
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION) {{
            if (resultCode == RESULT_OK && data != null) {{
                val serviceIntent = Intent(this, OcrService::class.java).apply {{
                    putExtra("RESULT_CODE", resultCode)
                    putExtra("RESULT_DATA", data)
                }}
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
                    startForegroundService(serviceIntent)
                }} else {{
                    startService(serviceIntent)
                }}
                moveTaskToBack(true)
            }}
        }}
    }}

    override fun onBackPressed() {{
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }}
}}
"""
    write_file(f"{base_src}/MainActivity.kt", main_kt)
    
    # Incrementa versão para garantir update
    os.system("python3 auto_version.py")

    print("\n✅ RESET CONCLUÍDO.")
    print("O app agora é um navegador simples que abre: " + SITE_URL)
    print("Compile agora: ./gradlew assembleDebug")

if __name__ == "__main__":
    main()


