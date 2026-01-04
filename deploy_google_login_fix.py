import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÃO ---
BACKUP_ROOT = Path("backup_automatico")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
COMMIT_MSG = "Fix: Google Login 403 (UserAgent spoofing) + Dialog Support"

# --- URL DO SITE ---
TARGET_URL = "https://motorista-pro-app.onrender.com"

# --- ARQUIVO ALVO ---
MAIN_ACTIVITY_PATH = "app/src/main/java/com/motoristapro/android/MainActivity.kt"

# --- NOVO CÓDIGO (Com suporte a Dialog e User Agent falso) ---
NEW_MAIN_ACTIVITY = f"""
package com.motoristapro.android

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.AlertDialog
import android.app.Dialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Message
import android.provider.Settings
import android.view.ViewGroup
import android.view.WindowManager
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
        setupWebView(webView)
        
        // 1. Carrega o Site
        webView.loadUrl("{TARGET_URL}")

        // 2. Pede Permissão de Notificação (Android 13+)
        askNotificationPermission()
    }}

    private fun setupWebView(view: WebView) {{
        val settings = view.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        
        // --- TRUQUE PARA O GOOGLE LOGIN (Simular Chrome) ---
        // Removemos o identificador "wv" que denuncia ser um WebView
        val defaultUA = settings.userAgentString
        settings.userAgentString = defaultUA.replace("; wv", "") + " (MotoristaPro)"
        
        // Permitir multiplas janelas (necessário para o popup do Google)
        settings.setSupportMultipleWindows(true)
        settings.javaScriptCanOpenWindowsAutomatically = true
        
        // Ponte JavaScript -> Android (Apenas na WebView principal)
        if (view == webView) {{
            view.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")
        }}

        view.webViewClient = WebViewClient()
        
        // Configura o WebChromeClient para interceptar popups (O "Dialog")
        view.webChromeClient = object : WebChromeClient() {{
            override fun onCreateWindow(view: WebView?, isDialog: Boolean, isUserGesture: Boolean, resultMsg: Message?): Boolean {{
                // Cria um novo WebView para o Popup do Google
                val newWebView = WebView(this@MainActivity)
                setupWebView(newWebView) // Aplica as mesmas configurações (User Agent, etc)
                
                // Cria um Dialog Nativo em tela cheia para exibir esse WebView
                val dialog = Dialog(this@MainActivity, android.R.style.Theme_Black_NoTitleBar_Fullscreen)
                dialog.setContentView(newWebView)
                dialog.window?.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.MATCH_PARENT)
                dialog.show()

                // Quando o popup fechar (ex: fim do login), fecha o dialog
                newWebView.webChromeClient = object : WebChromeClient() {{
                    override fun onCloseWindow(window: WebView?) {{
                        dialog.dismiss()
                    }}
                }}
                
                // Redireciona o transporte da janela para o novo WebView
                val transport = resultMsg?.obj as WebView.WebViewTransport
                transport.webView = newWebView
                resultMsg.sendToTarget()
                
                return true
            }}
        }}
    }}

    private fun askNotificationPermission() {{
        if (Build.VERSION.SDK_INT >= 33) {{
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {{
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), NOTIFICATION_PERMISSION_CODE)
            }}
        }}
    }}

    // --- PONTE JAVASCRIPT ---
    inner class WebAppInterface(private val context: Context) {{

        @JavascriptInterface
        fun startRobot() {{
            runOnUiThread {{ checkAndRequestPermissions() }}
        }}

        @JavascriptInterface
        fun requestPermission() {{
            runOnUiThread {{ checkAndRequestPermissions() }}
        }}

        @JavascriptInterface
        fun subscribeToPush(userId: String) {{
            // Placeholder para lógica de push
        }}
    }}

    // --- LÓGICA DE PERMISSÕES ---
    private fun checkAndRequestPermissions() {{
        if (!Settings.canDrawOverlays(this)) {{
            showExplanationDialog(
                "Permissão de Sobreposição",
                "Para mostrar o lucro flutuante, o app precisa 'Sobrepor outros apps'.",
                {{ startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))) }}
            )
            return
        }}

        if (!isAccessibilityServiceEnabled()) {{
            showExplanationDialog(
                "Ativar Leitura",
                "Para ler o preço da corrida, ative o 'Motorista Pro Leitor' em Acessibilidade.",
                {{ startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }}
            )
            return
        }}

        startOcrService()
    }}

    private fun startOcrService() {{
        try {{
            val intent = Intent(this, OcrService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
            Toast.makeText(this, "🤖 Robô Iniciado!", Toast.LENGTH_LONG).show()
        }} catch (e: Exception) {{
            Toast.makeText(this, "Erro: ${{e.message}}", Toast.LENGTH_SHORT).show()
        }}
    }}

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
                service.resolveInfo.serviceInfo.name.endsWith("WindowMonitorService")) return true
        }}
        return false
    }}
    
    override fun onBackPressed() {{
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
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
    print(f"🚀 Atualizando Android (Google Login Fix + Dialog)... [{{TIMESTAMP}}]")
    
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
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content.strip())
        print(f"✅ Arquivo atualizado: {{file_path}}")

    print("\\n☁️ Sincronizando com Git...")
    try:
        run_command("git add .")
        subprocess.run(f'git commit -m "{{COMMIT_MSG}}"', shell=True)
        run_command("git push")
        print("✅ Git Push realizado com sucesso!")
    except Exception as e:
        print(f"⚠️ Atenção: {{e}}")

    try:
        os.remove(__file__)
        print("✅ Script excluído.")
    except: pass

if __name__ == "__main__":
    main()

