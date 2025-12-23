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
    
    // --- UI HIERARQUIA ---
    private lateinit var tvValorTopo: TextView       // 1. R$ 20,00 (Grande)
    private lateinit var tvDadosMeio: TextView       // 2. 10km 10min (Pequeno)
    private lateinit var tvResultadosBaixo: TextView // 3. R$ 2,00/km R$ 120/h (Médio/Destaque)

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

    private fun setupGlassOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // --- CONTAINER GLASS ---
        rootLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(30, 25, 30, 25)
            visibility = View.GONE // Invisível até achar algo
            
            // Fundo Glass Escuro (Slate 900 com transparência)
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#F20F172A")) // Quase opaco para leitura
                cornerRadius = 40f
                setStroke(2, Color.parseColor("#33FFFFFF")) // Borda fina branca
            }
        }

        // 1. TOPO: VALOR (Gigante e Centralizado)
        tvValorTopo = TextView(this).apply {
            text = "R$ --"
            textSize = 32f // Bem Grande
            setTextColor(Color.parseColor("#4ADE80")) // Verde Neon
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setShadowLayer(10f, 0f, 0f, Color.BLACK)
        }

        // 2. MEIO: SOMA DE KM e MIN (Pequeno)
        tvDadosMeio = TextView(this).apply {
            text = "-- km  •  -- min"
            textSize = 14f
            setTextColor(Color.LTGRAY) // Cinza claro
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 10) // Espaço para separar do resultado final
        }

        // 3. BAIXO: RESULTADOS R$/KM e R$/H (Médio)
        tvResultadosBaixo = TextView(this).apply {
            text = "R$ --/km • R$ --/h"
            textSize = 18f
            setTextColor(Color.WHITE)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        rootLayout.addView(tvValorTopo)
        rootLayout.addView(tvDadosMeio)
        rootLayout.addView(tvResultadosBaixo)

        // Params da Janela
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 120 
        
        // Largura estilo Notificação (90% da tela)
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
                var foundData = false
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
                        
                        val task = recognizer.process(inputImage)
                        while (!task.isComplete) { delay(50) } // Espera resultado síncrono
                        
                        if (task.isSuccessful) {
                            // Se analyzeScreen retornar TRUE, significa que achou corrida
                            foundData = analyzeScreen(task.result.text)
                        }
                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }

                // --- CICLO DE VIDA DO OCR (O Segredo) ---
                if (foundData) {
                    // Cenario 1: Achou corrida.
                    // A janela já foi atualizada dentro do analyzeScreen.
                    // Agora PAUSAMOS por 5 segundos. A janela fica visível.
                    delay(5000)
                } else {
                    // Cenario 2: Não achou nada (ou a corrida sumiu).
                    // Fecha a janela imediatamente.
                    hideWindow()
                    // Espera só 1 segundo para tentar ler de novo (modo busca rápida).
                    delay(1000)
                }
            }
        }
    }

    private fun analyzeScreen(rawText: String): Boolean {
        // RESET DE VARIÁVEIS (Essencial para não somar infinitamente)
        // Elas são recriadas a cada frame lido.
        var frameMaxPrice = 0.0
        var frameTotalDist = 0.0
        var frameTotalTime = 0.0

        val cleanText = rawText.replace("\n", " ").replace("\r", " ")
        
        val pricePattern = Pattern.compile("(R\\$|RS|\\$)\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\s*(min)", Pattern.CASE_INSENSITIVE)

        // 1. Achar PREÇO (Maior valor)
        val priceMatcher = pricePattern.matcher(cleanText)
        while (priceMatcher.find()) {
            val v = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > frameMaxPrice) frameMaxPrice = v
        }

        // 2. Somar KMs
        val distMatcher = distPattern.matcher(cleanText)
        while (distMatcher.find()) {
            frameTotalDist += distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        // 3. Somar MINUTOS
        val timeMatcher = timePattern.matcher(cleanText)
        while (timeMatcher.find()) {
            frameTotalTime += timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // Se achou dados válidos neste frame
        if (frameMaxPrice > 0.0 && (frameTotalDist > 0.0 || frameTotalTime > 0.0)) {
            val valPerKm = if (frameTotalDist > 0) frameMaxPrice / frameTotalDist else 0.0
            val valPerHour = if (frameTotalTime > 0) (frameMaxPrice / frameTotalTime) * 60 else 0.0
            
            showWindow(frameMaxPrice, frameTotalDist, frameTotalTime, valPerKm, valPerHour)
            return true // Retorna TRUE para ativar o delay de 5s
        } 
        
        return false // Retorna FALSE para fechar janela e buscar rápido
    }

    private fun showWindow(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            if (rootLayout.visibility != View.VISIBLE) rootLayout.visibility = View.VISIBLE

            // Formatação Exata Solicitada
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km  •  %.0f min", dist, time)
            
            // Texto da Última Linha
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