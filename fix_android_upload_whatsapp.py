import os
import shutil

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
PROJETO = "MotoristaPro-Android"
DIR_MAIN = "app/src/main/java/com/motoristapro/android"
FILE_MAIN = os.path.join(DIR_MAIN, "MainActivity.kt")
FILE_MANIFEST = "app/src/main/AndroidManifest.xml"

# ==============================================================================
# CÓDIGO ATUALIZADO: MainActivity.kt
# ==============================================================================
# Adicionamos:
# 1. Variável 'fileUploadCallback' para gerenciar o seletor de arquivos.
# 2. Método 'onShowFileChooser' no WebChromeClient.
# 3. Método 'onActivityResult' para receber o arquivo selecionado.
# 4. Método 'shouldOverrideUrlLoading' no WebViewClient para abrir WhatsApp.

MAIN_ACTIVITY_CONTENT = r"""package com.motoristapro.android

import android.Manifest
import android.app.Dialog
import android.app.DownloadManager
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
import android.os.Environment
import android.os.Message
import android.print.PrintAttributes
import android.print.PrintManager
import android.provider.Settings
import android.util.Base64
import android.view.LayoutInflater
import android.view.ViewGroup
import android.view.Window
import android.webkit.*
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.google.firebase.messaging.FirebaseMessaging
import java.io.File
import java.io.FileOutputStream

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private val NOTIFICATION_PERMISSION_CODE = 101
    
    // Variáveis para Upload de Arquivo
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    private val FILE_CHOOSER_RESULT_CODE = 100

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

        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(jsReceiver, IntentFilter("wwebview.js_command"), Context.RECEIVER_EXPORTED)
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

    // Callback para receber o arquivo selecionado (Backup)
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILE_CHOOSER_RESULT_CODE) {
            if (fileUploadCallback == null) return
            val results = WebChromeClient.FileChooserParams.parseResult(resultCode, data)
            fileUploadCallback?.onReceiveValue(results)
            fileUploadCallback = null
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    private fun handleIntent(intent: Intent?) {
        if (intent?.action == "OPEN_ADD_SCREEN") {
            val h = intent.getIntExtra("h_val", 0)
            val m = intent.getIntExtra("m_val", 0)
            webView.loadUrl("https://motorista-pro-app.onrender.com/adicionar?tempo_cronometro=$h:$m")
        } else if (webView.url == null) {
            webView.loadUrl("https://motorista-pro-app.onrender.com")
        }
    }

    private fun setupWebView(view: WebView) {
        val settings = view.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.javaScriptCanOpenWindowsAutomatically = true
        settings.setSupportMultipleWindows(true)
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        
        val defaultUA = settings.userAgentString
        settings.userAgentString = defaultUA.replace("; wv", "") + " (MotoristaPro)"

        if (view == webView) {
            view.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")
        }

        // Configuração de Downloads
        view.setDownloadListener { url, userAgent, contentDisposition, mimetype, contentLength ->
            try {
                val request = DownloadManager.Request(Uri.parse(url))
                request.setMimeType(mimetype)
                request.addRequestHeader("User-Agent", userAgent)
                request.setDescription("Baixando arquivo...")
                val fileName = URLUtil.guessFileName(url, contentDisposition, mimetype)
                request.setTitle(fileName)
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName)
                
                val dm = getSystemService(DOWNLOAD_SERVICE) as DownloadManager
                dm.enqueue(request)
                Toast.makeText(applicationContext, "Download iniciado...", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Toast.makeText(applicationContext, "Erro ao baixar: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }

        view.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                val jsPrint = "window.print = function() { MotoristaProAndroid.printPage(); };"
                view?.evaluateJavascript(jsPrint, null)
            }

            // CORREÇÃO WHATSAPP: Intercepta links externos
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                
                // Se for http/https normal, deixa o WebView carregar
                if (url.startsWith("http://") || url.startsWith("https://")) {
                    // Exceção: Links do WhatsApp Web que redirecionam para app
                    if (url.contains("wa.me") || url.contains("api.whatsapp.com")) {
                        return false // Deixa carregar e o site redireciona para scheme whatsapp://
                    }
                    return false 
                }

                // Se for esquema customizado (whatsapp://, tel:, mailto:, intent://)
                try {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    startActivity(intent)
                    return true // Nós tratamos, WebView não precisa fazer nada
                } catch (e: Exception) {
                    // App não instalado (ex: WhatsApp não instalado)
                    return true 
                }
            }
        }

        view.webChromeClient = object : WebChromeClient() {
            // CORREÇÃO UPLOAD: Abre seletor de arquivos nativo
            override fun onShowFileChooser(webView: WebView?, filePathCallback: ValueCallback<Array<Uri>>?, fileChooserParams: FileChooserParams?): Boolean {
                if (fileUploadCallback != null) {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = null
                }
                fileUploadCallback = filePathCallback

                val intent = fileChooserParams?.createIntent()
                try {
                    startActivityForResult(intent, FILE_CHOOSER_RESULT_CODE)
                } catch (e: Exception) {
                    fileUploadCallback = null
                    return false
                }
                return true
            }

            override fun onCreateWindow(view: WebView?, isDialog: Boolean, isUserGesture: Boolean, resultMsg: Message?): Boolean {
                val newWebView = WebView(this@MainActivity)
                setupWebView(newWebView) // Aplica as mesmas regras (WhatsApp, Uploads) para popups
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

        @JavascriptInterface
        fun printPage() {
            runOnUiThread {
                val printManager = getSystemService(Context.PRINT_SERVICE) as? PrintManager
                val adapter = webView.createPrintDocumentAdapter("MotoristaPro_Doc")
                printManager?.print("Documento_MotoristaPro", adapter, PrintAttributes.Builder().build())
            }
        }

        @JavascriptInterface
        fun shareBase64Image(base64Data: String, title: String) {
            runOnUiThread {
                try {
                    val cleanBase64 = if (base64Data.contains(",")) base64Data.split(",")[1] else base64Data
                    val decodedString = Base64.decode(cleanBase64, Base64.DEFAULT)
                    
                    val cachePath = File(context.cacheDir, "images")
                    cachePath.mkdirs()
                    val stream = FileOutputStream("$cachePath/recibo.png")
                    stream.write(decodedString)
                    stream.close()

                    val newFile = File(cachePath, "recibo.png")
                    val contentUri = FileProvider.getUriForFile(context, "$packageName.provider", newFile)

                    if (contentUri != null) {
                        val shareIntent = Intent()
                        shareIntent.action = Intent.ACTION_SEND
                        shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                        shareIntent.setDataAndType(contentUri, context.contentResolver.getType(contentUri))
                        shareIntent.putExtra(Intent.EXTRA_STREAM, contentUri)
                        shareIntent.type = "image/png"
                        startActivity(Intent.createChooser(shareIntent, title))
                    }
                } catch (e: Exception) {
                    Toast.makeText(context, "Erro: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun checkAndRequestPermissions() {
        if (!Settings.canDrawOverlays(this)) {
            showProfessionalDialog(
                title = "Permissão de Sobreposição",
                message = "O Motorista Pro precisa exibir informações sobrepostas.",
                iconRes = R.drawable.ic_permission_layers,
                isAccessibility = false
            ) {
                startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName")))
            }
            return
        }

        if (!isAccessibilityServiceEnabled()) {
            showProfessionalDialog(
                title = "Serviço de Acessibilidade",
                message = "Necessário para leitura de tela.",
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

        view.findViewById<TextView>(R.id.dialog_title).text = title
        view.findViewById<TextView>(R.id.dialog_message).text = message
        view.findViewById<ImageView>(R.id.dialog_icon).setImageResource(iconRes)

        view.findViewById<Button>(R.id.btn_allow).setOnClickListener {
            dialog.dismiss()
            if (isAccessibility) Toast.makeText(this, "Toque em 'Aplicativos instalados' > 'Motorista Pro'", Toast.LENGTH_LONG).show()
            positiveAction()
        }
        view.findViewById<TextView>(R.id.btn_cancel).setOnClickListener { dialog.dismiss() }
        dialog.show()
        dialog.window?.setLayout((resources.displayMetrics.widthPixels * 0.90).toInt(), ViewGroup.LayoutParams.WRAP_CONTENT)
    }

    private fun startOcrService() {
        try {
            val intent = Intent(this, OcrService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
            Toast.makeText(this, "Robô Iniciado!", Toast.LENGTH_LONG).show()
        } catch (e: Exception) { Toast.makeText(this, "Erro: ${e.message}", Toast.LENGTH_SHORT).show() }
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

# ==============================================================================
# FUNÇÕES
# ==============================================================================

def log(msg): print(f"\033[36m[{PROJETO}] {msg}\033[0m")

def atualizar_manifest():
    if not os.path.exists(FILE_MANIFEST): return
    with open(FILE_MANIFEST, "r", encoding="utf-8") as f: content = f.read()
    
    # Adicionar permissão de visibilidade do WhatsApp
    if '<package android:name="com.whatsapp" />' not in content:
        # Insere dentro da tag <queries>
        content = content.replace('</queries>', '    <package android:name="com.whatsapp" />\n        <package android:name="com.whatsapp.w4b" />\n    </queries>')
        with open(FILE_MANIFEST, "w", encoding="utf-8") as f: f.write(content)
        log("AndroidManifest.xml atualizado (Queries do WhatsApp).")

def incrementar_versao():
    import re
    arq_gradle = "app/build.gradle.kts"
    if not os.path.exists(arq_gradle): return
    with open(arq_gradle, "r", encoding="utf-8") as f: content = f.read()
    match = re.search(r'(versionCode\s*=\s*)(\d+)', content)
    if match:
        new_ver = int(match.group(2)) + 1
        content = re.sub(r'(versionCode\s*=\s*)(\d+)', fr'\g<1>{new_ver}', content)
        with open(arq_gradle, "w", encoding="utf-8") as f: f.write(content)
        log(f"Versão incrementada para {new_ver}")
        return new_ver
    return 0

def aplicar():
    # 1. Substituir Main Activity
    with open(FILE_MAIN, "w", encoding="utf-8") as f: f.write(MAIN_ACTIVITY_CONTENT)
    log("MainActivity.kt atualizada com suporte a Upload e WhatsApp.")

    # 2. Atualizar Manifest
    atualizar_manifest()

    # 3. Git e Versão
    ver = incrementar_versao()
    os.system("git add .")
    os.system(f'git commit -m "Feat: Fix Upload de Arquivos e Links WhatsApp - v{ver}"')
    os.system("git push")
    log("Git Push realizado.")

if __name__ == "__main__":
    aplicar()


