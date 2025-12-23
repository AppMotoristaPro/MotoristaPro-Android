import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE FINAL (Bonito e Calculista) ---
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
            Log.e("OCR", "Erro Fatal", e)
        }
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro")
            .setContentText("Monitorando corridas...")
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
        
        // ESTILO FINAL: Fundo Preto Semitransparente (90% opacidade)
        overlayView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#E6000000")) 
            setPadding(30, 30, 30, 30)
        }

        statusText = TextView(this).apply {
            text = "Pronto"
            setTextColor(Color.LTGRAY)
            textSize = 12f
        }
        
        resultText = TextView(this).apply {
            text = "--"
            setTextColor(Color.WHITE)
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
        }

        // Botão de fechar discreto
        val closeBtn = Button(this).apply {
            text = "X"
            textSize = 10f
            layoutParams = LinearLayout.LayoutParams(100, 80).apply {
                gravity = Gravity.END
            }
            setOnClickListener { stopSelf() }
        }

        // Adiciona botão primeiro para ficar no topo ou em baixo, sua escolha. 
        // Aqui colocamos em baixo para nao atrapalhar leitura
        overlayView.addView(statusText)
        overlayView.addView(resultText)
        overlayView.addView(closeBtn)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
        params.y = 100 // Um pouco abaixo do topo para não cobrir notificações

        try {
            windowManager.addView(overlayView, params)
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
            
            // Callback obrigatório Android 14+
            mediaProjection?.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() {
                    super.onStop()
                    stopSelf()
                }
            }, Handler(Looper.getMainLooper()))
            
            val metrics = DisplayMetrics()
            windowManager.defaultDisplay.getMetrics(metrics)
            
            // Reduz resolução para economizar bateria e memória
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
            updateUI("Monitorando...", false)
            startOcrLoop()
        } catch (e: Exception) {
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
                                processFullText(visionText.text)
                            }
                            .addOnFailureListener {
                                // Silencioso em caso de erro de leitura para não poluir
                            }

                    } catch (e: Exception) {
                        try { image.close() } catch (x: Exception) {}
                    }
                }
                delay(2500) // Verifica a cada 2.5 segundos
            }
        }
    }

    private fun processFullText(rawText: String) {
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        
        // Regex Completa para Preço, Distância e Tempo
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)

        var price = 0.0
        var dist = 0.0
        var time = 0.0

        val priceMatcher = pricePattern.matcher(cleanText)
        if (priceMatcher.find()) {
            price = priceMatcher.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val distMatcher = distPattern.matcher(cleanText)
        if (distMatcher.find()) {
            dist = distMatcher.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        }

        val timeMatcher = timePattern.matcher(cleanText)
        if (timeMatcher.find()) {
            time = timeMatcher.group(1)?.toDoubleOrNull() ?: 0.0
        }

        // Só atualiza se achar pelo menos o preço e uma variável
        if (price > 0.0 && (dist > 0.0 || time > 0.0)) {
            val valPerKm = if (dist > 0) price / dist else 0.0
            val valPerHour = if (time > 0) (price / time) * 60 else 0.0
            
            val finalRes = String.format("R$ %.2f | %.1fkm | %.0fmin\\nKm: R$ %.2f\\nHora: R$ %.2f", 
                price, dist, time, valPerKm, valPerHour)
            
            // Lógica de Cor: Verde se for bom (ex: > R$ 2.00/km), Amarelo se for médio
            val isGood = valPerKm >= 2.0
            updateUI(finalRes, isGood)
        } else {
             // Se não achar nada, mantém o estado anterior ou mostra "Monitorando" 
             // (Não limpa a tela imediatamente para permitir leitura do motorista)
        }
    }

    private fun updateUI(msg: String, isGood: Boolean) {
        Handler(Looper.getMainLooper()).post {
            resultText.text = msg
            statusText.text = "Atualizado"
            if (isGood) {
                 resultText.setTextColor(Color.GREEN)
            } else {
                 resultText.setTextColor(Color.YELLOW) // Amarelo padrão, Verde se for top
            }
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

print("--- Gerando Versão Final (Ouro) ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nApp Finalizado.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'Release: Versao Final'")
print("3. git push")


