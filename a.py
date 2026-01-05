import os
import shutil
import subprocess
import sys
from datetime import datetime

# --- CONFIGURAÇÃO ---
PROJECT_NAME = "MotoristaPro-Android"
HOME_DIR = os.path.expanduser("~")
PROJECT_PATH = os.path.join(HOME_DIR, PROJECT_NAME)
BACKUP_DIR = os.path.join(PROJECT_PATH, "backup_automatico")

# Arquivos
FILES = {
    "ic_layers": "app/src/main/res/drawable/ic_permission_layers.xml",
    "ic_eye": "app/src/main/res/drawable/ic_permission_eye.xml",
    "layout_dialog": "app/src/main/res/layout/dialog_permission_edu.xml",
    "main_activity": "app/src/main/java/com/motoristapro/android/MainActivity.kt"
}

# --- 1. ÍCONE SOBREPOSIÇÃO (Camadas) ---
IC_LAYERS_CONTENT = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#2563EB" android:pathData="M11.99,18.54l-7.37,-5.73L3,14.07l9,7 9,-7 -1.63,-1.27 -7.38,5.74zM12,16l7.36,-5.73L21,9l-9,-7 -9,7 1.63,1.27L12,16z"/>
</vector>"""

# --- 2. ÍCONE ACESSIBILIDADE (Olho/Scan) ---
IC_EYE_CONTENT = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#2563EB" android:pathData="M12,4.5C7,4.5 2.73,7.61 1,12c1.73,4.39 6,7.5 11,7.5s9.27,-3.11 11,-7.5c-1.73,-4.39 -6,-7.5 -11,-7.5zM12,17c-2.76,0 -5,-2.24 -5,-5s2.24,-5 5,-5 5,2.24 5,5 -2.24,5 -5,5zM12,9c-1.66,0 -3,1.34 -3,3s1.34,3 3,3 3,-1.34 3,-3 -1.34,-3 -3,-3z"/>
</vector>"""

# --- 3. LAYOUT DO DIÁLOGO PROFISSIONAL ---
LAYOUT_DIALOG_CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:background="@drawable/bg_card_white"
    android:padding="24dp">

    <ImageView
        android:id="@+id/dialog_icon"
        android:layout_width="64dp"
        android:layout_height="64dp"
        android:layout_gravity="center"
        android:src="@drawable/ic_permission_layers"
        android:layout_marginBottom="16dp"
        android:background="@drawable/bg_circle_btn"
        android:padding="12dp"
        android:backgroundTint="#F0F9FF"/>

    <TextView
        android:id="@+id/dialog_title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Permissão Necessária"
        android:textSize="20sp"
        android:textStyle="bold"
        android:textColor="#0F172A"
        android:gravity="center"
        android:layout_marginBottom="12dp"/>

    <TextView
        android:id="@+id/dialog_message"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Explicação detalhada aqui..."
        android:textSize="14sp"
        android:textColor="#64748B"
        android:gravity="center"
        android:lineSpacingMultiplier="1.3"
        android:layout_marginBottom="24dp"/>

    <!-- Botão Principal -->
    <Button
        android:id="@+id/btn_allow"
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:text="PERMITIR AGORA"
        android:textSize="14sp"
        android:textStyle="bold"
        android:textColor="#FFFFFF"
        android:background="@drawable/bg_btn_gradient"
        android:elevation="4dp"/>

    <!-- Botão Cancelar -->
    <TextView
        android:id="@+id/btn_cancel"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Agora não"
        android:textSize="14sp"
        android:textColor="#94A3B8"
        android:gravity="center"
        android:padding="12dp"
        android:layout_marginTop="8dp"/>

</LinearLayout>
"""

# --- 4. MAIN ACTIVITY ATUALIZADA (Lógica de Diálogo Customizado) ---
MAIN_ACTIVITY_CONTENT = """package com.motoristapro.android

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.AlertDialog
import android.app.Dialog
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Message
import android.provider.Settings
import android.view.LayoutInflater
import android.view.Window
import android.view.accessibility.AccessibilityManager
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessaging

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private val NOTIFICATION_PERMISSION_CODE = 101

    private val jsReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val js = intent?.getStringExtra("js")
            if (js != null) {
                webView.evaluateJavascript(js, null)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        setupWebView(webView)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            registerReceiver(jsReceiver, IntentFilter("wwebview.js_command"), Context.RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(jsReceiver, IntentFilter("wwebview.js_command"))
        }

        handleIntent(intent)
        askNotificationPermission()
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        if (intent?.action == "OPEN_ADD_SCREEN") {
            val h = intent.getIntExtra("h_val", 0)
            val m = intent.getIntExtra("m_val", 0)
            webView.loadUrl("https://motorista-pro-app.onrender.com/adicionar?tempo_cronometro=\$h:\$m")
        } else if (webView.url == null) {
            webView.loadUrl("https://motorista-pro-app.onrender.com")
        }
    }

    private fun setupWebView(view: WebView) {
        val settings = view.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        val defaultUA = settings.userAgentString
        settings.userAgentString = defaultUA.replace("; wv", "") + " (MotoristaPro)"
        settings.javaScriptCanOpenWindowsAutomatically = true
        settings.setSupportMultipleWindows(true)

        if (view == webView) {
            view.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")
        }

        view.webViewClient = WebViewClient()
        view.webChromeClient = object : WebChromeClient() {
            override fun onCreateWindow(view: WebView?, isDialog: Boolean, isUserGesture: Boolean, resultMsg: Message?): Boolean {
                val newWebView = WebView(this@MainActivity)
                setupWebView(newWebView)
                val dialog = Dialog(this@MainActivity, android.R.style.Theme_Black_NoTitleBar_Fullscreen)
                dialog.setContentView(newWebView)
                dialog.show()
                newWebView.webChromeClient = object : WebChromeClient() {
                    override fun onCloseWindow(window: WebView?) { dialog.dismiss() }
                }
                val transport = resultMsg?.obj as WebView.WebViewTransport
                transport.webView = newWebView
                resultMsg.sendToTarget()
                return true
            }
        }
    }

    private fun askNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), NOTIFICATION_PERMISSION_CODE)
            }
        }
    }

    inner class WebAppInterface(private val context: Context) {
        @JavascriptInterface
        fun startRobot() { runOnUiThread { checkAndRequestPermissions() } }

        @JavascriptInterface
        fun requestPermission() { runOnUiThread { checkAndRequestPermissions() } }

        @JavascriptInterface
        fun subscribeToPush(userId: String) {
            FirebaseMessaging.getInstance().subscribeToTopic("all_users")
            if (userId.isNotEmpty()) FirebaseMessaging.getInstance().subscribeToTopic("user_\$userId")
        }

        @JavascriptInterface
        fun syncTimer(state: String, startTs: Long, elapsed: Long) {
            val intent = Intent(context, TimerService::class.java)
            intent.action = TimerService.ACTION_SYNC
            intent.putExtra("state", state)
            intent.putExtra("start_ts", startTs)
            intent.putExtra("elapsed", elapsed)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
    }

    private fun checkAndRequestPermissions() {
        // 1. Sobreposição (Overlay)
        if (!Settings.canDrawOverlays(this)) {
            showProfessionalDialog(
                title = "Ativar Janela Flutuante",
                message = "Para mostrar o lucro em cima do app da Uber/99, precisamos da sua permissão para sobrepor outros apps.",
                iconRes = R.drawable.ic_permission_layers,
                isAccessibility = false
            ) {
                startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:\$packageName")))
            }
            return
        }

        // 2. Acessibilidade
        if (!isAccessibilityServiceEnabled()) {
            showProfessionalDialog(
                title = "Ativar Leitura Inteligente",
                message = "O Robô usa a Acessibilidade para ler SOMENTE o preço e a distância na tela da oferta.\\n\\n🔒 Seus dados bancários e senhas estão 100% seguros e nunca são lidos.",
                iconRes = R.drawable.ic_permission_eye,
                isAccessibility = true
            ) {
                startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            }
            return
        }

        startOcrService()
    }

    private fun showProfessionalDialog(title: String, message: String, iconRes: Int, isAccessibility: Boolean, positiveAction: () -> Unit) {
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        
        // Infla o layout customizado
        val view = LayoutInflater.from(this).inflate(R.layout.dialog_permission_edu, null)
        dialog.setContentView(view)
        
        // Fundo transparente para respeitar os cantos arredondados
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        dialog.setCancelable(false)

        // Configura textos e ícone
        val tvTitle = view.findViewById<TextView>(R.id.dialog_title)
        val tvMessage = view.findViewById<TextView>(R.id.dialog_message)
        val ivIcon = view.findViewById<ImageView>(R.id.dialog_icon)
        val btnAllow = view.findViewById<Button>(R.id.btn_allow)
        val btnCancel = view.findViewById<TextView>(R.id.btn_cancel)

        tvTitle.text = title
        tvMessage.text = message
        ivIcon.setImageResource(iconRes)

        btnAllow.setOnClickListener {
            dialog.dismiss()
            if (isAccessibility) {
                // Toast extra para guiar o usuário na tela de configurações do Android
                Toast.makeText(this, "Procure por 'Motorista Pro' e ative a chave.", Toast.LENGTH_LONG).show()
            }
            positiveAction()
        }

        btnCancel.setOnClickListener {
            dialog.dismiss()
            Toast.makeText(this, "A permissão é necessária para o Robô funcionar.", Toast.LENGTH_SHORT).show()
        }

        dialog.show()
    }

    private fun startOcrService() {
        try {
            val intent = Intent(this, OcrService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
            Toast.makeText(this, "Robô Iniciado!", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Erro: \${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val enabledServices = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_GENERIC)
        for (service in enabledServices) {
            if (service.resolveInfo.serviceInfo.packageName == packageName &&
                service.resolveInfo.serviceInfo.name.endsWith("WindowMonitorService")) return true
        }
        return false
    }

    override fun onDestroy() {
        super.onDestroy()
        try { unregisterReceiver(jsReceiver) } catch (e: Exception) {}
    }

    override fun onBackPressed() { if (webView.canGoBack()) webView.goBack() else super.onBackPressed() }
}
"""

def write_file(rel_path, content):
    path = os.path.join(PROJECT_PATH, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📝 Criado/Atualizado: {rel_path}")

def main():
    print(f"🚀 Melhorando UX de Permissões em: {PROJECT_NAME}")
    if not os.path.exists(PROJECT_PATH):
        print("❌ Projeto não encontrado."); return

    # 1. BACKUP
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if os.path.exists(os.path.join(PROJECT_PATH, FILES["main_activity"])):
        shutil.copy(os.path.join(PROJECT_PATH, FILES["main_activity"]), os.path.join(BACKUP_DIR, f"MainActivity_{timestamp}.kt"))

    # 2. ESCREVER ARQUIVOS
    write_file(FILES["ic_layers"], IC_LAYERS_CONTENT)
    write_file(FILES["ic_eye"], IC_EYE_CONTENT)
    write_file(FILES["layout_dialog"], LAYOUT_DIALOG_CONTENT)
    write_file(FILES["main_activity"], MAIN_ACTIVITY_CONTENT)

    # 3. GIT
    os.system(f'cd {PROJECT_PATH} && git add . && git commit -m "Feat: Professional Permission Dialogs (Overlay & Accessibility)" && git push')

    # 4. LIMPEZA
    try: os.remove(sys.argv[0]) 
    except: pass

if __name__ == "__main__":
    main()


