package com.motoristapro.android

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
