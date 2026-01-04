import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÃO ---
BACKUP_ROOT = Path("backup_automatico")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
COMMIT_MSG = "Fix: Restaurar startRobot e adicionar Permissao Notificacao"

# --- URL DO SITE ---
TARGET_URL = "https://motorista-pro-app.onrender.com"

# --- ARQUIVO ALVO ---
MAIN_ACTIVITY_PATH = "app/src/main/java/com/motoristapro/android/MainActivity.kt"

# --- NOVO CÓDIGO (Completo e Corrigido) ---
NEW_MAIN_ACTIVITY = f"""
package com.motoristapro.android

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.accessibility.AccessibilityManager
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : ComponentActivity() {{

    private lateinit var webView: WebView
    private val NOTIFICATION_PERMISSION_CODE = 101

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        setupWebView()
        
        // 1. Carrega o Site
        webView.loadUrl("{TARGET_URL}")

        // 2. Pede Permissão de Notificação (Android 13+)
        askNotificationPermission()
    }}

    private fun setupWebView() {{
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        
        // Ponte JavaScript -> Android
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()
    }}

    private fun askNotificationPermission() {{
        // Apenas necessário para Android 13 (API 33) ou superior
        if (Build.VERSION.SDK_INT >= 33) {{
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {{
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), NOTIFICATION_PERMISSION_CODE)
            }}
        }}
    }}

    // --- PONTE JAVASCRIPT ---
    inner class WebAppInterface(private val context: Context) {{

        // CORREÇÃO: Restauramos o nome 'startRobot' que o site chama
        @JavascriptInterface
        fun startRobot() {{
            runOnUiThread {{
                checkAndRequestPermissions()
            }}
        }}

        // Mantemos este também por compatibilidade
        @JavascriptInterface
        fun requestPermission() {{
            runOnUiThread {{
                checkAndRequestPermissions()
            }}
        }}

        @JavascriptInterface
        fun subscribeToPush(userId: String) {{
            // Aqui você pode adicionar a lógica do Firebase Messaging se necessário
            // FirebaseMessaging.getInstance().subscribeToTopic("user_$userId")
        }}
    }}

    // --- LÓGICA DE PERMISSÕES E FLOW ---
    
    private fun checkAndRequestPermissions() {{
        // 1. Verificar Sobreposição (Overlay) - Para desenhar a bolha flutuante
        if (!Settings.canDrawOverlays(this)) {{
            showExplanationDialog(
                title = "Permissão de Sobreposição",
                message = "Para mostrar o lucro flutuante em cima do Uber e 99, o app precisa de permissão para 'Sobrepor outros apps'.",
                positiveAction = {{
                    val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
                    startActivity(intent)
                }}
            )
            return
        }}

        // 2. Verificar Acessibilidade (Leitura de Tela) - Para ler o preço
        if (!isAccessibilityServiceEnabled()) {{
            showExplanationDialog(
                title = "Ativar Leitura Automática",
                message = "Para ler o preço e a distância da corrida automaticamente, você precisa ativar o 'Motorista Pro Leitor' nas configurações de Acessibilidade.",
                positiveAction = {{
                    val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                    startActivity(intent)
                }}
            )
            return
        }}

        // 3. Tudo OK -> Iniciar Robô
        startOcrService()
    }}

    private fun startOcrService() {{
        try {{
            val intent = Intent(this, OcrService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
                startForegroundService(intent)
            }} else {{
                startService(intent)
            }}
            
            // Feedback visual
            Toast.makeText(this, "🤖 Robô Iniciado! Abra o Uber/99.", Toast.LENGTH_LONG).show()
            
        }} catch (e: Exception) {{
            Toast.makeText(this, "Erro ao iniciar: ${{e.message}}", Toast.LENGTH_SHORT).show()
        }}
    }}

    // --- UTILITÁRIOS ---

    private fun showExplanationDialog(title: String, message: String, positiveAction: () -> Unit) {{
        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("Configurar") {{ _, _ -> positiveAction() }}
            .setNegativeButton("Cancelar", null)
            .setCancelable(false)
            .show()
    }}

    private fun isAccessibilityServiceEnabled(): Boolean {{
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val enabledServices = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_GENERIC)
        for (service in enabledServices) {{
            if (service.resolveInfo.serviceInfo.packageName == packageName &&
                service.resolveInfo.serviceInfo.name.endsWith("WindowMonitorService")) {{
                return true
            }}
        }}
        return false
    }}
    
    override fun onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack()
        }} else {{
            super.onBackPressed()
        }}
    }}
}}
"""

FILES_TO_UPDATE = {
    MAIN_ACTIVITY_PATH: NEW_MAIN_ACTIVITY,
}

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {{command}}")
        sys.exit(1)

def main():
    print(f"🚀 Iniciando correção Android... [{{TIMESTAMP}}]")
    
    # 1. Backup
    current_backup_dir = BACKUP_ROOT / TIMESTAMP
    if not current_backup_dir.exists():
        current_backup_dir.mkdir(parents=True, exist_ok=True)

    for file_path_str, new_content in FILES_TO_UPDATE.items():
        file_path = Path(file_path_str)
        
        if file_path.exists():
            dest_backup = current_backup_dir / file_path
            dest_backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_backup)
            print(f"📦 Backup salvo: {{dest_backup}}")
        
        # 2. Escrita
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content.strip())
        print(f"✅ Arquivo atualizado: {{file_path}}")

    # 3. Git Push Automático
    print("\\n☁️ Sincronizando com Git...")
    try:
        run_command("git add .")
        subprocess.run(f'git commit -m "{{COMMIT_MSG}}"', shell=True)
        run_command("git push")
        print("✅ Git Push realizado com sucesso!")
    except Exception as e:
        print(f"⚠️ Atenção: {{e}}")

    # 4. Auto-destruição
    try:
        os.remove(__file__)
        print("✅ Script excluído.")
    except: pass

if __name__ == "__main__":
    main()

