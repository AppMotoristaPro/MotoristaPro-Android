package com.motoristapro.android

import android.accessibilityservice.AccessibilityServiceInfo
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.net.Uri
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

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        setupWebView()
        
        // URL DE PRODUÇÃO CORRIGIDA
        webView.loadUrl("https://motorista-pro-app.onrender.com") 
    }

    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        
        // Ponte JavaScript -> Android
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()
    }

    // --- PONTE JAVASCRIPT ---
    inner class WebAppInterface(private val context: Context) {

        @JavascriptInterface
        fun requestPermission() {
            // Executa na Thread principal para poder mostrar Dialogs/UI
            runOnUiThread {
                checkAndRequestPermissions()
            }
        }

        @JavascriptInterface
        fun subscribeToPush(userId: String) {
            // Lógica de Push (mantida placeholder para este update)
            // FirebaseMessaging.getInstance().subscribeToTopic("user_$userId")
        }
    }

    // --- LÓGICA DE PERMISSÕES E FLOW ---
    
    private fun checkAndRequestPermissions() {
        // 1. Verificar Sobreposição (Overlay) - Para desenhar a bolha flutuante
        if (!Settings.canDrawOverlays(this)) {
            showExplanationDialog(
                title = "Permissão de Sobreposição",
                message = "Para mostrar o lucro flutuante em cima do Uber e 99, o app precisa de permissão para 'Sobrepor outros apps'.",
                positiveAction = {
                    val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
                    startActivity(intent)
                }
            )
            return
        }

        // 2. Verificar Acessibilidade (Leitura de Tela) - Para ler o preço
        if (!isAccessibilityServiceEnabled()) {
            showExplanationDialog(
                title = "Ativar Leitura Automática",
                message = "Para ler o preço e a distância da corrida automaticamente, você precisa ativar o 'Motorista Pro Leitor' nas configurações de Acessibilidade.",
                positiveAction = {
                    val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                    startActivity(intent)
                }
            )
            return
        }

        // 3. Tudo OK -> Iniciar Robô
        startOcrService()
    }

    private fun startOcrService() {
        try {
            val intent = Intent(this, OcrService::class.java)
            startService(intent)
            // Feedback visual para o usuário
            Toast.makeText(this, "🤖 Robô Iniciado! Abra o Uber/99.", Toast.LENGTH_LONG).show()
            
            // Opcional: Minimizar o app para o usuário ir pro Uber
            // moveTaskToBack(true)
        } catch (e: Exception) {
            Toast.makeText(this, "Erro ao iniciar: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    // --- UTILITÁRIOS ---

    private fun showExplanationDialog(title: String, message: String, positiveAction: () -> Unit) {
        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("Configurar") { _, _ -> positiveAction() }
            .setNegativeButton("Cancelar", null)
            .setCancelable(false)
            .show()
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val enabledServices = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_GENERIC)
        for (service in enabledServices) {
            if (service.resolveInfo.serviceInfo.packageName == packageName &&
                service.resolveInfo.serviceInfo.name.endsWith("WindowMonitorService")) {
                return true
            }
        }
        return false
    }
    
    // Tratamento do botão voltar no WebView para não fechar o app direto
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}