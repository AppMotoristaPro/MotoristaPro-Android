package com.motoristapro.android

import android.app.*
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
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
        startForegroundService()
        setupOverlay()
    }

    private fun startForegroundService() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro")
            .setContentText("Monitorando tela...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .build()

        startForeground(1, notification)
    }

    private fun setupOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        overlayView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#E6000000"))
            setPadding(30, 30, 30, 30)
        }

        statusText = TextView(this).apply {
            text = "Iniciando..."
            setTextColor(Color.LTGRAY)
            textSize = 12f
        }
        
        resultText = TextView(this).apply {
            text = "--"
            setTextColor(Color.GREEN)
            textSize = 18f
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

        windowManager.addView(overlayView, params)
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
        val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjection = mpManager.getMediaProjection(code, data)
        
        val metrics = DisplayMetrics()
        windowManager.defaultDisplay.getMetrics(metrics)
        screenWidth = metrics.widthPixels
        screenHeight = metrics.heightPixels
        screenDensity = metrics.densityDpi

        // ImageReader com tamanho fixo seguro ou nativo
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
        startOcrLoop()
    }

    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isRunning) {
                try {
                    val image = imageReader?.acquireLatestImage()
                    if (image != null) {
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
                        image.close()

                        val inputImage = InputImage.fromBitmap(bitmap, 0)
                        
                        recognizer.process(inputImage)
                            .addOnSuccessListener { visionText ->
                                processExtractedText(visionText.text)
                            }
                            .addOnFailureListener { e ->
                                updateStatus("Erro OCR: ${e.message}")
                            }
                    } else {
                        withContext(Dispatchers.Main) {
                            statusText.text = "Aguardando tela..."
                        }
                    }
                } catch (e: Exception) {
                    Log.e("OCR", "Erro no loop", e)
                }

                delay(5000)
            }
        }
    }

    private fun processExtractedText(rawText: String) {
        // Regex corrigidas com escape duplo para Python escrever corretamente no Kotlin
        val pricePattern = Pattern.compile("R\\$\\s*([0-9]+[.,][0-9]{2})")
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\s*km", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\s*min", Pattern.CASE_INSENSITIVE)

        var price = 0.0
        var dist = 0.0
        var time = 0.0

        val priceMatcher = pricePattern.matcher(rawText)
        if (priceMatcher.find()) {
            price = priceMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val distMatcher = distPattern.matcher(rawText)
        if (distMatcher.find()) {
            dist = distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val timeMatcher = timePattern.matcher(rawText)
        if (timeMatcher.find()) {
            time = timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // String Format corrigido com escape duplo de nova linha
        val resultString = if (price > 0 && (dist > 0 || time > 0)) {
            val valPerKm = if (dist > 0) price / dist else 0.0
            val valPerHour = if (time > 0) (price / time) * 60 else 0.0
            
            String.format("R$ %.2f | %.1f km | %.0f min\nKm: R$ %.2f\nHora: R$ %.2f", 
                price, dist, time, valPerKm, valPerHour)
        } else {
            "Buscando..."
        }

        updateUI(resultString)
    }

    private fun updateStatus(msg: String) {
        Handler(Looper.getMainLooper()).post {
            statusText.text = msg
        }
    }

    private fun updateUI(result: String) {
        Handler(Looper.getMainLooper()).post {
            statusText.text = "Lendo (Próx em 5s)..."
            resultText.text = result
            
            if (result.contains("Km: R$") && result.contains("Hora: R$")) {
                 resultText.setTextColor(Color.GREEN)
            } else {
                 resultText.setTextColor(Color.WHITE)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        if (::overlayView.isInitialized) windowManager.removeView(overlayView)
        virtualDisplay?.release()
        mediaProjection?.stop()
        recognizer.close()
    }
}