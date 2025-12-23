import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- MAIN ACTIVITY COM NOVA URL ---
main_activity_content = """
package com.motoristapro.android

import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.FrameLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Container Raiz
        val root = FrameLayout(this)
        setContentView(root)

        // WebView (Fundo)
        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        
        // Garante que links abram dentro do app
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                view?.loadUrl(url ?: return false)
                return true
            }
        }
        
        // URL ATUALIZADA (GitHub Dev Environment)
        webView.loadUrl("https://refactored-space-tribble-v69ggpvvvj94hxprw-5000.app.github.dev")
        
        root.addView(webView)

        // Botão Flutuante para Iniciar o OCR (Frente)
        val btnStart = Button(this)
        btnStart.text = "ATIVAR LEITURA"
        val params = FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.WRAP_CONTENT,
            FrameLayout.LayoutParams.WRAP_CONTENT
        )
        params.gravity = android.view.Gravity.BOTTOM or android.view.Gravity.END
        params.setMargins(0, 0, 50, 150)
        btnStart.layoutParams = params
        root.addView(btnStart)

        btnStart.setOnClickListener {
            checkPermissionsAndStart()
        }
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            Toast.makeText(this, "Permita a sobreposição!", Toast.LENGTH_LONG).show()
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
                // Inicia o Serviço de OCR
                val serviceIntent = Intent(this, OcrService::class.java).apply {
                    putExtra("RESULT_CODE", resultCode)
                    putExtra("RESULT_DATA", data)
                }
                
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    startForegroundService(serviceIntent)
                } else {
                    startService(serviceIntent)
                }
            } else {
                Toast.makeText(this, "Permissão de tela negada!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
"""

print("--- Atualizando URL para Ambiente de Desenvolvimento ---")
create_file("app/src/main/java/com/motoristapro/android/MainActivity.kt", main_activity_content)

print("\nURL Atualizada.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Config: Update WebView URL'")
print("3. git push")


