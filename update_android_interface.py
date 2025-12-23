import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- MAIN ACTIVITY (Com JS Interface e Sem Botão Flutuante) ---
main_activity_content = """
package com.motoristapro.android

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.localbroadcastmanager.content.LocalBroadcastManager

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    // Interface para o Javascript chamar o Android
    inner class WebAppInterface(private val mContext: Context) {
        @JavascriptInterface
        fun requestPermission() {
            runOnUiThread {
                checkPermissionsAndStart()
            }
        }
    }

    private val ocrReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == "OCR_DATA_DETECTED") {
                val price = intent.getDoubleExtra("price", 0.0)
                val dist = intent.getDoubleExtra("dist", 0.0)
                val time = intent.getDoubleExtra("time", 0.0)
                injectDataIntoSite(price, dist, time)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = FrameLayout(this)
        setContentView(root)

        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        
        // Define o UserAgent para o site saber que é o App
        webView.settings.userAgentString = webView.settings.userAgentString + " MotoristaProApp"
        
        // Injeta a interface JS
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                view?.loadUrl(url ?: return false)
                return true
            }
        }
        
        // URL DO SITE
        webView.loadUrl("https://refactored-space-tribble-v69ggpvvvj94hxprw-5000.app.github.dev")
        
        root.addView(webView)

        // Botão flutuante REMOVIDO! Agora o controle é pelo site.

        LocalBroadcastManager.getInstance(this).registerReceiver(
            ocrReceiver, IntentFilter("OCR_DATA_DETECTED")
        )
    }

    private fun injectDataIntoSite(price: Double, dist: Double, time: Double) {
        val currentUrl = webView.url ?: ""
        if (currentUrl.contains("/adicionar")) {
            val jsCommand = "if(window.MotoristaProBridge) { window.MotoristaProBridge.preencherDados($price, $dist, $time); }"
            webView.evaluateJavascript(jsCommand, null)
        }
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
        startProjectionRequest()
    }

    private fun startProjectionRequest() {
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
                
                // Avisa o site que começou
                webView.evaluateJavascript("if(window.onServiceStarted) window.onServiceStarted();", null)
            } else {
                Toast.makeText(this, "Permissão negada.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        LocalBroadcastManager.getInstance(this).unregisterReceiver(ocrReceiver)
    }
}
"""

print("--- Removendo Botão Flutuante e Adicionando Ponte JS ---")
create_file("app/src/main/java/com/motoristapro/android/MainActivity.kt", main_activity_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'UI: Move Activation Button to Web'")
print("3. git push")


