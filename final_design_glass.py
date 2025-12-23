import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Design Glass + Lógica Inteligente) ---
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
    
    // UI Elements da Hierarquia
    private lateinit var tvValorPrincipal: TextView // R$ 00,00
    private lateinit var tvDadosBrutos: TextView    // 10km • 20min
    private lateinit var layoutResultados: LinearLayout
    private lateinit var tvResKm: TextView          // R$ 2,00/km
    private lateinit var tvResHora: TextView        // R$ 60,00/h

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    
    // Controle de Loop
    private var isPausedForCooldown = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        try {
            startForegroundServiceCompat()
            setupGlassOverlay()
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
            .setContentText("Monitorando tela...")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    private fun setupGlassOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- CONTAINER GLASS ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 30, 40, 30)
            visibility = View.GONE // Começa invisível
            
            // Fundo Efeito Vidro Escuro
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#EE111827")) // Cinza/Azul Quase Preto (Alta Opacidade para leitura)
                cornerRadius = 40f
                setStroke(3, Color.parseColor("#44FFFFFF")) // Borda branca translúcida (Glass Effect)
            }
        }

        // 1. TOPO: Valor da Corrida (Gigante)
        tvValorPrincipal = TextView(this).apply {
            text = "R$ --,--"
            textSize = 28f
            setTextColor(Color.parseColor("#4ADE80")) // Verde Neon
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setShadowLayer(10f, 0f, 0f, Color.BLACK) // Sombra para destaque
        }

        // 2. MEIO: Soma de KM e Minutos
        tvDadosBrutos = TextView(this).apply {
            text = "-- km  •  -- min"
            textSize = 14f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setPadding(0, 5, 0, 20) // Espaço abaixo
        }

        // 3. BASE: Grid de Resultados (R$/km e R$/h)
        layoutResultados = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            weightSum = 2f
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)
        }

        // Coluna Esquerda (KM)
        val colKm = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val labelKm = TextView(this).apply { text = "R$/KM"; textSize = 10f; setTextColor(Color.LTGRAY) }
        tvResKm = TextView(this).apply { text = "--"; textSize = 18f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD }
        colKm.addView(labelKm); colKm.addView(tvResKm)

        // Coluna Direita (Hora)
        val colHora = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val labelHora = TextView(this).apply { text = "R$/HORA"; textSize = 10f; setTextColor(Color.LTGRAY) }
        tvResHora = TextView(this).apply { text = "--"; textSize = 18f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD }
        colHora.addView(labelHora); colHora.addView(tvResHora)

        layoutResultados.addView(colKm)
        layoutResultados.addView(colHora)

        // Adiciona tudo ao root
        rootLayout.addView(tvValorPrincipal)
        rootLayout.addView(tvDadosBrutos)
        rootLayout.addView(getDivider())
        rootLayout.addView(layoutResultados)

        // Layout Params (Topo Centralizado)
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 120 // Margem do topo

        try {
            windowManager.addView(rootLayout, params)
        } catch (e: Exception) {
            Log.e("Overlay", "Erro", e)
        }
    }

    private fun getDivider(): View {
        return View(this).apply {
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1).apply {
                setMargins(20, 0, 20, 15)
            }
            setBackgroundColor(Color.parseColor("#33FFFFFF")) // Linha fina
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
                // Se estivermos em cooldown visual, não processamos imagem, mas mantemos o loop vivo
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
                
                // Leitura rápida (1s) quando está buscando. 
                // Se achar, o analyzeScreen ativa o cooldown de 5s.
                delay(1000) 
            }
        }
    }

    private fun analyzeScreen(rawText: String) {
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        // --- 1. EXTRAÇÃO E SOMA ---
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        var maxPrice = 0.0
        var totalDist = 0.0
        var totalTime = 0.0

        // Pega o maior preço (assumindo ser o total da corrida)
        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > maxPrice) maxPrice = v
        }

        // Soma todas as distâncias
        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            totalDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        // Soma todos os tempos
        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            totalTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // --- 2. LÓGICA DE DECISÃO ---
        if (maxPrice > 0.0 && (totalDist > 0.0 || totalTime > 0.0)) {
            // ACHOU CORRIDA!
            val valPerKm = if (totalDist > 0) maxPrice / totalDist else 0.0
            val valPerHour = if (totalTime > 0) (maxPrice / totalTime) * 60 else 0.0
            
            // Atualiza UI
            updateWindow(true, maxPrice, totalDist, totalTime, valPerKm, valPerHour)
            
            // Ativa Cooldown: Janela fica visível por 5s sem ler nada novo
            triggerCooldown() 
        } else {
            // NÃO ACHOU NADA (Tela de mapa, menu, etc)
            // Fecha a janela imediatamente para não atrapalhar
            updateWindow(false, 0.0, 0.0, 0.0, 0.0, 0.0)
        }
    }

    private fun triggerCooldown() {
        scope.launch {
            isPausedForCooldown = true
            delay(5000) // Aguarda 5 segundos com a janela visível
            isPausedForCooldown = false
            // Após 5s, o loop volta a ler. Se a corrida sumiu, a janela fecha no próximo segundo.
        }
    }

    private fun updateWindow(visible: Boolean, price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            if (!visible) {
                if (rootLayout.visibility == View.VISIBLE) rootLayout.visibility = View.GONE
                return@post
            }

            if (rootLayout.visibility == View.GONE) rootLayout.visibility = View.VISIBLE

            // Formatação
            tvValorPrincipal.text = String.format("R$ %.2f", price)
            tvDadosBrutos.text = String.format("%.1f km  •  %.0f min", dist, time)
            
            tvResKm.text = String.format("%.2f", valKm)
            tvResHora.text = String.format("%.0f", valHora)

            // Cores Dinâmicas
            val kmColor = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") // Verde
                valKm >= 1.5 -> Color.parseColor("#FACC15") // Amarelo
                else -> Color.parseColor("#F87171") // Vermelho
            }
            tvResKm.setTextColor(kmColor)
            
            val horaColor = when {
                valHora >= 60.0 -> Color.parseColor("#4ADE80")
                valHora >= 40.0 -> Color.parseColor("#FACC15")
                else -> Color.parseColor("#F87171")
            }
            tvResHora.setTextColor(horaColor)
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

print("--- Implementando Design Glass e Lógica Inteligente ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'UI: Glass Effect and Smart Loop'")
print("3. git push")


