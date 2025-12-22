import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE COM DEBUG VISUAL E REGEX MELHORADA ---
ocr_service_content = """
package com.motoristapro.android

import android.app.*
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.DisplayMetrics
import android.util.Log
import android.view.Gravity
import android.view.WindowManager
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.app.NotificationCompat
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.*
import java.util.regex.Pattern

class OcrService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var overlayView: LinearLayout
    private lateinit var statusText: TextView
    private lateinit var resultText: TextView

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    private var screenDensity = 0

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForegroundServiceCompat()
        setupOverlay()
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro")
            .setContentText("Lendo tela...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    private fun setupOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        overlayView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#E6000000"))
            setPadding(20, 20, 20, 20)
        }

        statusText = TextView(this).apply {
            text = "Iniciando..."
            setTextColor(Color.YELLOW)
            textSize = 12f
        }
        
        resultText = TextView(this).apply {
            text = "--"
            setTextColor(Color.WHITE)
            textSize = 14f // Fonte um pouco menor para caber msg de erro
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
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 150

        try {
            windowManager.addView(overlayView, params)
        } catch (e: Exception) {
            Log.e("Overlay", "Erro", e)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val resultCode = intent?.getIntExtra("RESULT_CODE", 0) ?: 0
        val resultData = intent?.getParcelableExtra<Intent>("RESULT_DATA")

        if (resultCode != 0 && resultData != null) {
            setupMediaProjection(resultCode, resultData)
        }
        return START_STICKY
    }

    private fun setupMediaProjection(code: Int, data: Intent) {
        try {
            val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
            mediaProjection = mpManager.getMediaProjection(code, data)
            
            val metrics = DisplayMetrics()
            windowManager.defaultDisplay.getMetrics(metrics)
            
            // Usar resolucao nativa mas com cuidado no ImageReader
            screenWidth = metrics.widthPixels
            screenHeight = metrics.heightPixels
            screenDensity = metrics.densityDpi

            // PixelFormat.RGBA_8888 é o padrão mais seguro
            imageReader = ImageReader.newInstance(screenWidth, screenHeight, PixelFormat.RGBA_8888, 2)
            
            virtualDisplay = mediaProjection?.createVirtualDisplay(
                "ScreenCapture",
                screenWidth,
                screenHeight,
                screenDensity,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader?.surface,
                null,
                null
            )
            
            isRunning = true
            updateStatus("Captura iniciada. Aguardando frame...")
            startOcrLoop()
        } catch (e: Exception) {
            updateStatus("Erro Setup: ${e.message}")
            stopSelf()
        }
    }

    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isRunning) {
                var image = try {
                    imageReader?.acquireLatestImage()
                } catch (e: Exception) { null }

                if (image != null) {
                    try {
                        val planes = image.planes
                        val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride
                        val rowStride = planes[0].rowStride
                        val rowPadding = rowStride - pixelStride * screenWidth
                        
                        // Criar bitmap com tratamento seguro de buffer
                        val bitmap = Bitmap.createBitmap(
                            screenWidth + rowPadding / pixelStride,
                            screenHeight,
                            Bitmap.Config.ARGB_8888
                        )
                        bitmap.copyPixelsFromBuffer(buffer)
                        
                        // Recortar apenas a área útil (remove padding lateral se houver)
                        val cleanBitmap = if (rowPadding == 0) bitmap else 
                            Bitmap.createBitmap(bitmap, 0, 0, screenWidth, screenHeight)

                        image.close() // Fechar imediatamente para liberar buffer

                        val inputImage = InputImage.fromBitmap(cleanBitmap, 0)
                        
                        // Processamento IA
                        recognizer.process(inputImage)
                            .addOnSuccessListener { visionText ->
                                val text = visionText.text
                                if (text.isEmpty()) {
                                    updateStatus("Tela lida: Sem texto")
                                } else {
                                    updateStatus("Analisando texto...")
                                    processExtractedText(text)
                                }
                            }
                            .addOnFailureListener { e ->
                                updateStatus("Erro ML Kit: ${e.message}")
                            }

                    } catch (e: Exception) {
                        updateStatus("Erro Buffer: ${e.message}")
                        try { image.close() } catch (x: Exception) {}
                    }
                } else {
                   // Frame nao disponivel ainda, normal no inicio
                }

                delay(3000) // Tenta a cada 3 segundos
            }
        }
    }

    private fun processExtractedText(rawText: String) {
        // Normaliza o texto para facilitar Regex (remove quebras de linha estranhas)
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        // Regex super permissiva
        // Aceita "R$", "RS", "$", com ou sem espaço
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        // Aceita "km", "xm", com espaço ou numeros colados
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        // Aceita "min"
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        var price = 0.0
        var dist = 0.0
        var time = 0.0

        val priceMatcher = pricePattern.matcher(cleanText)
        if (priceMatcher.find()) {
            price = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val distMatcher = distPattern.matcher(cleanText)
        if (distMatcher.find()) {
            dist = distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val timeMatcher = timePattern.matcher(cleanText)
        if (timeMatcher.find()) {
            time = timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // Debug na tela para o usuario ver o que esta sendo lido
        if (price > 0 || dist > 0) {
            val valPerKm = if (dist > 0) price / dist else 0.0
            val valPerHour = if (time > 0) (price / time) * 60 else 0.0
            
            val finalRes = String.format("R$ %.2f | %.1f km | %.0f min\\nKm: R$ %.2f | Hora: R$ %.2f", 
                price, dist, time, valPerKm, valPerHour)
            
            updateUI(finalRes, true)
        } else {
            // Mostra trecho do texto lido para debug
            val debugSample = if (cleanText.length > 20) cleanText.substring(0, 20) + "..." else cleanText
            updateUI("Nada detectado.\\nLido: $debugSample", false)
        }
    }

    private fun updateStatus(msg: String) {
        Handler(Looper.getMainLooper()).post {
            statusText.text = msg
        }
    }

    private fun updateUI(result: String, success: Boolean) {
        Handler(Looper.getMainLooper()).post {
            resultText.text = result
            if (success) {
                 statusText.text = "SUCESSO (Pausa 5s)"
                 resultText.setTextColor(Color.GREEN)
            } else {
                 statusText.text = "Tentando..."
                 resultText.setTextColor(Color.WHITE)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        try { if (::overlayView.isInitialized) windowManager.removeView(overlayView) } catch (e: Exception) {}
        try { virtualDisplay?.release() } catch (e: Exception) {}
        try { mediaProjection?.stop() } catch (e: Exception) {}
        try { recognizer.close() } catch (e: Exception) {}
    }
}
"""

print("--- Atualizando OCR com Debug Visual ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Fix: Debug OCR e Buffer'")
print("3. git push")


