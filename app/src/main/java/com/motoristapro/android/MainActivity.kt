package com.motoristapro.android

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Inicializa a WebView
        webView = WebView(this)
        setContentView(webView)

        // Configurações da WebView para Aplicações Modernas (React/SPA)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true // Necessário para persistência de dados (localStorage)
            databaseEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            
            // Ajustes de viewport para mobile
            useWideViewPort = true
            loadWithOverviewMode = true
        }

        // Garante que links abram dentro do app, não no Chrome externo
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                view?.loadUrl(url ?: return false)
                return true
            }
        }

        // URL Alvo
        webView.loadUrl("https://motorista-pro-app.onrender.com")
    }

    // Comportamento do botão Voltar (Back)
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}