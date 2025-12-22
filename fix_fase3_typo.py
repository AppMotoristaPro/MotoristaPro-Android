import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Corrigido: {path}")

# --- OCR SERVICE CORRIGIDO ---
ocr_service_content = """
package com.motoristapro.android

import android.app.*
import android.content.Intent
import android.graphics.PixelFormat
import android.os.IBinder
import android.view.Gravity
import android.view.WindowManager
import android.widget.TextView
import android.widget.LinearLayout
import android.graphics.Color
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import android.media.projection.MediaProjectionManager
import android.media.projection.MediaProjection
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.util.DisplayMetrics

class OcrService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var overlayView: LinearLayout
    private lateinit var statusText: TextView
    private lateinit var resultText: TextView
    
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    
    // CORREÇÃO: Espaço adicionado entre 'var' e 'imageReader'
    private var imageReader: ImageReader? = null
    
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var isRunning = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForeground()
        setupOverlay()
    }

    private fun startForeground() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro Ativo")
            .setContentText("Lendo tela em busca de corridas...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .build()

        startForeground(1, notification)
    }

    private fun setupOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        overlayView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#CC000000"))
            setPadding(20, 20, 20, 20)
        }

        statusText = TextView(this).apply {
            text = "Aguardando..."
            setTextColor(Color.YELLOW)
            textSize = 12f
        }
        
        resultText = TextView(this).apply {
            text = "--"
            setTextColor(Color.WHITE)
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
        }

        overlayView.addView(statusText)
        overlayView.addView(resultText)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.START
        params.x = 50
        params.y = 200

        windowManager.addView(overlayView, params)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val resultCode = intent?.getIntExtra("RESULT_CODE", 0) ?: 0
        val resultData = intent?.getParcelableExtra<Intent>("RESULT_DATA")

        if (resultCode != 0 && resultData != null) {
            startMediaProjection(resultCode, resultData)
        }
        return START_STICKY
    }

    private fun startMediaProjection(code: Int, data: Intent) {
        val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = mpManager.getMediaProjection(code, data)
        
        val metrics = DisplayMetrics()
        windowManager.defaultDisplay.getMetrics(metrics)
        
        // Setup placeholder do OCR loop
        isRunning = true
        startOcrLoop()
    }

    private fun startOcrLoop() {
        scope.launch {
            while (isRunning) {
                statusText.text = "Lendo..."
                delay(1000) 
                
                // Simulação para testar overlay
                resultText.text = "R$ 25,00 - 10km"
                
                statusText.text = "Dormindo..."
                delay(5000)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        if (::overlayView.isInitialized) windowManager.removeView(overlayView)
        mediaProjection?.stop()
    }
}
"""

print("--- Corrigindo erro de digitação no OcrService ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nArquivo corrigido.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Fix: Typo OcrService'")
print("3. git push")


