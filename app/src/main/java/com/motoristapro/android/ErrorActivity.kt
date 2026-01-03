package com.motoristapro.android

import android.app.Activity
import android.os.Bundle
import android.widget.ScrollView
import android.widget.TextView
import android.graphics.Color
import android.widget.LinearLayout

class ErrorActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val scroll = ScrollView(this)
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.setPadding(50, 50, 50, 50)
        layout.setBackgroundColor(Color.WHITE)

        val title = TextView(this)
        title.text = "ERRO FATAL (CRASH)"
        title.textSize = 24f
        title.setTextColor(Color.RED)
        title.setPadding(0, 0, 0, 30)

        val message = TextView(this)
        message.text = intent.getStringExtra("error") ?: "Erro desconhecido"
        message.textSize = 14f
        message.setTextColor(Color.BLACK)

        layout.addView(title)
        layout.addView(message)
        scroll.addView(layout)

        setContentView(scroll)
    }
}
