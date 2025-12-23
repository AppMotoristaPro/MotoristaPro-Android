import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- OCR SERVICE (Lógica de Comparação Robô vs Janela) ---
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
import android.view.View.OnTouchListener
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
    
    // UI
    private var bubbleView: View? = null
    private var infoCardView: LinearLayout? = null
    private var controlsView: LinearLayout? = null
    private var iconView: ImageView? = null
    
    // Movimento
    private var initialX = 0; private var initialY = 0; private var initialTouchX = 0f; private var initialTouchY = 0f
    private var bubbleParams: WindowManager.LayoutParams? = null

    // Texto Card
    private lateinit var tvValorTopo: TextView
    private lateinit var tvDadosMeio: TextView
    private lateinit var tvResultadosBaixo: TextView
    private lateinit var tvDicaAcao: TextView

    // Core
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    
    // --- VARIÁVEIS DE ESTADO (O CÉREBRO DA COMPARAÇÃO) ---
    private var isServiceRunning = false
    private var isMonitoring = true
    
    // Variavel da Janela (Memória do que está sendo exibido)
    private var windowPrice = 0.0
    private var windowDist = 0.0
    private var windowTime = 0.0
    
    // Timer de Timeout
    private var lastValidReadTime = 0L
    private val TIMEOUT_MS = 5000L // 5 Segundos para fechar

    // Configs
    private var minKm = 2.0
    private var minHora = 60.0
    private var screenWidth = 0; private var screenHeight = 0

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
            createMovableBubble()
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
        val notification = NotificationCompat.Builder(this, channelId).setContentTitle("Motorista Pro").setContentText("Monitoramento Ativo").setSmallIcon(R.drawable.ic_launcher_foreground).setOngoing(true).build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION) else startForeground(1, notification)
    }

    // --- UI SETUP (Bolha Transparente e Card) ---
    private fun createMovableBubble() {
        val bubbleLayout = FrameLayout(this)
        iconView = ImageView(this)
        iconView!!.setImageResource(R.drawable.ic_launcher_foreground)
        iconView!!.background = null; iconView!!.elevation = 10f
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(150, 150))
        bubbleParams = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        bubbleParams!!.gravity = Gravity.TOP or Gravity.START; bubbleParams!!.x = 20; bubbleParams!!.y = 300
        bubbleLayout.setOnTouchListener(object : OnTouchListener {
            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> { initialX = bubbleParams!!.x; initialY = bubbleParams!!.y; initialTouchX = event.rawX; initialTouchY = event.rawY; return true }
                    MotionEvent.ACTION_MOVE -> { bubbleParams!!.x = initialX + (event.rawX - initialTouchX).toInt(); bubbleParams!!.y = initialY + (event.rawY - initialTouchY).toInt(); windowManager.updateViewLayout(bubbleView, bubbleParams); return true }
                    MotionEvent.ACTION_UP -> { if (abs(event.rawX - initialTouchX) < 10 && abs(event.rawY - initialTouchY) < 10) showControls(); return true }
                }
                return false
            }
        })
        bubbleView = bubbleLayout
        windowManager.addView(bubbleView, bubbleParams)
    }
    
    private fun createControls() {
        controlsView = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(20, 20, 20, 20); visibility = View.GONE; background = GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = 30f; setStroke(1, Color.LTGRAY) } }
        val btnToggle = Button(this).apply { text = "PAUSAR"; textSize = 12f; setTextColor(Color.WHITE); background = GradientDrawable().apply { setColor(Color.parseColor("#F59E0B")); cornerRadius = 20f }; setOnClickListener { toggleMonitoring(this); hideControls() } }
        val btnKill = Button(this).apply { text = "FECHAR APP"; textSize = 10f; setTextColor(Color.WHITE); background = GradientDrawable().apply { setColor(Color.parseColor("#EF4444")); cornerRadius = 20f }; setOnClickListener { stopSelf() }; layoutParams = LinearLayout.LayoutParams(-1, -2).apply { setMargins(0, 10, 0, 0) } }
        val btnClose = TextView(this).apply { text = "Fechar Menu"; textSize = 12f; setTextColor(Color.GRAY); gravity = Gravity.CENTER; setPadding(0, 15, 0, 0); setOnClickListener { hideControls() } }
        controlsView!!.addView(btnToggle); controlsView!!.addView(btnKill); controlsView!!.addView(btnClose)
        val params = WindowManager.LayoutParams(600, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT); params.gravity = Gravity.CENTER
        windowManager.addView(controlsView, params)
    }
    
    private fun createInfoCard() {
        infoCardView = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(30, 25, 30, 25); visibility = View.GONE; background = GradientDrawable().apply { setColor(Color.parseColor("#F20F172A")); cornerRadius = 40f; setStroke(2, Color.parseColor("#33FFFFFF")) }; setOnClickListener { hideCard() } }
        tvValorTopo = TextView(this).apply { text = "R$ --"; textSize = 26f; setTextColor(Color.parseColor("#4ADE80")); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER; setShadowLayer(5f, 0f, 0f, Color.BLACK) }
        tvDadosMeio = TextView(this).apply { text = "--"; textSize = 14f; setTextColor(Color.LTGRAY); gravity = Gravity.CENTER; setPadding(0, 2, 0, 10) }
        tvResultadosBaixo = TextView(this).apply { text = "--"; textSize = 18f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER }
        tvDicaAcao = TextView(this).apply { text = "..."; textSize = 13f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER; setPadding(10, 5, 10, 5); layoutParams = LinearLayout.LayoutParams(-2, -2).apply { gravity = Gravity.CENTER_HORIZONTAL; setMargins(0, 15, 0, 0) } }
        infoCardView!!.addView(tvValorTopo); infoCardView!!.addView(tvDadosMeio); infoCardView!!.addView(tvResultadosBaixo); infoCardView!!.addView(tvDicaAcao)
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT); params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL; params.y = 80; params.width = (resources.displayMetrics.widthPixels * 0.90).toInt()
        windowManager.addView(infoCardView, params)
    }

    private fun toggleMonitoring(btn: Button) {
        isMonitoring = !isMonitoring
        if (isMonitoring) { btn.text = "PAUSAR"; iconView?.alpha = 1.0f; Toast.makeText(this, "Monitorando", 0).show() }
        else { btn.text = "RETOMAR"; iconView?.alpha = 0.5f; hideCard(); Toast.makeText(this, "Pausado", 0).show() }
    }
    private fun showControls() { bubbleView?.visibility = View.GONE; controlsView?.visibility = View.VISIBLE }
    private fun hideControls() { controlsView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE }
    private fun hideCard() { Handler(Looper.getMainLooper()).post { if (infoCardView?.visibility == View.VISIBLE) { infoCardView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE } } }

    private fun showCard(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            bubbleView?.visibility = View.GONE; controlsView?.visibility = View.GONE; infoCardView?.visibility = View.VISIBLE
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.2f/h", valKm, valHora)
            val color: Int; val message: String; val bgDica = GradientDrawable().apply { cornerRadius = 15f }
            if (valKm >= minKm) { color = Color.parseColor("#4ADE80"); message = "BOA! ACEITA LOGO 🚀"; bgDica.setColor(Color.parseColor("#334ADE80")) }
            else if (valKm >= (minKm * 0.75)) { color = Color.parseColor("#FACC15"); message = "MÉDIA. ANALISE BEM 🤔"; bgDica.setColor(Color.parseColor("#33FACC15")) }
            else { color = Color.parseColor("#F87171"); message = "PREJUÍZO! PULA FORA 🛑"; bgDica.setColor(Color.parseColor("#33F87171")) }
            tvResultadosBaixo.setTextColor(color); tvDicaAcao.text = message; tvDicaAcao.setTextColor(color); tvDicaAcao.background = bgDica
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val resultCode = intent?.getIntExtra("RESULT_CODE", 0) ?: 0
        val resultData = intent?.getParcelableExtra<Intent>("RESULT_DATA")
        if (mediaProjection != null) { isMonitoring = true; iconView?.alpha = 1.0f; return START_STICKY }
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
            isServiceRunning = true; startOcrLoop()
        } catch (e: Exception) { stopSelf() }
    }

    // --- LOOP INTELIGENTE ---
    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isServiceRunning) {
                if (!isMonitoring) { delay(500); continue }
                
                var hasNewData = false
                val image = try { imageReader?.acquireLatestImage() } catch (e: Exception) { null }
                
                if (image != null) {
                    try {
                        val planes = image.planes; val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride; val rowStride = planes[0].rowStride; val rowPadding = rowStride - pixelStride * screenWidth
                        val fullBitmap = Bitmap.createBitmap(screenWidth + rowPadding / pixelStride, screenHeight, Bitmap.Config.ARGB_8888)
                        fullBitmap.copyPixelsFromBuffer(buffer); image.close()
                        
                        // Crop 10% topo para não ler a janela
                        val cropY = (screenHeight * 0.10).toInt(); val cropHeight = screenHeight - cropY
                        if (cropHeight > 0 && cropY < fullBitmap.height) {
                            val croppedBitmap = Bitmap.createBitmap(fullBitmap, 0, cropY, screenWidth, cropHeight)
                            val inputImage = InputImage.fromBitmap(croppedBitmap, 0)
                            val task = recognizer.process(inputImage)
                            while (!task.isComplete) { delay(20) }
                            
                            if (task.isSuccessful) {
                                // CHAMA A ANÁLISE
                                hasNewData = analyzeScreen(task.result.text)
                            }
                        }
                    } catch (e: Exception) { try { image.close() } catch (x: Exception) {} }
                }
                
                // FECHAMENTO AUTOMÁTICO
                // Se NÃO teve dados válidos neste ciclo, checa o timeout
                if (!hasNewData) {
                    val timeSinceLast = System.currentTimeMillis() - lastValidReadTime
                    if (timeSinceLast > TIMEOUT_MS) {
                        hideCard()
                        // Reseta memória para permitir que a MESMA corrida apareça de novo se reaberta
                        windowPrice = 0.0
                        windowDist = 0.0
                    }
                }
                
                delay(1000) // Verifica a cada 1 segundo
            }
        }
    }

    private fun analyzeScreen(rawText: String): Boolean {
        // 1. Variáveis do Robô (Frame Atual) - ZERADAS SEMPRE
        var framePrice = 0.0
        var frameDist = 0.0
        var frameTime = 0.0

        val cleanText = rawText.replace("\\n", " ").replace("\\r", " ").lowercase()
        
        // 2. Extração (Regex)
        val pm = Pattern.compile("(?:r\\\\$|rs|\\\\$)\\\\s*([0-9]+[.,][0-9]{2})").matcher(cleanText)
        while (pm.find()) { val v = pm.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0; if (v > framePrice) framePrice = v }
        
        val dm = Pattern.compile("([0-9]+[.,]?[0-9]*)\\\\s*(km|m)(?!in)").matcher(cleanText)
        while (dm.find()) { 
            var d = dm.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (dm.group(2) == "m") d /= 1000.0 
            if (d < 200) frameDist += d 
        }
        
        val tm = Pattern.compile("([0-9]+)\\\\s*h\\\\s*(?:([0-9]+)\\\\s*min)?").matcher(cleanText)
        while (tm.find()) { frameTime += ((tm.group(1)?.toIntOrNull()?:0)*60) + (tm.group(2)?.toIntOrNull()?:0) }
        if (frameTime == 0.0) { 
            val mm = Pattern.compile("([0-9]+)\\\\s*min").matcher(cleanText)
            while (mm.find()) frameTime += mm.group(1)?.toDoubleOrNull() ?: 0.0 
        }

        // 3. Lógica de Comparação Robô vs Janela
        if (framePrice > 0.0 && (frameDist > 0.0 || frameTime > 0.0)) {
            // Achamos dados válidos!
            lastValidReadTime = System.currentTimeMillis() // Reseta timeout
            
            // É diferente do que está na Janela?
            if (isDifferentFromWindow(framePrice, frameDist)) {
                
                // SIM, É NOVO!
                // 1. Atualiza Memória da Janela
                windowPrice = framePrice
                windowDist = frameDist
                windowTime = frameTime
                
                // 2. Calcula
                val valPerKm = if (frameDist > 0) framePrice / frameDist else 0.0
                val valPerHour = if (frameTime > 0) (framePrice / frameTime) * 60 else 0.0
                
                // 3. Exibe (O showCard substitui o texto, não soma)
                showCard(framePrice, frameDist, frameTime, valPerKm, valPerHour)
                
                // Broadcast para o site
                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", framePrice); intent.putExtra("dist", frameDist); intent.putExtra("time", frameTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            // Se for IGUAL, não faz nada (mantém a janela aberta e o timer resetado)
            
            return true // Informa o loop que achamos dados
        }
        
        return false // Não achou nada neste frame
    }

    private fun isDifferentFromWindow(p: Double, d: Double): Boolean {
        // Compara Frame Atual (p, d) com Memória da Janela (windowPrice, windowDist)
        return (abs(p - windowPrice) > 0.1 || abs(d - windowDist) > 0.1)
    }

    override fun onDestroy() {
        super.onDestroy(); isServiceRunning = false
        try { if (bubbleView != null) windowManager.removeView(bubbleView); if (infoCardView != null) windowManager.removeView(infoCardView); if (controlsView != null) windowManager.removeView(controlsView) } catch (e: Exception) {}
        try { virtualDisplay?.release(); mediaProjection?.stop(); recognizer.close() } catch (e: Exception) {}
        LocalBroadcastManager.getInstance(this).unregisterReceiver(configReceiver)
    }
}
"""

print("--- Aplicando Lógica de Comparação e Timeout 5s ---")
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nExecute:")
print("1. git add .")
print("2. git commit -m 'Fix: Comparison Logic and Timeout'")
print("3. git push")


