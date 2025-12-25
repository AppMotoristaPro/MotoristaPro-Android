import os

# --- CONFIGURAÇÃO ---
# Mantém a URL atual ou põe uma de teste
SITE_URL = "https://motoristapro.onrender.com"

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo atualizado: {path}")

def main():
    print("🚨 Adicionando Botão de Início Forçado (Offline)...")
    
    path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"
    
    # Código com o Botão Nativo sobreposto ao WebView
    code = f"""package com.motoristapro.android

import android.app.DownloadManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.webkit.*
import android.widget.Button
import android.widget.FrameLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {{

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    inner class WebAppInterface(private val mContext: Context) {{
        @JavascriptInterface
        fun startRobot() {{
            checkPermissionsAndStart()
        }}
        
        @JavascriptInterface
        fun getVersionCode(): Int {{
            return try {{
                val pInfo = mContext.packageManager.getPackageInfo(mContext.packageName, 0)
                if (Build.VERSION.SDK_INT >= 28) pInfo.longVersionCode.toInt() else pInfo.versionCode
            }} catch (e: Exception) {{ 0 }}
        }}
        
        @JavascriptInterface
        fun updateConfig(goodKm: Double, badKm: Double, goodHour: Double, badHour: Double) {{
            val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
            prefs.edit()
                .putFloat("good_km", goodKm.toFloat())
                .putFloat("bad_km", badKm.toFloat())
                .putFloat("good_hour", goodHour.toFloat())
                .putFloat("bad_hour", badHour.toFloat())
                .apply()
            val intent = Intent("OCR_CONFIG_UPDATED")
            androidx.localbroadcastmanager.content.LocalBroadcastManager.getInstance(mContext).sendBroadcast(intent)
            runOnUiThread {{ Toast.makeText(mContext, "Configurado via Site!", Toast.LENGTH_SHORT).show() }}
        }}
    }}

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        
        // Layout Raiz (FrameLayout permite empilhar coisas)
        val root = FrameLayout(this)
        setContentView(root)
        
        // 1. WebView (Fica no fundo)
        webView = WebView(this)
        webView.layoutParams = FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT)
        
        // Configs Web
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        webView.settings.userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 MotoristaProApp"
        
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }}

        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = object : WebViewClient() {{
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {{
                if (url != null && (url.startsWith("whatsapp:") || url.startsWith("geo:") || url.startsWith("tel:"))) {{
                    try {{ startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }} catch(e:Exception){{}}
                    return true
                }}
                return false
            }}
            override fun onPageFinished(view: WebView?, url: String?) {{
                super.onPageFinished(view, url)
                if (Build.VERSION.SDK_INT >= 21) CookieManager.getInstance().flush()
            }}
        }}

        webView.setDownloadListener {{ url, userAgent, contentDisposition, mimetype, contentLength ->
            try {{
                val request = DownloadManager.Request(Uri.parse(url))
                request.setMimeType(mimetype)
                request.addRequestHeader("cookie", CookieManager.getInstance().getCookie(url))
                request.addRequestHeader("User-Agent", userAgent)
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, URLUtil.guessFileName(url, contentDisposition, mimetype))
                val dm = getSystemService(DOWNLOAD_SERVICE) as DownloadManager
                dm.enqueue(request)
                Toast.makeText(this, "Baixando...", Toast.LENGTH_SHORT).show()
            }} catch (e: Exception) {{
                try {{ startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }} catch (e2: Exception) {{}}
            }}
        }}
        
        root.addView(webView)
        
        // 2. BOTÃO DE EMERGÊNCIA (Fica na frente)
        val btnStart = Button(this).apply {{
            text = "🤖 INICIAR ROBÔ (OFFLINE)"
            textSize = 14f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply {{
                setColor(Color.parseColor("#10B981")) // Verde
                cornerRadius = 50f
                setStroke(2, Color.WHITE)
            }}
            elevation = 20f
            setPadding(40, 20, 40, 20)
            setOnClickListener {{
                Toast.makeText(context, "Iniciando modo manual...", Toast.LENGTH_SHORT).show()
                checkPermissionsAndStart()
            }}
        }}

        // Posiciona no final da tela, centralizado
        val paramsBtn = FrameLayout.LayoutParams(FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT).apply {{
            gravity = Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL
            bottomMargin = 100 // Margem do fundo
        }}
        
        root.addView(btnStart, paramsBtn)

        // Carrega Site
        webView.loadUrl("{SITE_URL}")
    }}

    private fun checkPermissionsAndStart() {{
        if (!Settings.canDrawOverlays(this)) {{
            Toast.makeText(this, "Preciso de permissão para desenhar na tela", Toast.LENGTH_LONG).show()
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }}
        val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(mpManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
    }}

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {{
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION) {{
            if (resultCode == RESULT_OK && data != null) {{
                val serviceIntent = Intent(this, OcrService::class.java).apply {{
                    putExtra("RESULT_CODE", resultCode)
                    putExtra("RESULT_DATA", data)
                }}
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
                    startForegroundService(serviceIntent)
                }} else {{
                    startService(serviceIntent)
                }}
                // Minimizar
                moveTaskToBack(true)
            }}
        }}
    }}

    override fun onBackPressed() {{ if (webView.canGoBack()) webView.goBack() else super.onBackPressed() }}
}}
"""
    write_file(path, code)
    
    # Incrementa versão para garantir update
    os.system("python3 auto_version.py")
    
    print("✅ Botão offline adicionado! Compile o APK.")

if __name__ == "__main__":
    main()
