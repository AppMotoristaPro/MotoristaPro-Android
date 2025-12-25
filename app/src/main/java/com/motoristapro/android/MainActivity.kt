package com.motoristapro.android

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
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    // Interface JS (Ponte Site <-> App)
    inner class WebAppInterface(private val mContext: Context) {
        
        // Inicia o Robô
        @JavascriptInterface
        fun startRobot() {
            checkPermissionsAndStart()
        }
        
        // Retorna a versão atual do App para o Site verificar se há update
        @JavascriptInterface
        fun getVersionCode(): Int {
            return try {
                val pInfo = mContext.packageManager.getPackageInfo(mContext.packageName, 0)
                if (Build.VERSION.SDK_INT >= 28) pInfo.longVersionCode.toInt() else pInfo.versionCode
            } catch (e: Exception) { 0 }
        }
        
        // Atualiza configurações vindas do site (Backup)
        @JavascriptInterface
        fun updateConfig(goodKm: Double, badKm: Double, goodHour: Double, badHour: Double) {
            val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
            prefs.edit()
                .putFloat("good_km", goodKm.toFloat())
                .putFloat("bad_km", badKm.toFloat())
                .putFloat("good_hour", goodHour.toFloat())
                .putFloat("bad_hour", badHour.toFloat())
                .apply()
                
            val intent = Intent("OCR_CONFIG_UPDATED")
            androidx.localbroadcastmanager.content.LocalBroadcastManager.getInstance(mContext).sendBroadcast(intent)
            runOnUiThread { Toast.makeText(mContext, "Sincronizado com Site!", Toast.LENGTH_SHORT).show() }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        webView = WebView(this)
        setContentView(webView)

        // Configurações Web
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        
        // User Agent "Fake Chrome" para passar no Google Login e "MotoristaProApp" para o site detectar
        val ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 MotoristaProApp"
        webView.settings.userAgentString = ua
        
        // Cookies (Essencial para Login Google não perder sessão)
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }

        // Ponte JS
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                // Links externos (WhatsApp, Maps, Tel)
                if (url != null && (url.startsWith("whatsapp:") || url.startsWith("geo:") || url.startsWith("tel:") || url.startsWith("mailto:"))) {
                    try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch(e:Exception){}
                    return true
                }
                return false
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // Força salvar cookies
                if (Build.VERSION.SDK_INT >= 21) CookieManager.getInstance().flush()
                
                // Segurança: Se sair da conta, mata o robô
                if (url != null && (url.contains("/login") || url.contains("/register"))) {
                    stopService(Intent(this@MainActivity, OcrService::class.java))
                }
            }
        }

        // Gerenciador de Downloads Nativo (Resolve o bug de clicar e nada acontecer)
        webView.setDownloadListener { url, userAgent, contentDisposition, mimetype, contentLength ->
            try {
                val request = DownloadManager.Request(Uri.parse(url))
                request.setMimeType(mimetype)
                request.addRequestHeader("cookie", CookieManager.getInstance().getCookie(url))
                request.addRequestHeader("User-Agent", userAgent)
                request.setDescription("Baixando arquivo...")
                request.setTitle(URLUtil.guessFileName(url, contentDisposition, mimetype))
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, URLUtil.guessFileName(url, contentDisposition, mimetype))
                
                val dm = getSystemService(DOWNLOAD_SERVICE) as DownloadManager
                dm.enqueue(request)
                Toast.makeText(this, "Download iniciado...", Toast.LENGTH_LONG).show()
            } catch (e: Exception) {
                // Fallback: Tenta abrir no navegador se falhar
                try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch (e2: Exception) { Toast.makeText(this, "Erro no download", Toast.LENGTH_SHORT).show() }
            }
        }
        
        webView.loadUrl("https://motoristapro.onrender.com")
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
                // Minimizar para mostrar o overlay
                val startMain = Intent(Intent.ACTION_MAIN)
                startMain.addCategory(Intent.CATEGORY_HOME)
                startMain.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                startActivity(startMain)
            }
        }
    }

    override fun onBackPressed() { if (webView.canGoBack()) webView.goBack() else super.onBackPressed() }
}
