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
    
    // Elementos da UI
    private lateinit var tvValorTopo: TextView      // R$ 20,00
    private lateinit var tvDadosMeio: TextView      // 10 km • 10 min
    private lateinit var tvResultadosBaixo: TextView // R$ 2,00/km • R$ 120,00/h

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        try {
            startForegroundServiceCompat()
            setupHierarchicalOverlay()
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

    private fun setupHierarchicalOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- CARD DE INFORMAÇÃO ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(30, 20, 30, 20)
            visibility = View.GONE // Invisível por padrão
            
            // Fundo Moderno Escuro
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#F2111827")) // Slate 900 (95% Opaco)
                cornerRadius = 35f
                setStroke(2, Color.parseColor("#33FFFFFF")) // Borda Vidro
            }
        }

        // 1. TOPO: VALOR DA CORRIDA (Gigante)
        tvValorTopo = TextView(this).apply {
            text = "R$ --"
            textSize = 28f 
            setTextColor(Color.parseColor("#4ADE80")) // Verde Neon
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setShadowLayer(8f, 0f, 0f, Color.BLACK)
        }

        // 2. MEIO: KM e MINUTOS (Pequeno)
        tvDadosMeio = TextView(this).apply {
            text = "-- km • -- min"
            textSize = 14f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setPadding(0, 2, 0, 10)
        }

        // Linha Divisória Sutil
        val divider = View(this).apply {
            layoutParams = LinearLayout.LayoutParams(150, 2).apply {
                gravity = Gravity.CENTER
                setMargins(0, 0, 0, 8)
            }
            setBackgroundColor(Color.parseColor("#33FFFFFF"))
        }

        // 3. BAIXO: RESULTADOS (Médio e Colorido)
        tvResultadosBaixo = TextView(this).apply {
            text = "R$ --/km • R$ --/h"
            textSize = 16f
            setTextColor(Color.LTGRAY)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        rootLayout.addView(tvValorTopo)
        rootLayout.addView(tvDadosMeio)
        rootLayout.addView(divider)
        rootLayout.addView(tvResultadosBaixo)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 100 
        
        // Ajuste de largura (90% da tela para parecer notificação)
        params.width = (resources.displayMetrics.widthPixels * 0.90).toInt()

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
                var imageFound = false
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
                        
                        // Processamento Síncrono (espera resultado) para controlar o delay corretamente
                        val task = recognizer.process(inputImage)
                        
                        // Aguarda a Task do ML Kit
                        while (!task.isComplete) { delay(50) }
                        
                        if (task.isSuccessful) {
                            // Se achou corrida, o analyzeScreen retorna TRUE
                            if (analyzeScreen(task.result.text)) {
                                imageFound = true
                            }
                        }
                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }

                // LÓGICA DE FREEZE (Pausa Inteligente)
                if (imageFound) {
                    // Achou corrida e mostrou janela?
                    // Desliga leitura por 5 segundos (Janela continua visível)
                    delay(5000)
                } else {
                    // Não achou nada?
                    // Esconde janela e tenta de novo em 1s (Scan rápido)
                    hideWindow()
                    delay(1000)
                }
            }
        }
    }

    private fun analyzeScreen(rawText: String): Boolean {
        val cleanText = rawText.replace("\n", " ").replace("\r", " ")
        
        val pricePattern = Pattern.compile("(R\\$|RS|\\$)\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\s*(min)", Pattern.CASE_INSENSITIVE)

        var maxPrice = 0.0
        var totalDist = 0.0
        var totalTime = 0.0

        // 1. Achar PREÇO (Maior valor da tela)
        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > maxPrice) maxPrice = v
        }

        // 2. Somar KMs
        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            totalDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        // 3. Somar MINUTOS
        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            totalTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // SE achou dados válidos -> Atualiza UI e retorna TRUE para pausar o loop
        if (maxPrice > 0.0 && (totalDist > 0.0 || totalTime > 0.0)) {
            val valPerKm = if (totalDist > 0) maxPrice / totalDist else 0.0
            val valPerHour = if (totalTime > 0) (maxPrice / totalTime) * 60 else 0.0
            
            showWindow(maxPrice, totalDist, totalTime, valPerKm, valPerHour)
            return true
        } 
        
        return false // Não achou nada
    }

    private fun showWindow(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            // Se já estiver visível com os MESMOS dados, não faz nada (evita flicker)
            // Mas como temos o delay de 5s, o flicker já é evitado pela lógica do loop.
            
            if (rootLayout.visibility != View.VISIBLE) rootLayout.visibility = View.VISIBLE

            // Formatação Exata Pedida
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km • %.0f min", dist, time)
            
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.2f/h", valKm, valHora)

            // Cores baseadas no KM
            val color = when {
                valKm >= 2.0 -> Color.parseColor("#4ADE80") // Verde
                valKm >= 1.5 -> Color.parseColor("#FACC15") // Amarelo
                else -> Color.parseColor("#F87171") // Vermelho
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