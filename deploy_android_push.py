import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÃO ---
BACKUP_ROOT = Path("backup_automatico")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
COMMIT_MSG = "Feat: Push Notifications na Barra de Status (FCM)"

# --- URL DO SITE (Mantendo a correta) ---
TARGET_URL = "https://motorista-pro-app.onrender.com"

# --- CAMINHOS DOS ARQUIVOS ---
BASE_PACKAGE = "app/src/main/java/com/motoristapro/android"
MAIN_ACTIVITY_PATH = f"{BASE_PACKAGE}/MainActivity.kt"
FCM_SERVICE_PATH = f"{BASE_PACKAGE}/MyFirebaseMessagingService.kt"

# -----------------------------------------------------------------------------
# 1. NOVO CONTEÚDO: MainActivity.kt
# (Adiciona a lógica real de inscrição no Firebase Messaging)
# -----------------------------------------------------------------------------
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
import com.google.firebase.messaging.FirebaseMessaging

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

        // 2. Pede Permissão de Notificação
        askNotificationPermission()
    }}

    private fun setupWebView(view: WebView) {{
        val settings = view.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        
        // User Agent para Google Login
        val defaultUA = settings.userAgentString
        settings.userAgentString = defaultUA.replace("; wv", "") + " (MotoristaPro)"
        
        settings.setSupportMultipleWindows(true)
        settings.javaScriptCanOpenWindowsAutomatically = true
        
        if (view == webView) {{
            view.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")
        }}

        view.webViewClient = WebViewClient()
        
        // Gerenciamento de Popups (Google Login)
        view.webChromeClient = object : WebChromeClient() {{
            override fun onCreateWindow(view: WebView?, isDialog: Boolean, isUserGesture: Boolean, resultMsg: Message?): Boolean {{
                val newWebView = WebView(this@MainActivity)
                setupWebView(newWebView)
                val dialog = Dialog(this@MainActivity, android.R.style.Theme_Black_NoTitleBar_Fullscreen)
                dialog.setContentView(newWebView)
                dialog.show()
                newWebView.webChromeClient = object : WebChromeClient() {{
                    override fun onCloseWindow(window: WebView?) {{ dialog.dismiss() }}
                }}
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

    inner class WebAppInterface(private val context: Context) {{
        @JavascriptInterface
        fun startRobot() {{ runOnUiThread {{ checkAndRequestPermissions() }} }}

        @JavascriptInterface
        fun requestPermission() {{ runOnUiThread {{ checkAndRequestPermissions() }} }}

        @JavascriptInterface
        fun subscribeToPush(userId: String) {{
            // LÓGICA DE INSCRIÇÃO REAL NO FIREBASE
            FirebaseMessaging.getInstance().subscribeToTopic("all_users")
            if (userId.isNotEmpty()) {{
                val topic = "user_$userId"
                FirebaseMessaging.getInstance().subscribeToTopic(topic)
                    .addOnCompleteListener {{ task ->
                        if (task.isSuccessful) {{
                            // Opcional: Log de sucesso
                        }}
                    }}
            }}
        }}
    }}

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

# -----------------------------------------------------------------------------
# 2. NOVO CONTEÚDO: MyFirebaseMessagingService.kt
# (Garante que a notificação apareça na barra mesmo com o app aberto)
# -----------------------------------------------------------------------------
NEW_FCM_SERVICE = """
package com.motoristapro.android

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // Verifica se a mensagem tem payload de notificação
        remoteMessage.notification?.let {
            sendNotification(it.title ?: "Nova Mensagem", it.body ?: "")
        }
    }

    private fun sendNotification(title: String, messageBody: String) {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_IMMUTABLE
        )

        val channelId = "motorista_pro_channel"
        val notificationBuilder = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.mipmap.ic_launcher) // Ícone padrão do app
            .setContentTitle(title)
            .setContentText(messageBody)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_HIGH)

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Cria o canal de notificação (Necessário para Android 8.0+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Avisos Motorista Pro",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        notificationManager.notify(System.currentTimeMillis().toInt(), notificationBuilder.build())
    }
}
"""

FILES_TO_UPDATE = {
    MAIN_ACTIVITY_PATH: NEW_MAIN_ACTIVITY,
    FCM_SERVICE_PATH: NEW_FCM_SERVICE
}

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        sys.exit(1)

def main():
    print(f"🚀 Configurando Push Notifications (Android)... [{TIMESTAMP}]")
    
    current_backup_dir = BACKUP_ROOT / TIMESTAMP
    if not current_backup_dir.exists():
        current_backup_dir.mkdir(parents=True, exist_ok=True)

    for file_path_str, new_content in FILES_TO_UPDATE.items():
        file_path = Path(file_path_str)
        
        if file_path.exists():
            dest_backup = current_backup_dir / file_path
            dest_backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_backup)
            print(f"📦 Backup salvo: {dest_backup}")
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content.strip())
        print(f"✅ Arquivo criado/atualizado: {file_path}")

    print("\n☁️ Sincronizando com Git...")
    try:
        run_command("git add .")
        subprocess.run(f'git commit -m "{COMMIT_MSG}"', shell=True)
        run_command("git push")
        print("✅ Git Push realizado com sucesso!")
    except Exception as e:
        print(f"⚠️ Atenção: {e}")

    try:
        os.remove(__file__)
        print("✅ Script excluído.")
    except: pass

if __name__ == "__main__":
    main()

