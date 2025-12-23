import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Lógica Flash & UI Compacta) ---
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
    private lateinit var tvValorPrincipal: TextView
    private lateinit var tvDetalhes: TextView
    private lateinit var tvResultados: TextView

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    
    // Controle de Estado da Corrida
    private var lastPrice = 0.0
    private var lastDist = 0.0
    private var lastTime = 0.0
    
    // Controle de Loop
    private var isPausedForCooldown = false

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

    private fun setupCompactOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- CARD SUPER COMPACTO ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(25, 15, 25, 15) // Padding reduzido pela metade
            visibility = View.GONE // Começa invisível
            
            // Glass Escuro e Redondo
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#F2111827")) // Quase 100% opaco
                cornerRadius = 35f
                setStroke(2, Color.parseColor("#33FFFFFF"))
            }
        }

        // 1. TOPO: Valor (Fonte 22)
        tvValorPrincipal = TextView(this).apply {
            text = "R$ --"
            textSize = 22f
            setTextColor(Color.parseColor("#4ADE80")) // Verde
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setShadowLayer(5f, 0f, 0f, Color.BLACK)
        }

        // 2. MEIO: Detalhes (Fonte 12)
        tvDetalhes = TextView(this).apply {
            text = "-- km • -- min"
            textSize = 12f
            setTextColor(Color.LTGRAY)
            gravity = Gravity.CENTER
            setPadding(0, 2, 0, 8)
        }

        // 3. BASE: Cálculos em uma linha só (Fonte 14)
        tvResultados = TextView(this).apply {
            text = "Km: R$ --  |  H: R$ --"
            textSize = 14f
            setTextColor(Color.WHITE)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        rootLayout.addView(tvValorPrincipal)
        rootLayout.addView(tvDetalhes)
        rootLayout.addView(getDivider())
        rootLayout.addView(tvResultados)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 100 

        try {
            windowManager.addView(rootLayout, params)
        } catch (e: Exception) {
            Log.e("Overlay", "Erro", e)
        }
    }

    private fun getDivider(): View {
        return View(this).apply {
            layoutParams = LinearLayout.LayoutParams(100, 1).apply { // Linha curta centralizada
                gravity = Gravity.CENTER
                setMargins(0, 0, 0, 5)
            }
            setBackgroundColor(Color.parseColor("#44FFFFFF"))
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
                if (isPausedForCooldown) {
                    delay(100)
                    continue
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
                            .addOnSuccessListener { visionText -> analyzeScreen(visionText.text) }
                            .addOnFailureListener { }

                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }
                
                delay(1000) // Leitura rápida
            }
        }
    }

    private fun analyzeScreen(rawText: String) {
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        var currentMaxPrice = 0.0
        var currentTotalDist = 0.0
        var currentTotalTime = 0.0

        // Soma valores
        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > currentMaxPrice) currentMaxPrice = v
        }

        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            currentTotalDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            currentTotalTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // --- LÓGICA DE EXIBIÇÃO INTELIGENTE ---
        if (currentMaxPrice > 0.0 && (currentTotalDist > 0.0 || currentTotalTime > 0.0)) {
            
            // Verifica se é uma NOVA corrida (valores diferentes da última lida)
            if (isDifferentFromLast(currentMaxPrice, currentTotalDist, currentTotalTime)) {
                
                // Atualiza Memória
                lastPrice = currentMaxPrice
                lastDist = currentTotalDist
                lastTime = currentTotalTime
                
                val valPerKm = if (currentTotalDist > 0) currentMaxPrice / currentTotalDist else 0.0
                val valPerHour = if (currentTotalTime > 0) (currentMaxPrice / currentTotalTime) * 60 else 0.0
                
                // MOSTRA JANELA
                updateWindow(true, currentMaxPrice, currentTotalDist, currentTotalTime, valPerKm, valPerHour)
                
                // ATIVA PAUSA DE 5s (Janela visível)
                triggerCooldown()
            } else {
                // É a MESMA corrida que já mostramos e já passou os 5s.
                // O usuário pediu para NÃO exibir se for igual.
                updateWindow(false, 0.0, 0.0, 0.0, 0.0, 0.0)
            }
        } else {
            // Não achou nada (Mapa/Menu) -> Reseta memória para próxima ser considerada "Nova"
            lastPrice = 0.0
            lastDist = 0.0
            lastTime = 0.0
            updateWindow(false, 0.0, 0.0, 0.0, 0.0, 0.0)
        }
    }

    private fun isDifferentFromLast(p: Double, d: Double, t: Double): Boolean {
        // Tolerância pequena para erros de OCR (ex: 10.1km vs 10.0km)
        return (kotlin.math.abs(p - lastPrice) > 0.1 || 
                kotlin.math.abs(d - lastDist) > 0.5 || 
                kotlin.math.abs(t - lastTime) > 1.0)
    }

    private fun triggerCooldown() {
        scope.launch {
            isPausedForCooldown = true
            delay(5000) // Janela fica na tela por 5s
            isPausedForCooldown = false
            // Ao acordar, o loop vai ler de novo. 
            // Se for igual -> cai no else do analyzeScreen -> Esconde.
            // Se mudou -> cai no if -> Atualiza e espera mais 5s.
        }
    }

    private fun updateWindow(visible: Boolean, price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            if (!visible) {
                if (rootLayout.visibility == View.VISIBLE) rootLayout.visibility = View.GONE
                return@post
            }

            if (rootLayout.visibility == View.GONE) rootLayout.visibility = View.VISIBLE

            // Formatação Compacta
            tvValorPrincipal.text = String.format("R$ %.2f", price)
            tvDetalhes.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvResultados.text = String.format("Km: R$ %.2f   H: R$ %.0f", valKm, valHora)

            // Cores
            val kmColor = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") // Verde
                valKm >= 1.5 -> Color.parseColor("#FACC15") // Amarelo
                else -> Color.parseColor("#F87171") // Vermelho
            }
            tvResultados.setTextColor(kmColor)
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

print("--- Aplicando Lógica Flash e UI Compacta ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Fix: Smart Flash Logic and Tiny Card'")
print("3. git push")


