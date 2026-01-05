package com.motoristapro.android

import android.util.Log

object Logger {
    // Em produção, usamos Logcat. 
    // O usuário não vê, mas o desenvolvedor vê no Android Studio.
    
    fun log(tag: String, msg: String) {
        // Log.d = Debug. Use Log.i para Info ou Log.e para Erro.
        Log.d("MotoristaPro_$tag", msg)
    }

    fun clear() {
        // Não é necessário limpar Logcat programaticamente
    }
}
