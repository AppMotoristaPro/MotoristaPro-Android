import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- 1. MANIFESTO (Com permissão de Internet) ---
manifest_content = """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- FASE 2: Permissão de Internet Adicionada -->
    <uses-permission android:name="android.permission.INTERNET" />

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

# --- 2. MAIN ACTIVITY (WebView Completa) ---
# Usamos criação programática da UI (sem XML de layout) para evitar erros de recursos (R.java)
# neste ambiente de build simplificado.
main_activity_content = """
package com.motoristapro.android

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Inicializa a WebView
        webView = WebView(this)
        setContentView(webView)

        // Configurações da WebView para Aplicações Modernas (React/SPA)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true // Necessário para persistência de dados (localStorage)
            databaseEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            
            // Ajustes de viewport para mobile
            useWideViewPort = true
            loadWithOverviewMode = true
        }

        // Garante que links abram dentro do app, não no Chrome externo
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                view?.loadUrl(url ?: return false)
                return true
            }
        }

        // URL Alvo
        webView.loadUrl("https://motorista-pro-app.onrender.com")
    }

    // Comportamento do botão Voltar (Back)
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
"""

print("--- Iniciando Setup Fase 2: WebView ---")

# Atualizar Manifesto
create_file("app/src/main/AndroidManifest.xml", manifest_content)

# Atualizar MainActivity
create_file("app/src/main/java/com/motoristapro/android/MainActivity.kt", main_activity_content)

print("\n--- Fase 2 Aplicada ---")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Fase 2: Implementando WebView'")
print("3. git push")


