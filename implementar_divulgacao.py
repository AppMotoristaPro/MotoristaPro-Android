import os

# Caminho do arquivo MainActivity.kt
file_path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"

# Novo conteúdo do arquivo com o Diálogo de Divulgação
new_content = r'''package com.motoristapro.android

import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.media.projection.MediaProjectionManager
import android.webkit.CookieManager
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102
    
    // URL FIXA
    private val SITE_URL = "https://motorista-pro-app.onrender.com"

    inner class WebAppInterface(private val mContext: Context) {
        @JavascriptInterface
        fun startRobot() {
            // Em vez de iniciar direto, mostra a divulgação
            runOnUiThread {
                showPrivacyDisclosure()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        val btnStart = findViewById<Button>(R.id.btnStartRobot)
        
        // Ação do Botão Offline
        btnStart.setOnClickListener {
            showPrivacyDisclosure()
        }

        // Configurações Web
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        
        // Cookies
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }

        // Interface JS
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                if (url != null && (url.startsWith("whatsapp:") || url.startsWith("geo:") || url.startsWith("tel:"))) {
                    try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch(e:Exception){}
                    return true
                }
                return false
            }
        }

        // Carrega o Site
        webView.loadUrl(SITE_URL)
    }

    /**
     * EXIGÊNCIA DO GOOGLE PLAY: Divulgação Proeminente.
     * Deve explicar O QUE é coletado e PARA QUE, antes da permissão do sistema.
     */
    private fun showPrivacyDisclosure() {
        AlertDialog.Builder(this)
            .setTitle("Aviso de Privacidade")
            .setMessage("O Motorista Pro utiliza a funcionalidade de captura de tela (Media Projection) exclusivamente para ler informações de corridas (preço, distância e tempo) e calcular seus ganhos em tempo real.\n\nEsses dados são processados localmente no seu dispositivo e NÃO são compartilhados com servidores externos ou terceiros.\n\nPara utilizar o Robô, você precisa concordar com esta coleta e conceder as permissões a seguir.")
            .setPositiveButton("Concordo e Continuar") { dialog, _ ->
                dialog.dismiss()
                checkPermissionsAndStart()
            }
            .setNegativeButton("Cancelar") { dialog, _ ->
                dialog.dismiss()
                Toast.makeText(this, "Funcionalidade cancelada", Toast.LENGTH_SHORT).show()
            }
            .setCancelable(false)
            .show()
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "Permita a sobreposição para ver os cálculos", Toast.LENGTH_LONG).show()
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
        
        // Solicita a captura de tela
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
            } else {
                Toast.makeText(this, "Permissão de captura negada.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
}
'''

if os.path.exists(os.path.dirname(file_path)):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ MainActivity.kt atualizado com Divulgação Proeminente!")
else:
    print(f"❌ Erro: Diretório não encontrado.")


