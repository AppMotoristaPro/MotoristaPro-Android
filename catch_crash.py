import os

def main():
    print("🚑 Injetando Capturador de Erros (Crash Handler)...")
    
    # Vamos criar uma classe Application personalizada que captura erros globais
    app_class = """package com.motoristapro.android

import android.app.Application
import android.content.Intent
import android.os.Process
import java.io.PrintWriter
import java.io.StringWriter

class MotoristaApp : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // Define o capturador padrão de exceções não tratadas
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            handleUncaughtException(thread, throwable)
        }
    }

    private fun handleUncaughtException(thread: Thread, e: Throwable) {
        e.printStackTrace() // Loga no console se possível

        val sw = StringWriter()
        e.printStackTrace(PrintWriter(sw))
        val stackTrace = sw.toString()

        // Abre uma Activity de Erro para mostrar o texto na tela
        val intent = Intent(applicationContext, ErrorActivity::class.java)
        intent.putExtra("error", stackTrace)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
        startActivity(intent)

        Process.killProcess(Process.myPid())
        System.exit(1)
    }
}
"""
    # Cria o arquivo da Application
    with open("app/src/main/java/com/motoristapro/android/MotoristaApp.kt", "w") as f:
        f.write(app_class)

    # Cria a Activity de Erro (Layout via código para não depender de XML que pode estar quebrado)
    error_activity = """package com.motoristapro.android

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
"""
    with open("app/src/main/java/com/motoristapro/android/ErrorActivity.kt", "w") as f:
        f.write(error_activity)

    # Atualiza o AndroidManifest.xml para usar a nova Application e registrar a ErrorActivity
    manifest_path = "app/src/main/AndroidManifest.xml"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = f.read()

    # 1. Adiciona android:name=".MotoristaApp" na tag <application>
    if 'android:name=".MotoristaApp"' not in manifest:
        manifest = manifest.replace('<application', '<application android:name=".MotoristaApp"')
    
    # 2. Adiciona a ErrorActivity
    if 'ErrorActivity' not in manifest:
        activity_tag = '<activity android:name=".ErrorActivity" android:process=":error_process" />'
        manifest = manifest.replace('</application>', f'    {activity_tag}\n    </application>')

    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest)

    print("✅ Sistema de Debug instalado. Compile e abra o app para ver o erro.")

if __name__ == "__main__":
    main()


