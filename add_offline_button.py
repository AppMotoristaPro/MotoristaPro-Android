import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Atualizado: {path}")

def main():
    print("🔘 Adicionando Botão 'Iniciar Robô' Independente...")

    base_res = "app/src/main/res/layout"
    base_java = "app/src/main/java/com/motoristapro/android"

    # ==============================================================================
    # 1. NOVO LAYOUT (WebView + Botão Flutuante)
    # ==============================================================================
    layout_xml = """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- O Site carrega aqui no fundo -->
    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <!-- Botão Nativo (Sempre visível) -->
    <Button
        android:id="@+id/btnForceStart"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="INICIAR ROBÔ"
        android:layout_gravity="bottom|center_horizontal"
        android:layout_marginBottom="40dp"
        android:paddingStart="30dp"
        android:paddingEnd="30dp"
        android:paddingTop="15dp"
        android:paddingBottom="15dp"
        android:backgroundTint="#2563EB"
        android:textColor="#FFFFFF"
        android:textSize="16sp"
        android:textStyle="bold"
        android:elevation="10dp"/>

</FrameLayout>
"""
    write_file(f"{base_res}/activity_main.xml", layout_xml)

    # ==============================================================================
    # 2. ATUALIZAR KOTLIN (Ligar o botão)
    # ==============================================================================
    # Vamos ler o arquivo atual para manter as configs de WebView e só adicionar o botão
    main_path = f"{base_java}/MainActivity.kt"
    
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Adiciona imports se faltarem
        if "import android.widget.Button" not in content:
            content = content.replace("import android.os.Bundle", "import android.os.Bundle\nimport android.widget.Button\nimport android.widget.FrameLayout")

        # Injeta a lógica do botão no onCreate
        # Procura onde o WebView é definido
        if "webView = findViewById(R.id.webView)" in content:
            button_logic = """
        webView = findViewById(R.id.webView)
        
        // --- BOTÃO OFFLINE ---
        val btnForce = findViewById<Button>(R.id.btnForceStart)
        btnForce.setOnClickListener {
            Toast.makeText(this, "Iniciando modo manual...", Toast.LENGTH_SHORT).show()
            checkPermissionsAndStart()
        }
            """
            content = content.replace("webView = findViewById(R.id.webView)", button_logic)
            
            write_file(main_path, content)
        else:
            # Se a estrutura estiver muito diferente, reescrevemos o arquivo básico seguro
            print("⚠️ Estrutura diferente detectada. Reescrevendo MainActivity completa para garantir...")
            
            full_code = """package com.motoristapro.android

import android.app.DownloadManager
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.webkit.*
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102
    
    // URL do Site (Pode ser alterada via script depois)
    private val SITE_URL = "https://motoristapro.onrender.com"

    inner class WebAppInterface(private val mContext: Context) {
        @JavascriptInterface
        fun startRobot() {
            checkPermissionsAndStart()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        
        // BOTÃO NATIVO DE INÍCIO
        findViewById<Button>(R.id.btnForceStart).setOnClickListener {
            checkPermissionsAndStart()
        }

        // Configurações Web
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 MotoristaProApp"

        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }

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
        
        // Download Manager
        webView.setDownloadListener { url, userAgent, contentDisposition, mimetype, contentLength ->
            try {
                val request = DownloadManager.Request(Uri.parse(url))
                request.setMimeType(mimetype)
                request.addRequestHeader("cookie", CookieManager.getInstance().getCookie(url))
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, URLUtil.guessFileName(url, contentDisposition, mimetype))
                val dm = getSystemService(DOWNLOAD_SERVICE) as DownloadManager
                dm.enqueue(request)
                Toast.makeText(this, "Baixando...", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch (e2: Exception) {}
            }
        }

        webView.loadUrl(SITE_URL)
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
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
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
}
"""
            write_file(main_path, full_code)

    # Incrementa versão
    os.system("python3 auto_version.py")
    print("🚀 Botão Adicionado! Compile e Instale.")

if __name__ == "__main__":
    main()


