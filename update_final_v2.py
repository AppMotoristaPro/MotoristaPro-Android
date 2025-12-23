import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Compacto, Somatório e Invisível) ---
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

class OcrService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var rootLayout: LinearLayout
    
    // UI Elements
    private lateinit var tvResumo: TextView // "R$ 20,00 (10km 20min)"
    private lateinit var tvCalculos: TextView // "Km: R$ 2,00 | H: R$ 60"

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    
    // Controle de Visibilidade
    private var lastDetectionTime = 0L
    private val HIDE_TIMEOUT = 5000L // Some após 5s sem detectar corrida

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        try {
            startForegroundServiceCompat()
            setupCompactOverlay()
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
            .setContentText("Monitorando em segundo plano...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    private fun setupCompactOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- LAYOUT COMPACTO ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(20, 15, 20, 15) // Padding reduzido
            visibility = View.GONE // COMEÇA INVISÍVEL
            
            // Fundo Compacto e Arredondado
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#1E293B")) // Slate 800
                cornerRadius = 25f
                setStroke(2, Color.parseColor("#475569"))
            }
        }

        // Linha 1: Resumo (Preço + Dados Brutos)
        tvResumo = TextView(this).apply {
            text = "Analisando..."
            textSize = 14f
            setTextColor(Color.WHITE)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        // Linha 2: Cálculos (O que importa)
        tvCalculos = TextView(this).apply {
            text = "--"
            textSize = 12f
            setTextColor(Color.parseColor("#94A3B8")) // Cinza
            gravity = Gravity.CENTER
            setPadding(0, 5, 0, 0)
        }

        rootLayout.addView(tvResumo)
        rootLayout.addView(tvCalculos)

        // Params Ajustados para ser pequeno
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 80 // Bem no topo

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
            
            // Baixa resolução para performance
            screenWidth = metrics.widthPixels / 2
            screenHeight = metrics.heightPixels / 2
            val screenDensity = metrics.densityDpi

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
        } catch (e: Exception) {
            stopSelf()
        }
    }

    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isRunning) {
                // Check de visibilidade (Auto-Hide)
                if (System.currentTimeMillis() - lastDetectionTime > HIDE_TIMEOUT) {
                    updateVisibility(false)
                }

                var image = try { imageReader?.acquireLatestImage() } catch (e: Exception) { null }

                if (image != null) {
                    try {
                        val planes = image.planes
                        val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride
                        val rowStride = planes[0].rowStride
                        val rowPadding = rowStride - pixelStride * screenWidth
                        
                        val bitmap = Bitmap.createBitmap(screenWidth + rowPadding / pixelStride, screenHeight, Bitmap.Config.ARGB_8888)
                        bitmap.copyPixelsFromBuffer(buffer)
                        
                        val cleanBitmap = if (rowPadding == 0) bitmap else Bitmap.createBitmap(bitmap, 0, 0, screenWidth, screenHeight)
                        image.close() 

                        val inputImage = InputImage.fromBitmap(cleanBitmap, 0)
                        
                        recognizer.process(inputImage)
                            .addOnSuccessListener { visionText -> processAndSumText(visionText.text) }
                            .addOnFailureListener { }

                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }
                
                // Intervalo de leitura (reduzido para 2s para detectar rápido, o Auto-Hide cuida do spam)
                delay(2000) 
            }
        }
    }

    private fun processAndSumText(rawText: String) {
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        // Regex Ajustada
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        // Variáveis de Soma
        var totalPrice = 0.0
        var totalDist = 0.0
        var totalTime = 0.0

        // 1. Achar o maior preço (normalmente o preço final é o maior valor monetário na tela)
        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > totalPrice) totalPrice = v // Assume o maior valor como o preço da corrida
        }

        // 2. Somar TODAS as distâncias encontradas (ex: 2km até passageiro + 10km destino)
        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            totalDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        // 3. Somar TODOS os tempos
        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            totalTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // Lógica de Exibição
        if (totalPrice > 0.0 && (totalDist > 0.0 || totalTime > 0.0)) {
            // Corrida Detectada!
            lastDetectionTime = System.currentTimeMillis()
            
            val valPerKm = if (totalDist > 0) totalPrice / totalDist else 0.0
            val valPerHour = if (totalTime > 0) (totalPrice / totalTime) * 60 else 0.0
            
            updateUI(totalPrice, totalDist, totalTime, valPerKm, valPerHour)
            updateVisibility(true)
        }
    }

    private fun updateVisibility(visible: Boolean) {
        Handler(Looper.getMainLooper()).post {
            try {
                if (visible) {
                    if (rootLayout.visibility != View.VISIBLE) rootLayout.visibility = View.VISIBLE
                } else {
                    if (rootLayout.visibility != View.GONE) rootLayout.visibility = View.GONE
                }
            } catch (e: Exception) {}
        }
    }

    private fun updateUI(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            // Texto Compacto: "R$ 20.50 (12km 25min)"
            tvResumo.text = String.format("R$ %.2f  (%.1fkm %.0fmin)", price, dist, time)
            
            // Texto Cálculos: "Km: 1.80 | H: 50.00"
            tvCalculos.text = String.format("Km: R$ %.2f   H: R$ %.2f", valKm, valHora)
            
            // Cor baseada na qualidade (R$ 2.00/km meta)
            val color = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") // Verde
                valKm >= 1.5 -> Color.parseColor("#FACC15") // Amarelo
                else -> Color.parseColor("#F87171") // Vermelho
            }
            tvResumo.setTextColor(color)
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

print("--- UI StopClub (Soma, Compacto, Auto-Hide) ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Feature: Multi-stop Sum and AutoHide'")
print("3. git push")


