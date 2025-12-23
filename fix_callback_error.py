import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Com Callback Obrigatório) ---
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
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
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
        try {
            startForegroundServiceCompat()
            setupOverlay()
        } catch (e: Exception) {
            showToast("Erro Fatal: ${e.message}")
        }
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro")
            .setContentText("Lendo Tela...")
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
            setBackgroundColor(Color.BLUE) // Mantendo AZUL para teste visual
            setPadding(20, 20, 20, 20)
        }

        statusText = TextView(this).apply {
            text = "INICIANDO..."
            setTextColor(Color.WHITE)
            textSize = 14f
        }
        
        resultText = TextView(this).apply {
            text = "--"
            setTextColor(Color.YELLOW)
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
        }

        val closeBtn = Button(this).apply {
            text = "PARAR"
            setOnClickListener { stopSelf() }
        }

        overlayView.addView(statusText)
        overlayView.addView(resultText)
        overlayView.addView(closeBtn)

        val params = WindowManager.LayoutParams(
            600,
            600,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.CENTER

        try {
            windowManager.addView(overlayView, params)
        } catch (e: Exception) {
            showToast("Erro Janela: ${e.message}")
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
            
            // CORREÇÃO CRÍTICA: Registrar Callback ANTES de criar o VirtualDisplay
            // Isso é obrigatório no Android 14+
            mediaProjection?.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() {
                    super.onStop()
                    stopSelf()
                }
            }, Handler(Looper.getMainLooper()))
            
            val metrics = DisplayMetrics()
            windowManager.defaultDisplay.getMetrics(metrics)
            
            screenWidth = metrics.widthPixels
            screenHeight = metrics.heightPixels
            screenDensity = metrics.densityDpi

            // Usando resolução nativa para garantir compatibilidade
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
            updateUI("Captura OK. Lendo...")
            startOcrLoop()
        } catch (e: Exception) {
            showToast("Erro SetupMP: ${e.message}")
            updateUI("Erro SetupMP: ${e.message}")
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
                        
                        val bitmap = Bitmap.createBitmap(
                            screenWidth + rowPadding / pixelStride,
                            screenHeight,
                            Bitmap.Config.ARGB_8888
                        )
                        bitmap.copyPixelsFromBuffer(buffer)
                        
                        val cleanBitmap = if (rowPadding == 0) bitmap else 
                            Bitmap.createBitmap(bitmap, 0, 0, screenWidth, screenHeight)

                        image.close() 

                        val inputImage = InputImage.fromBitmap(cleanBitmap, 0)
                        
                        recognizer.process(inputImage)
                            .addOnSuccessListener { visionText ->
                                processText(visionText.text)
                            }
                            .addOnFailureListener {
                                updateUI("Erro ML")
                            }

                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }
                delay(2000)
            }
        }
    }

    private fun processText(rawText: String) {
        // Regex simplificada para teste
        // Procura qualquer formato monetário
        val pricePattern = Pattern.compile("R\\\\$\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val matcher = pricePattern.matcher(rawText)
        
        if (matcher.find()) {
            val valor = matcher.group(1)
            updateUI("ACHEI: R$ $valor")
        } else {
            // Mostra os primeiros 30 caracteres lidos para debug
            val sample = rawText.replace("\\n", " ").take(30)
            updateUI("Lendo: $sample...")
        }
    }

    private fun updateUI(msg: String) {
        Handler(Looper.getMainLooper()).post {
            resultText.text = msg
        }
    }
    
    private fun showToast(msg: String) {
        Handler(Looper.getMainLooper()).post {
            Toast.makeText(applicationContext, msg, Toast.LENGTH_LONG).show()
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

print("--- Adicionando Callback Obrigatório ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Fix: Register MediaProjection Callback'")
print("3. git push")


