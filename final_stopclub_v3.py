import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Lógica StopClub Real + UI Legível) ---
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
    private lateinit var tvValorGrande: TextView
    private lateinit var tvDadosSoma: TextView
    private lateinit var tvCalculos: TextView

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var hideJob: Job? = null
    
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    
    // Memória da última corrida mostrada
    private var lastShownPrice = 0.0
    private var lastShownDist = 0.0

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        try {
            startForegroundServiceCompat()
            setupBannerOverlay()
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

    private fun setupBannerOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- LAYOUT BANNER (Largura total, mas com margem) ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(30, 20, 30, 20)
            visibility = View.GONE // COMEÇA INVISÍVEL (Regra StopClub)
            
            // Fundo Preto/Azul Vidro (Legível)
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#F50F172A")) // Slate 900 (Quase 100% opaco)
                cornerRadius = 40f
                setStroke(3, Color.parseColor("#44FFFFFF")) // Borda Vidro
            }
        }

        // 1. TOPO: VALOR DA CORRIDA (Gigante e Centralizado)
        tvValorGrande = TextView(this).apply {
            text = "R$ --"
            textSize = 26f // Aumentado para ler fácil
            setTextColor(Color.parseColor("#4ADE80")) // Verde Neon
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setShadowLayer(10f, 0f, 0f, Color.BLACK)
        }

        // 2. MEIO: SOMA KM E MIN (Médio)
        tvDadosSoma = TextView(this).apply {
            text = "-- km • -- min"
            textSize = 16f // Aumentado
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setPadding(0, 5, 0, 10)
        }

        // 3. BASE: RESULTADOS DO CÁLCULO (Coloridos)
        tvCalculos = TextView(this).apply {
            text = "Km: R$ --  |  H: R$ --"
            textSize = 18f // Bem visível
            setTextColor(Color.LTGRAY)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        rootLayout.addView(tvValorGrande)
        rootLayout.addView(tvDadosSoma)
        rootLayout.addView(getDivider())
        rootLayout.addView(tvCalculos)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT, // Ocupa largura
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP
        params.y = 100 // Margem do topo para não cobrir relógio do sistema
        
        // Margens laterais falsas (ajustando a largura do layoutParams seria complexo no código puro, 
        // então confiamos no padding do rootLayout ou ajustamos a largura para 90%)
        params.width = (resources.displayMetrics.widthPixels * 0.92).toInt()

        try {
            windowManager.addView(rootLayout, params)
        } catch (e: Exception) {
            Log.e("Overlay", "Erro", e)
        }
    }

    private fun getDivider(): View {
        return View(this).apply {
            layoutParams = LinearLayout.LayoutParams(200, 2).apply {
                gravity = Gravity.CENTER
                setMargins(0, 0, 0, 10)
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
                // Captura e Processa
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
                
                // Intervalo de leitura (1.5s é um bom balanço entre rapidez e bateria)
                delay(1500) 
            }
        }
    }

    private fun analyzeScreen(rawText: String) {
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        // Regex robusta para pegar valores soltos
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        var foundPrice = 0.0
        var foundTotalDist = 0.0
        var foundTotalTime = 0.0

        // 1. Achar o PREÇO (Pega o MAIOR valor monetário da tela, pois geralmente é o total)
        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > foundPrice) foundPrice = v
        }

        // 2. Somar KMs
        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            foundTotalDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        // 3. Somar Minutos
        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            foundTotalTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // --- LÓGICA DE DECISÃO (CÉREBRO DO STOPCLUB) ---
        if (foundPrice > 0.0 && (foundTotalDist > 0.0 || foundTotalTime > 0.0)) {
            
            // É uma corrida DIFERENTE da última que mostramos?
            if (isDifferentRace(foundPrice, foundTotalDist)) {
                
                // Sim, é nova!
                lastShownPrice = foundPrice
                lastShownDist = foundTotalDist
                
                val valPerKm = if (foundTotalDist > 0) foundPrice / foundTotalDist else 0.0
                val valPerHour = if (foundTotalTime > 0) (foundPrice / foundTotalTime) * 60 else 0.0
                
                showBanner(foundPrice, foundTotalDist, foundTotalTime, valPerKm, valPerHour)
            } 
            // Se for IGUAL à última, não fazemos NADA (o timer de ocultar já está rodando ou já ocultou)
            
        } else {
            // Não achou nada na tela (Mapa, Menu, etc).
            // Não precisamos resetar 'lastShownPrice' imediatamente, 
            // pois se a mesma oferta piscar, não queremos spammar.
            // Mas se passar muito tempo, podemos resetar? 
            // Por enquanto, mantemos a lógica simples: Só mostra se mudar os valores.
        }
    }

    private fun isDifferentRace(p: Double, d: Double): Boolean {
        // Tolerância para evitar disparos falsos se o OCR ler "10.0" num frame e "10" no outro
        return (abs(p - lastShownPrice) > 0.1 || abs(d - lastShownDist) > 0.5)
    }

    private fun showBanner(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            // 1. Atualiza UI
            tvValorGrande.text = String.format("R$ %.2f", price)
            tvDadosSoma.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvCalculos.text = String.format("Km: R$ %.2f   H: R$ %.0f", valKm, valHora)

            val kmColor = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") // Verde
                valKm >= 1.5 -> Color.parseColor("#FACC15") // Amarelo
                else -> Color.parseColor("#F87171") // Vermelho
            }
            tvCalculos.setTextColor(kmColor)

            // 2. Torna Visível
            if (rootLayout.visibility != View.VISIBLE) {
                rootLayout.visibility = View.VISIBLE
            }

            // 3. Agenda o desaparecimento (Auto-Hide) em 5 segundos
            // Cancela agendamento anterior para não piscar
            hideJob?.cancel()
            hideJob = scope.launch {
                delay(5000)
                withContext(Dispatchers.Main) {
                    rootLayout.visibility = View.GONE
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        hideJob?.cancel()
        try { if (::rootLayout.isInitialized) windowManager.removeView(rootLayout) } catch (e: Exception) {}
        try { virtualDisplay?.release() } catch (e: Exception) {}
        try { mediaProjection?.stop() } catch (e: Exception) {}
        try { recognizer.close() } catch (e: Exception) {}
    }
}
"""

print("--- UI e Lógica Final: StopClub Clone ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Release: StopClub Logic V3'")
print("3. git push")


