import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Com Dicas de Ação) ---
ocr_service_content = """
package com.motoristapro.android

import android.app.*
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.graphics.*
import android.graphics.drawable.GradientDrawable
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.*
import android.util.DisplayMetrics
import android.view.*
import android.widget.*
import androidx.core.app.NotificationCompat
import androidx.localbroadcastmanager.content.LocalBroadcastManager
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.*
import java.util.regex.Pattern
import kotlin.math.abs

class OcrService : Service() {

    private lateinit var windowManager: WindowManager
    
    // VIEWS
    private var bubbleView: View? = null
    private var infoCardView: LinearLayout? = null
    private var controlsView: LinearLayout? = null
    private var iconView: ImageView? = null

    // Elementos do Card
    private lateinit var tvValorTopo: TextView
    private lateinit var tvDadosMeio: TextView
    private lateinit var tvResultadosBaixo: TextView
    private lateinit var tvDicaAcao: TextView // NOVA LINHA: DICA

    // Core
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    
    // Estados
    private var isServiceRunning = false
    private var isMonitoring = true
    private var lastValidReadTime = 0L
    private val TIMEOUT_MS = 5000L
    
    // Memória
    private var lastPrice = 0.0
    private var lastDist = 0.0
    
    // Configs
    private var minKm = 2.0
    private var minHora = 60.0
    private var screenWidth = 0
    private var screenHeight = 0

    private val configReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) { loadConfigs() }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        loadConfigs()
        LocalBroadcastManager.getInstance(this).registerReceiver(configReceiver, IntentFilter("OCR_CONFIG_UPDATED"))
        
        try {
            startForegroundServiceCompat()
            createBubble()
            createInfoCard()
            createControls()
            isServiceRunning = true
        } catch (e: Exception) { e.printStackTrace() }
    }
    
    private fun loadConfigs() {
        val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
        minKm = prefs.getFloat("min_km", 2.0f).toDouble()
        minHora = prefs.getFloat("min_hora", 60.0f).toDouble()
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro").setContentText("Monitoramento Ativo").setSmallIcon(R.drawable.ic_launcher_foreground).setOngoing(true).build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    // --- 1. BOLHA ---
    private fun createBubble() {
        val bubbleLayout = FrameLayout(this)
        iconView = ImageView(this)
        iconView!!.setImageResource(R.drawable.ic_launcher_foreground)
        updateBubbleState(true)
        
        iconView!!.setPadding(15,15,15,15)
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(120, 120))
        
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT
        )
        params.gravity = Gravity.TOP or Gravity.START; params.x = 20; params.y = 300
        
        bubbleLayout.setOnClickListener { showControls() }
        bubbleView = bubbleLayout
        windowManager.addView(bubbleView, params)
    }
    
    private fun updateBubbleState(active: Boolean) {
        val bg = GradientDrawable()
        bg.shape = GradientDrawable.OVAL
        bg.setStroke(2, Color.WHITE)
        if (active) {
            bg.setColor(Color.parseColor("#2563EB"))
            iconView?.alpha = 1.0f
        } else {
            bg.setColor(Color.parseColor("#475569"))
            iconView?.alpha = 0.7f
        }
        iconView?.background = bg
    }

    // --- 2. CONTROLES ---
    private fun createControls() {
        controlsView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(20, 20, 20, 20)
            visibility = View.GONE
            background = GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = 30f; setStroke(1, Color.LTGRAY) }
        }
        
        val btnToggle = Button(this).apply {
            text = "PAUSAR MONITORAMENTO"
            textSize = 12f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply { setColor(Color.parseColor("#F59E0B")); cornerRadius = 20f }
            setOnClickListener { toggleMonitoring(this); hideControls() }
        }
        
        val btnKill = Button(this).apply {
            text = "FECHAR APP TOTALMENTE"
            textSize = 10f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply { setColor(Color.parseColor("#EF4444")); cornerRadius = 20f }
            setOnClickListener { stopSelf() }
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply { setMargins(0, 10, 0, 0) }
        }
        
        val btnCloseMenu = TextView(this).apply {
            text = "Fechar Menu"; textSize = 12f; setTextColor(Color.GRAY); gravity = Gravity.CENTER
            setPadding(0, 15, 0, 0); setOnClickListener { hideControls() }
        }
        
        controlsView!!.addView(btnToggle); controlsView!!.addView(btnKill); controlsView!!.addView(btnCloseMenu)

        val params = WindowManager.LayoutParams(600, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.CENTER
        windowManager.addView(controlsView, params)
    }
    
    private fun toggleMonitoring(btn: Button) {
        isMonitoring = !isMonitoring
        if (isMonitoring) {
            btn.text = "PAUSAR MONITORAMENTO"; updateBubbleState(true); Toast.makeText(this, "Monitoramento Retomado", Toast.LENGTH_SHORT).show()
        } else {
            btn.text = "ATIVAR MONITORAMENTO"; updateBubbleState(false); hideCard(); Toast.makeText(this, "Monitoramento Pausado", Toast.LENGTH_SHORT).show()
        }
    }

    // --- 3. CARD (COM DICA DE AÇÃO) ---
    private fun createInfoCard() {
        infoCardView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(30, 25, 30, 25)
            visibility = View.GONE 
            background = GradientDrawable().apply { setColor(Color.parseColor("#F20F172A")); cornerRadius = 40f; setStroke(2, Color.parseColor("#33FFFFFF")) }
        }

        tvValorTopo = TextView(this).apply { text = "R$ --"; textSize = 26f; setTextColor(Color.parseColor("#4ADE80")); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER; setShadowLayer(5f, 0f, 0f, Color.BLACK) }
        tvDadosMeio = TextView(this).apply { text = "-- km • -- min"; textSize = 14f; setTextColor(Color.LTGRAY); gravity = Gravity.CENTER; setPadding(0, 2, 0, 10) }
        tvResultadosBaixo = TextView(this).apply { text = "R$ --/km • R$ --/h"; textSize = 18f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER }
        
        // NOVA LINHA: DICA
        tvDicaAcao = TextView(this).apply {
            text = "..."
            textSize = 13f
            setTextColor(Color.WHITE)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(10, 5, 10, 5)
            // Background será definido dinamicamente
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                setMargins(0, 15, 0, 0)
            }
        }

        infoCardView!!.addView(tvValorTopo); infoCardView!!.addView(tvDadosMeio); infoCardView!!.addView(tvResultadosBaixo); infoCardView!!.addView(tvDicaAcao)
        
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL; params.y = 80; params.width = (resources.displayMetrics.widthPixels * 0.90).toInt()
        windowManager.addView(infoCardView, params)
    }

    private fun showControls() { bubbleView?.visibility = View.GONE; controlsView?.visibility = View.VISIBLE }
    private fun hideControls() { controlsView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE }
    
    private fun showCard(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            bubbleView?.visibility = View.GONE; controlsView?.visibility = View.GONE; infoCardView?.visibility = View.VISIBLE
            
            // Textos
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.2f/h", valKm, valHora)
            
            // Lógica de Decisão
            val color: Int
            val message: String
            val bgDica = GradientDrawable().apply { cornerRadius = 15f }

            if (valKm >= minKm) {
                // BOA
                color = Color.parseColor("#4ADE80") // Verde
                message = "BOA! ACEITA LOGO 🚀"
                bgDica.setColor(Color.parseColor("#334ADE80")) // Verde Translúcido
            } else if (valKm >= (minKm * 0.75)) {
                // MÉDIA
                color = Color.parseColor("#FACC15") // Amarelo
                message = "MÉDIA. ANALISE BEM 🤔"
                bgDica.setColor(Color.parseColor("#33FACC15")) // Amarelo Translúcido
            } else {
                // RUIM
                color = Color.parseColor("#F87171") // Vermelho
                message = "PREJUÍZO! PULA FORA 🛑"
                bgDica.setColor(Color.parseColor("#33F87171")) // Vermelho Translúcido
            }
            
            tvResultadosBaixo.setTextColor(color)
            tvDicaAcao.text = message
            tvDicaAcao.setTextColor(color)
            tvDicaAcao.background = bgDica
        }
    }
    
    private fun hideCard() { 
        Handler(Looper.getMainLooper()).post { 
            if (infoCardView?.visibility == View.VISIBLE) {
                infoCardView?.visibility = View.GONE
                bubbleView?.visibility = View.VISIBLE
            }
        } 
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val resultCode = intent?.getIntExtra("RESULT_CODE", 0) ?: 0
        val resultData = intent?.getParcelableExtra<Intent>("RESULT_DATA")
        if (mediaProjection != null) { isMonitoring = true; updateBubbleState(true); return START_STICKY }
        if (resultCode != 0 && resultData != null) setupMediaProjection(resultCode, resultData)
        return START_STICKY
    }

    private fun setupMediaProjection(code: Int, data: Intent) {
        try {
            val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
            mediaProjection = mpManager.getMediaProjection(code, data)
            mediaProjection?.registerCallback(object : MediaProjection.Callback() { override fun onStop() { super.onStop(); stopSelf() } }, Handler(Looper.getMainLooper()))
            val metrics = DisplayMetrics(); windowManager.defaultDisplay.getMetrics(metrics)
            screenWidth = metrics.widthPixels / 2; screenHeight = metrics.heightPixels / 2
            imageReader = ImageReader.newInstance(screenWidth, screenHeight, PixelFormat.RGBA_8888, 2)
            virtualDisplay = mediaProjection?.createVirtualDisplay("ScreenCapture", screenWidth, screenHeight, metrics.densityDpi, DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, imageReader?.surface, null, null)
            isRunning = true; startOcrLoop()
        } catch (e: Exception) { stopSelf() }
    }

    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isServiceRunning) {
                if (!isMonitoring) { delay(500); continue }
                var image = try { imageReader?.acquireLatestImage() } catch (e: Exception) { null }
                var frameHasData = false
                if (image != null) {
                    try {
                        val planes = image.planes; val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride; val rowStride = planes[0].rowStride; val rowPadding = rowStride - pixelStride * screenWidth
                        val fullBitmap = Bitmap.createBitmap(screenWidth + rowPadding / pixelStride, screenHeight, Bitmap.Config.ARGB_8888)
                        fullBitmap.copyPixelsFromBuffer(buffer); image.close()
                        val cropY = (screenHeight * 0.10).toInt(); val cropHeight = screenHeight - cropY
                        if (cropHeight > 0 && cropY < fullBitmap.height) {
                            val croppedBitmap = Bitmap.createBitmap(fullBitmap, 0, cropY, screenWidth, cropHeight)
                            val inputImage = InputImage.fromBitmap(croppedBitmap, 0)
                            val task = recognizer.process(inputImage)
                            while (!task.isComplete) { delay(20) }
                            if (task.isSuccessful) frameHasData = analyzeScreen(task.result.text)
                        }
                    } catch (e: Exception) { try { image.close() } catch (x: Exception) {} }
                }
                if (!frameHasData && (System.currentTimeMillis() - lastValidReadTime > TIMEOUT_MS)) { hideCard() }
                delay(1000)
            }
        }
    }

    private fun analyzeScreen(rawText: String): Boolean {
        var framePrice = 0.0; var frameDist = 0.0; var frameTime = 0.0
        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ")
        val pricePattern = Pattern.compile("(R\\\\$|RS|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})", Pattern.CASE_INSENSITIVE)
        val distPattern = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|xm)", Pattern.CASE_INSENSITIVE)
        val timePattern = Pattern.compile("([0-9]+)\\\\s*(min)", Pattern.CASE_INSENSITIVE)
        val pm = pricePattern.matcher(cleanText); 
        while (pm.find()) { val v = pm.group(2)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0; if (v > framePrice) framePrice = v }
        val dm = distPattern.matcher(cleanText); 
        while (dm.find()) frameDist += dm.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
        val tm = timePattern.matcher(cleanText); 
        while (tm.find()) frameTime += tm.group(1)?.toDoubleOrNull() ?: 0.0

        if (framePrice > 0.0 && (frameDist > 0.0 || frameTime > 0.0)) {
            lastValidReadTime = System.currentTimeMillis()
            if (isDifferent(framePrice, frameDist)) {
                lastPrice = framePrice; lastDist = frameDist
                val valPerKm = if (frameDist > 0) framePrice / frameDist else 0.0
                val valPerHour = if (frameTime > 0) (framePrice / frameTime) * 60 else 0.0
                showCard(framePrice, frameDist, frameTime, valPerKm, valPerHour)
                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", framePrice); intent.putExtra("dist", frameDist); intent.putExtra("time", frameTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            return true
        }
        return false
    }

    private fun isDifferent(p: Double, d: Double): Boolean { return (abs(p - lastPrice) > 0.1 || abs(d - lastDist) > 0.5) }

    override fun onDestroy() {
        super.onDestroy(); isServiceRunning = false
        try { if (bubbleView != null) windowManager.removeView(bubbleView); if (infoCardView != null) windowManager.removeView(infoCardView); if (controlsView != null) windowManager.removeView(controlsView) } catch (e: Exception) {}
        try { virtualDisplay?.release(); mediaProjection?.stop(); recognizer.close() } catch (e: Exception) {}
        LocalBroadcastManager.getInstance(this).unregisterReceiver(configReceiver)
    }
}
"""

print("--- Aplicando Dicas de Ação (Boa/Ruim) ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'UI: Add Action Hints (Boa/Ruim)'")
print("3. git push")


