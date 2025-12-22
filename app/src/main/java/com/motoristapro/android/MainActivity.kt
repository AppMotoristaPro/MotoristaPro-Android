package com.motoristapro.android

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import android.view.Gravity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Criando a UI via código para simplificar esta fase inicial
        val textView = TextView(this)
        textView.text = "Motorista Pro Android\nFase 1: Setup Completo!\n\nAguardando Webview e OCR..."
        textView.textSize = 24f
        textView.gravity = Gravity.CENTER
        
        setContentView(textView)
    }
}