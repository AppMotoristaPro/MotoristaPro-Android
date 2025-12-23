import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE COM NOVA UI MODERNA ---
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
import android.widget.Button
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
    
    // Elementos da UI
    private lateinit var tvPreco: TextView
    private lateinit var tvDetalhesCorrida: TextView // KM e Min
    private lateinit var tvGanhoKm: TextView
    private lateinit var tvGanhoHora: TextView
    private lateinit var tvStatus: TextView

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
            setupModernOverlay()
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
            .setContentText("Assistente Ativo")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    private fun setupModernOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- CONTAINER PRINCIPAL (CARD) ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(30, 30, 30, 30)
            
            // Fundo Arredondado Cinza Escuro/Azulado Moderno
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#1E293B")) // Slate 800
                cornerRadius = 30f
                setStroke(2, Color.parseColor("#334155")) // Borda sutil
            }
        }

        // --- LINHA DO CABEÇALHO (PREÇO + FECHAR) ---
        val headerLayout = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }

        tvPreco = TextView(this).apply {
            text = "R$ --,--"
            textSize = 24f
            setTextColor(Color.parseColor("#4ADE80")) // Verde Neon
            typeface = Typeface.DEFAULT_BOLD
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }

        val btnClose = Button(this).apply {
            text = "X"
            textSize = 14f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.TRANSPARENT)
            setPadding(0,0,0,0)
            layoutParams = LinearLayout.LayoutParams(80, 80)
            setOnClickListener { stopSelf() }
        }

        headerLayout.addView(tvPreco)
        headerLayout.addView(btnClose)

        // --- DETALHES GERAIS (KM e MIN) ---
        tvDetalhesCorrida = TextView(this).apply {
            text = "-- km  •  -- min"
            textSize = 14f
            setTextColor(Color.parseColor("#CBD5E1")) // Cinza claro
            setPadding(0, 5, 0, 15)
        }

        // --- GRID DE CÁLCULOS (GANHO/KM e GANHO/H) ---
        val statsLayout = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            weightSum = 2f
        }

        // Coluna 1: R$/KM
        val colKm = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val lblKm = TextView(this).apply { text = "Valor por KM"; textSize = 10f; setTextColor(Color.GRAY) }
        tvGanhoKm = TextView(this).apply { 
            text = "R$ --"; textSize = 16f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD 
        }
        colKm.addView(lblKm); colKm.addView(tvGanhoKm)

        // Coluna 2: R$/Hora
        val colHora = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            gravity = Gravity.END // Alinha à direita
        }
        val lblHora = TextView(this).apply { text = "Valor por Hora"; textSize = 10f; setTextColor(Color.GRAY); gravity = Gravity.END }
        tvGanhoHora = TextView(this).apply { 
            text = "R$ --"; textSize = 16f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.END
        }
        colHora.addView(lblHora); colHora.addView(tvGanhoHora)

        statsLayout.addView(colKm)
        statsLayout.addView(colHora)

        // --- BARRA DE STATUS INFERIOR ---
        tvStatus = TextView(this).apply {
            text = "Aguardando leitura..."
            textSize = 10f
            setTextColor(Color.parseColor("#64748B")) // Slate 500
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 15, 0, 0)
        }

        // Montagem final
        rootLayout.addView(headerLayout)
        rootLayout.addView(tvDetalhesCorrida)
        rootLayout.addView(getDivider()) // Linha divisória
        rootLayout.addView(statsLayout)
        rootLayout.addView(tvStatus)

        // Params da Janela
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT, // Ocupa largura (respeitando margem do layout)
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 50 // Margem superior
        
        // Ajuste de largura para nao ocupar 100% da tela (estilo Card)
        params.width = (resources.displayMetrics.widthPixels * 0.95).toInt()

        try {
            windowManager.addView(rootLayout, params)
        } catch (e: Exception) {
            Log.e("Overlay", "Erro", e)
        }
    }

    private fun getDivider(): View {
        return View(this).apply {
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 2).apply {
                setMargins(0, 10, 0, 10)
            }
            setBackgroundColor(Color.parseColor("#334155"))
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
            screenDensity = metrics.densityDpi

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
                            .addOnSuccessListener { visionText -> processFullText(visionText.text) }
                            .addOnFailureListener { }

                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }
                delay(2000)
            }
        }
    }

    private fun processFullText(rawText: String) {
        // Limpeza básica
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        // Regex Otimizada
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        var price = 0.0
        var dist = 0.0
        var time = 0.0

        val priceMatcher = pricePattern.matcher(cleanText)
        if (priceMatcher.find()) price = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0

        val distMatcher = distPattern.matcher(cleanText)
        if (distMatcher.find()) dist = distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0

        val timeMatcher = timePattern.matcher(cleanText)
        if (timeMatcher.find()) time = timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0

        if (price > 0.0 && (dist > 0.0 || time > 0.0)) {
            val valPerKm = if (dist > 0) price / dist else 0.0
            val valPerHour = if (time > 0) (price / time) * 60 else 0.0
            
            updateUI(price, dist, time, valPerKm, valPerHour)
        } else {
            // Pode adicionar lógica para "limpar" a tela se ficar mto tempo sem ler nada
        }
    }

    private fun updateUI(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            // Atualiza Valores Principais
            tvPreco.text = String.format("R$ %.2f", price)
            tvDetalhesCorrida.text = String.format("%.1f km  •  %.0f min", dist, time)
            
            tvGanhoKm.text = String.format("R$ %.2f", valKm)
            tvGanhoHora.text = String.format("R$ %.2f", valHora)
            
            // Lógica de Cores (Gamification)
            // KM: Verde > 2.0, Amarelo > 1.5, Vermelho < 1.5
            val kmColor = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") // Green 400
                valKm >= 1.5 -> Color.parseColor("#FACC15") // Yellow 400
                else -> Color.parseColor("#F87171") // Red 400
            }
            tvGanhoKm.setTextColor(kmColor)

            // Hora: Verde > 60, Amarelo > 40, Vermelho < 40
            val horaColor = when {
                valHora >= 60.0 -> Color.parseColor("#4ADE80")
                valHora >= 40.0 -> Color.parseColor("#FACC15")
                else -> Color.parseColor("#F87171")
            }
            tvGanhoHora.setTextColor(horaColor)

            tvStatus.text = "Dados atualizados"
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

print("--- UI Redesenhada: Card Moderno ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'UI: Card Moderno e Formatado'")
print("3. git push")


