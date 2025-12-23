import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Corte Ajustado para 10%) ---
ocr_service_content = """
package com.motoristapro.android

import android.app.*
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
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
import android.view.View
import android.view.WindowManager
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.app.NotificationCompat
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.*
import java.util.regex.Pattern
import kotlin.math.abs

class OcrService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var rootLayout: LinearLayout
    
    // UI Elements
    private lateinit var tvValorTopo: TextView
    private lateinit var tvDadosMeio: TextView
    private lateinit var tvResultadosBaixo: TextView

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    
    // Memória Anti-Spam
    private var lastPrice = 0.0
    private var lastDist = 0.0
    private var sameFrameCount = 0

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        try {
            startForegroundServiceCompat()
            setupMiniGlassOverlay()
        } catch (e: Exception) {
            Log.e("OCR", "Erro Fatal", e)
        }
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro")
            .setContentText("Monitorando...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    private fun setupMiniGlassOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(25, 15, 25, 15)
            visibility = View.GONE 
            
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#F20F172A")) 
                cornerRadius = 30f
                setStroke(1, Color.parseColor("#33FFFFFF")) 
            }
        }

        tvValorTopo = TextView(this).apply {
            text = "R$ --"
            textSize = 20f 
            setTextColor(Color.parseColor("#4ADE80")) 
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setShadowLayer(5f, 0f, 0f, Color.BLACK)
        }

        tvDadosMeio = TextView(this).apply {
            text = "-- km • -- min"
            textSize = 12f
            setTextColor(Color.LTGRAY)
            gravity = Gravity.CENTER
            setPadding(0, 2, 0, 5)
        }

        tvResultadosBaixo = TextView(this).apply {
            text = "R$ --/km • R$ --/h"
            textSize = 14f
            setTextColor(Color.WHITE)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        rootLayout.addView(tvValorTopo)
        rootLayout.addView(tvDadosMeio)
        rootLayout.addView(tvResultadosBaixo)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 80 

        try {
            windowManager.addView(rootLayout, params)
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
            
            mediaProjection?.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() { super.onStop(); stopSelf() }
            }, Handler(Looper.getMainLooper()))
            
            val metrics = DisplayMetrics()
            windowManager.defaultDisplay.getMetrics(metrics)
            
            screenWidth = metrics.widthPixels / 2
            screenHeight = metrics.heightPixels / 2
            
            imageReader = ImageReader.newInstance(screenWidth, screenHeight, PixelFormat.RGBA_8888, 2)
            
            virtualDisplay = mediaProjection?.createVirtualDisplay(
                "ScreenCapture",
                screenWidth,
                screenHeight,
                metrics.densityDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader?.surface,
                null,
                null
            )
            
            isRunning = true
            startOcrLoop()
        } catch (e: Exception) {
            stopSelf()
        }
    }

    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isRunning) {
                var image = try { imageReader?.acquireLatestImage() } catch (e: Exception) { null }
                var shouldWait = false

                if (image != null) {
                    try {
                        val planes = image.planes
                        val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride
                        val rowStride = planes[0].rowStride
                        val rowPadding = rowStride - pixelStride * screenWidth
                        
                        val fullBitmap = Bitmap.createBitmap(screenWidth + rowPadding / pixelStride, screenHeight, Bitmap.Config.ARGB_8888)
                        fullBitmap.copyPixelsFromBuffer(buffer)
                        image.close() 

                        // --- CORTE AJUSTADO: 10% ---
                        // Ignora apenas os 10% superiores da tela.
                        // A janela flutuante deve estar posicionada DENTRO desses 10% (y=80)
                        // para não ser lida.
                        val cropY = (screenHeight * 0.10).toInt()
                        val cropHeight = screenHeight - cropY
                        
                        if (cropHeight > 0 && cropY < fullBitmap.height) {
                            val croppedBitmap = Bitmap.createBitmap(fullBitmap, 0, cropY, screenWidth, cropHeight)
                            val inputImage = InputImage.fromBitmap(croppedBitmap, 0)
                            
                            val task = recognizer.process(inputImage)
                            while (!task.isComplete) { delay(50) }
                            
                            if (task.isSuccessful) {
                                shouldWait = analyzeScreen(task.result.text)
                            }
                        }
                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }

                if (shouldWait) {
                    delay(5000)
                } else {
                    delay(1000)
                }
            }
        }
    }

    private fun analyzeScreen(rawText: String): Boolean {
        var framePrice = 0.0
        var frameDist = 0.0
        var frameTime = 0.0

        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > framePrice) framePrice = v
        }

        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            frameDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            frameTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        if (framePrice > 0.0 && (frameDist > 0.0 || frameTime > 0.0)) {
            
            if (isSameAsLast(framePrice, frameDist)) {
                sameFrameCount++
                // Se viu a mesma coisa 2 vezes seguidas, é estático -> Fecha
                if (sameFrameCount >= 2) {
                    hideWindow()
                    return false
                }
                return true 
            } else {
                // É NOVO!
                sameFrameCount = 0
                lastPrice = framePrice
                lastDist = frameDist
                
                val valPerKm = if (frameDist > 0) framePrice / frameDist else 0.0
                val valPerHour = if (frameTime > 0) (framePrice / frameTime) * 60 else 0.0
                
                showWindow(framePrice, frameDist, frameTime, valPerKm, valPerHour)
                return true // Ativa delay 5s
            }
        } else {
            sameFrameCount = 0
            hideWindow()
            return false
        }
    }

    private fun isSameAsLast(p: Double, d: Double): Boolean {
        return (abs(p - lastPrice) < 0.1 && abs(d - lastDist) < 0.5)
    }

    private fun showWindow(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            if (rootLayout.visibility != View.VISIBLE) rootLayout.visibility = View.VISIBLE

            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.2f/h", valKm, valHora)

            val color = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") 
                valKm >= 1.5 -> Color.parseColor("#FACC15")
                else -> Color.parseColor("#F87171")
            }
            tvResultadosBaixo.setTextColor(color)
        }
    }

    private fun hideWindow() {
        Handler(Looper.getMainLooper()).post {
            if (rootLayout.visibility == View.VISIBLE) {
                rootLayout.visibility = View.GONE
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        try { if (::rootLayout.isInitialized) windowManager.removeView(rootLayout) } catch (e: Exception) {}
        try { virtualDisplay?.release() } catch (e: Exception) {}
        try { mediaProjection?.stop() } catch (e: Exception) {}
        try { recognizer.close() } catch (e: Exception) {}
    }
}
"""

print("--- Corte de Segurança: 10% ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Config: Crop 10 percent'")
print("3. git push")


