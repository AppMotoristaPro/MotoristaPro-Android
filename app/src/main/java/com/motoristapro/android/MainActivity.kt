package com.motoristapro.android

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
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
            // Correção da string com escape correto
            webView.loadUrl("https://motorista-pro-app.onrender.com/adicionar?tempo_cronometro=$h:$m")
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
            if (userId.isNotEmpty()) FirebaseMessaging.getInstance().subscribeToTopic("user_$userId")
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
                title = "Permissão de Sobreposição",
                // TEXTO OTIMIZADO PARA GOOGLE PLAY: Explica O QUE e PARA QUE
                message = "O Motorista Pro precisa exibir informações sobrepostas a outros aplicativos para mostrar o cálculo de lucro em tempo real enquanto você navega no app de viagens.",
                iconRes = R.drawable.ic_permission_layers,
                isAccessibility = false
            ) {
                val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
                startActivity(intent)
            }
            return
        }

        // 2. Acessibilidade
        if (!isAccessibilityServiceEnabled()) {
            showProfessionalDialog(
                title = "Serviço de Acessibilidade",
                // TEXTO BLINDADO PARA GOOGLE PLAY (Prominent Disclosure)
                message = "O Motorista Pro utiliza a API de Acessibilidade para ler o conteúdo da tela apenas quando os apps de viagem estão abertos. Isso é necessário para extrair automaticamente o preço e a distância da corrida e calcular o seu lucro líquido.\n\nNenhum outro dado pessoal ou sensível é coletado, armazenado ou compartilhado.",
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
        
        val view = LayoutInflater.from(this).inflate(R.layout.dialog_permission_edu, null)
        dialog.setContentView(view)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        dialog.setCancelable(false)

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
                Toast.makeText(this, "Toque em 'Aplicativos instalados' > 'Motorista Pro'", Toast.LENGTH_LONG).show()
            }
            positiveAction()
        }

        btnCancel.setOnClickListener {
            dialog.dismiss()
        }

        dialog.show()
    }

    private fun startOcrService() {
        try {
            val intent = Intent(this, OcrService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
            Toast.makeText(this, "Robô Iniciado!", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Erro: ${e.message}", Toast.LENGTH_SHORT).show()
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
