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
        webView.webViewClient = WebViewClient()
        webView.loadUrl("https://motorista-pro-app.onrender.com")
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
                val serviceIntent = Intent(this, OcrService::class.java).apply {
                    putExtra("RESULT_CODE", resultCode)
                    putExtra("RESULT_DATA", data)
                }
                startForegroundService(serviceIntent)
            } else {
                Toast.makeText(this, "Permissão de tela negada!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
}