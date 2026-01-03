package com.motoristapro.android

import android.os.Environment
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object Logger {
    private const val FILE_NAME = "motorista_full_trace.txt"
    private val dateFormat = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault())

    fun log(tag: String, msg: String) {
        try {
            val dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            val file = File(dir, FILE_NAME)
            val timestamp = dateFormat.format(Date())
            
            // Formato: [12:00:00.000] [TAG] Mensagem
            val line = "[$timestamp] [$tag] $msg\n"
            
            val writer = FileWriter(file, true)
            writer.append(line)
            writer.flush()
            writer.close()
        } catch (e: Exception) {
            // Falha silenciosa para não travar o app
        }
    }
    
    fun clear() {
        try {
            val dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            val file = File(dir, FILE_NAME)
            if (file.exists()) file.delete()
        } catch (e: Exception) {}
    }
}
