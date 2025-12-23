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
    
    // UI
    private var bubbleView: View? = null
    private var infoCardView: LinearLayout? = null
    private var controlsView: LinearLayout? = null
    private var iconView: ImageView? = null

    // Textos
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
    
    // Estados
    private var isServiceRunning = false
    private var isMonitoring = true
    private var lastValidReadTime = 0L
    private val TIMEOUT_MS = 5000L // Fecha em 5s se não achar nada
    
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
            .setContentTitle("Motorista Pro").setContentText("Monitoramento Ativo")
            .setSmallIcon(R.drawable.ic_launcher_foreground).setOngoing(true).build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    // --- UI (Bolha e Card) ---
    private fun createBubble() {
        val bubbleLayout = FrameLayout(this)
        // --- NOVO DESIGN: Redondo, Branco e com Ícone do App ---
        val bg = GradientDrawable()
        bg.shape = GradientDrawable.OVAL
        bg.setColor(Color.WHITE)
        bg.setStroke(2, Color.parseColor("#2563EB")) // Azul do Site
        bubbleLayout.background = bg
        bubbleLayout.elevation = 20f

        iconView = ImageView(this)
        // Usa o ícone do próprio APK (que você vai substituir manualmente)
        iconView!!.setImageResource(R.mipmap.ic_launcher_round)
        iconView!!.setPadding(15, 15, 15, 15) // Margem interna para ficar bonito
        
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(160, 160))
        // -------------------------------------------------------
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.TOP or Gravity.START; params.x = 20; params.y = 300
        bubbleLayout.setOnClickListener { showControls() }
        bubbleView = bubbleLayout
        windowManager.addView(bubbleView, params)
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
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        
        // POSIÇÃO FIXA NO TOPO (Importante para a máscara saber onde cortar)
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL; params.y = 80; 
        params.width = (resources.displayMetrics.widthPixels * 0.90).toInt()
        windowManager.addView(infoCardView, params)
    }

    private fun toggleMonitoring(btn: Button) {
        isMonitoring = !isMonitoring
        if (isMonitoring) { btn.text = "PAUSAR"; iconView?.alpha = 1.0f; Toast.makeText(this, "Retomado", Toast.LENGTH_SHORT).show() }
        else { btn.text = "RETOMAR"; iconView?.alpha = 0.5f; hideCard(); Toast.makeText(this, "Pausado", Toast.LENGTH_SHORT).show() }
    }
    private fun showControls() { bubbleView?.visibility = View.GONE; controlsView?.visibility = View.VISIBLE }
    private fun hideControls() { controlsView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE }
    
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
    private fun hideCard() { Handler(Looper.getMainLooper()).post { if (infoCardView?.visibility == View.VISIBLE) { infoCardView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE } } }

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

    private fun startOcrLoop() {
        scope.launch(Dispatchers.IO) {
            while (isServiceRunning) {
                if (!isMonitoring) { delay(1000); continue }
                
                var image = try { imageReader?.acquireLatestImage() } catch (e: Exception) { null }
                var hasValidData = false
                
                if (image != null) {
                    try {
                        val planes = image.planes; val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride; val rowStride = planes[0].rowStride; val rowPadding = rowStride - pixelStride * screenWidth
                        
                        // 1. Converte para Bitmap
                        val fullBitmap = Bitmap.createBitmap(screenWidth + rowPadding / pixelStride, screenHeight, Bitmap.Config.ARGB_8888)
                        fullBitmap.copyPixelsFromBuffer(buffer)
                        image.close()
                        
                        // 2. APLICA MÁSCARA DE SEGURANÇA (O PULO DO GATO)
                        // Pintamos um retângulo PRETO sobre os 25% superiores da tela.
                        // Isso garante que o OCR nunca leia a nossa janela flutuante.
                        val canvas = Canvas(fullBitmap)
                        val paint = Paint()
                        paint.color = Color.BLACK
                        paint.style = Paint.Style.FILL
                        
                        // Desenha o quadrado preto no topo (Cobre a janela)
                        canvas.drawRect(0f, 0f, fullBitmap.width.toFloat(), fullBitmap.height * 0.25f, paint)

                        // 3. Envia para IA
                        val inputImage = InputImage.fromBitmap(fullBitmap, 0)
                        val task = recognizer.process(inputImage)
                        while (!task.isComplete) { delay(20) }
                        if (task.isSuccessful) hasValidData = analyzeScreen(task.result.text)
                        
                    } catch (e: Exception) { try { image.close() } catch (x: Exception) {} }
                }
                
                // Timeout e Fechamento
                if (!hasValidData) {
                    if (System.currentTimeMillis() - lastValidReadTime > TIMEOUT_MS) {
                        hideCard()
                        lastPrice = 0.0 // Reset para permitir reabertura
                    }
                }
                delay(1000)
            }
        }
    }

    private fun analyzeScreen(rawText: String): Boolean {
        var framePrice = 0.0; var frameDist = 0.0; var frameTime = 0.0
        // Limpeza agressiva: remove tudo que não é alphanumérico ou pontuação chave
        val cleanText = rawText.replace("[^0-9a-zA-Z$,. ]".toRegex(), " ").lowercase()
        
        // 1. PREÇO: Aceita "R$ 10", "10,50", "10.5", "10"
        // Regex busca cifrão seguido de digitos, com ou sem decimais
        val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)").matcher(cleanText)
        while (pm.find()) { 
            val vStr = pm.group(1)?.replace(",", ".") 
            val v = vStr?.toDoubleOrNull() ?: 0.0
            // Filtro de segurança: ignora valores absurdos (ex: R$ 0.00 ou R$ 5000 numa tela só)
            if (v > 1.0 && v < 2000.0 && v > framePrice) framePrice = v 
        }
        
        // 2. DISTÂNCIA: Aceita "1.5 km", "10km", "500m"
        val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)").matcher(cleanText)
        while (dm.find()) { 
            var d = dm.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = dm.group(2)
            if (unit == "m") d /= 1000.0 // Converte metros para KM
            // Filtro: Viagens muito longas (>300km) geralmente são erro de leitura de data/hora
            if (d > 0.1 && d < 300.0) frameDist += d 
        }
        
        // 3. TEMPO: Aceita "1h 20min", "50 min"
        val tm = Pattern.compile("([0-9]+)\\s*h\\s*(?:([0-9]+)\\s*min)?").matcher(cleanText)
        while (tm.find()) { 
            val h = tm.group(1)?.toIntOrNull() ?: 0
            val m = tm.group(2)?.toIntOrNull() ?: 0
            frameTime += (h * 60) + m
        }
        if (frameTime == 0.0) { 
            val mm = Pattern.compile("([0-9]+)\\s*min").matcher(cleanText)
            while (mm.find()) frameTime += mm.group(1)?.toDoubleOrNull() ?: 0.0 
        }

        // --- LÓGICA DE DECISÃO ---
        // Só exibe se tivermos PREÇO e (Distância OU Tempo)
        if (framePrice > 0.0 && (frameDist > 0.0 || frameTime > 0.0)) {
            lastValidReadTime = System.currentTimeMillis()
            
            // Evita ficar piscando a tela com a mesma leitura
            if (abs(framePrice - lastPrice) > 0.1 || abs(frameDist - lastDist) > 0.1) {
                lastPrice = framePrice; lastDist = frameDist
                
                // Cálculos de Rentabilidade
                val valPerKm = if (frameDist > 0) framePrice / frameDist else 0.0
                val valPerHour = if (frameTime > 0) (framePrice / frameTime) * 60 else 0.0
                
                // Exibe o Card (Usa as configs minKm e minHora carregadas do site)
                showCard(framePrice, frameDist, frameTime, valPerKm, valPerHour)
                
                // Envia para o site (WebView)
                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", framePrice); intent.putExtra("dist", frameDist); intent.putExtra("time", frameTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            return true
        }
        return false
    }

    

    override fun onDestroy() {
        super.onDestroy(); isServiceRunning = false
        try { if (bubbleView != null) windowManager.removeView(bubbleView); if (infoCardView != null) windowManager.removeView(infoCardView); if (controlsView != null) windowManager.removeView(controlsView) } catch (e: Exception) {}
        try { virtualDisplay?.release(); mediaProjection?.stop(); recognizer.close() } catch (e: Exception) {}
        LocalBroadcastManager.getInstance(this).unregisterReceiver(configReceiver)
    }
}