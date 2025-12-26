package com.motoristapro.android

import android.app.*
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.graphics.*
import android.util.DisplayMetrics
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.*
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
    private var bubbleView: View? = null
    private var infoCardView: LinearLayout? = null
    private var iconView: ImageView? = null
    
    // Elementos de Texto
    private lateinit var tvValorTopo: TextView
    private lateinit var tvDadosMeio: TextView
    private lateinit var tvResultadosBaixo: TextView
    private lateinit var tvDicaAcao: TextView

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    
    // Configurações
    private var goodKm = 2.0
    private var badKm = 1.5
    private var goodHour = 60.0
    private var badHour = 40.0
    
    private var isServiceRunning = false
    private var isMonitoring = true
    private var lastValidReadTime = 0L
    private val TIMEOUT_MS = 5000L
    
    private var lastPrice = 0.0
    private var lastDist = 0.0
    private var screenWidth = 0
    private var screenHeight = 0
    private lateinit var bubbleParams: WindowManager.LayoutParams

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
            isServiceRunning = true
        } catch (e: Exception) { e.printStackTrace() }
    }
    
    private fun loadConfigs() {
        val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
        goodKm = prefs.getFloat("good_km", 2.0f).toDouble()
        badKm = prefs.getFloat("bad_km", 1.5f).toDouble()
        goodHour = prefs.getFloat("good_hour", 60.0f).toDouble()
        badHour = prefs.getFloat("bad_hour", 40.0f).toDouble()
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "OCR Service", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro").setContentText("Robô Ativo")
            .setSmallIcon(R.drawable.ic_launcher_foreground).setOngoing(true).build()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
        } else {
            startForeground(1, notification)
        }
    }

    private fun createBubble() {
        val bubbleLayout = FrameLayout(this)
        bubbleLayout.background = null 

        iconView = ImageView(this)
        iconView!!.setImageResource(R.mipmap.ic_launcher_round)
        iconView!!.scaleType = ImageView.ScaleType.CENTER_CROP
        
        iconView!!.outlineProvider = object : ViewOutlineProvider() {
            override fun getOutline(view: View, outline: Outline) {
                outline.setOval(0, 0, view.width, view.height)
            }
        }
        iconView!!.clipToOutline = true
        
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(160, 160))

        bubbleLayout.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View?, event: MotionEvent?): Boolean {
                when (event!!.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialX = bubbleParams.x
                        initialY = bubbleParams.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        bubbleParams.x = initialX + (event.rawX - initialTouchX).toInt()
                        bubbleParams.y = initialY + (event.rawY - initialTouchY).toInt()
                        windowManager.updateViewLayout(bubbleView, bubbleParams)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        if (abs(event.rawX - initialTouchX) < 10 && abs(event.rawY - initialTouchY) < 10) {
                            toggleMonitoring()
                        }
                        return true
                    }
                }
                return false
            }
        })

        bubbleView = bubbleLayout
        bubbleParams = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        bubbleParams.gravity = Gravity.TOP or Gravity.START
        bubbleParams.x = 20
        bubbleParams.y = 300
        windowManager.addView(bubbleView, bubbleParams)
    }
    
    private fun createInfoCard() {
        infoCardView = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(30, 25, 30, 25); visibility = View.GONE; background = GradientDrawable().apply { setColor(Color.parseColor("#F20F172A")); cornerRadius = 40f; setStroke(2, Color.parseColor("#33FFFFFF")) }; setOnClickListener { hideCard() } }
        tvValorTopo = TextView(this).apply { text = "R$ --"; textSize = 26f; setTextColor(Color.parseColor("#4ADE80")); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER; setShadowLayer(5f, 0f, 0f, Color.BLACK) }
        tvDadosMeio = TextView(this).apply { text = "--"; textSize = 14f; setTextColor(Color.LTGRAY); gravity = Gravity.CENTER; setPadding(0, 2, 0, 10) }
        tvResultadosBaixo = TextView(this).apply { text = "--"; textSize = 18f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER }
        tvDicaAcao = TextView(this).apply { text = "..."; textSize = 13f; setTextColor(Color.WHITE); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER; setPadding(10, 5, 10, 5); layoutParams = LinearLayout.LayoutParams(-2, -2).apply { gravity = Gravity.CENTER_HORIZONTAL; setMargins(0, 15, 0, 0) } }
        infoCardView!!.addView(tvValorTopo); infoCardView!!.addView(tvDadosMeio); infoCardView!!.addView(tvResultadosBaixo); infoCardView!!.addView(tvDicaAcao)
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL; params.y = 80; 
        params.width = (resources.displayMetrics.widthPixels * 0.65).toInt()
        windowManager.addView(infoCardView, params)
    }

    private fun toggleMonitoring() {
        isMonitoring = !isMonitoring
        if (isMonitoring) { iconView?.alpha = 1.0f; Toast.makeText(this, "Robô Ligado", Toast.LENGTH_SHORT).show() }
        else { iconView?.alpha = 0.5f; hideCard(); Toast.makeText(this, "Pausado", Toast.LENGTH_SHORT).show() }
    }
    
    private fun showCard(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double, color: Int, msg: String, bg: Drawable) {
        Handler(Looper.getMainLooper()).post {
            bubbleView?.visibility = View.GONE; infoCardView?.visibility = View.VISIBLE
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.2f/h", valKm, valHora)
            
            tvResultadosBaixo.setTextColor(color)
            tvDicaAcao.text = msg
            tvDicaAcao.setTextColor(color)
            tvDicaAcao.background = bg
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
                        
                        val fullBitmap = Bitmap.createBitmap(screenWidth + rowPadding / pixelStride, screenHeight, Bitmap.Config.ARGB_8888)
                        fullBitmap.copyPixelsFromBuffer(buffer)
                        image.close()
                        
                        val canvas = Canvas(fullBitmap)
                        val paint = Paint()
                        paint.color = Color.BLACK
                        paint.style = Paint.Style.FILL
                        canvas.drawRect(0f, 0f, fullBitmap.width.toFloat(), fullBitmap.height * 0.25f, paint)

                        val inputImage = InputImage.fromBitmap(fullBitmap, 0)
                        val task = recognizer.process(inputImage)
                        while (!task.isComplete) { delay(20) }
                        if (task.isSuccessful) hasValidData = analyzeScreen(task.result.text)
                        
                    } catch (e: Exception) { try { image.close() } catch (x: Exception) {} }
                }
                
                if (!hasValidData) {
                    if (System.currentTimeMillis() - lastValidReadTime > TIMEOUT_MS) {
                        hideCard()
                        lastPrice = 0.0
                    }
                }
                delay(1000)
            }
        }
    }

    // --- CÉREBRO OCR (Com Filtros) ---
    private fun analyzeScreen(rawText: String): Boolean {
        var cleanText = rawText.lowercase()
            .replace(Regex("""r\$\s*[0-9.,]+\s*/\s*km"""), "") 
            .replace(Regex("""\+\s*r\$\s*[0-9.,]+\s*inclu[íi]do"""), "")
            .replace("mais de 30 min", "")
            .replace("[^0-9a-zA-Z$,. ]".toRegex(), " ")

        val prices = ArrayList<Double>()
        val dists = ArrayList<Double>()
        val times = ArrayList<Double>()

        val pm = Pattern.compile("""(?:r\$|rs|\$)\s*([0-9]+(?:[.,][0-9]{0,2})?)""")
        val matP = pm.matcher(cleanText)
        while (matP.find()) {
            val v = matP.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > 4.5 && v < 2000.0) prices.add(v)
        }

        val dm = Pattern.compile("""([0-9]+(?:[.,][0-9]+)?)\s*(km|m)(?!in)""")
        val matD = dm.matcher(cleanText)
        while (matD.find()) {
            var d = matD.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = matD.group(2)
            if (unit == "m") d /= 1000.0
            if (d > 0.05 && d < 400.0) dists.add(d)
        }

        val tmH = Pattern.compile("""([0-9]+)\s*(?:h|hr|hrs|hora)""")
        val matH = tmH.matcher(cleanText)
        while (matH.find()) {
            val h = matH.group(1)?.toIntOrNull() ?: 0
            if (h > 0) times.add((h * 60).toDouble())
        }
        cleanText = matH.replaceAll(" ") 

        val tmM = Pattern.compile("""([0-9]+)\s*(?:min|m)(?!in)""")
        val matM = tmM.matcher(cleanText)
        while (matM.find()) {
            val m = matM.group(1)?.toDoubleOrNull() ?: 0.0
            if (m > 0) times.add(m)
        }

        if (prices.isEmpty() || dists.size < 2 || times.size < 2) return false

        prices.sortDescending()
        dists.sortDescending()
        times.sortDescending()

        val finalPrice = prices[0]
        val finalDist = dists[0] + dists[1]
        
        var finalTime = 0.0
        if (times.size >= 3) finalTime = times[0] + times[1] + times[2]
        else finalTime = times[0] + times[1]

        if (finalPrice > 0 && finalDist > 0 && finalTime > 0) {
            lastValidReadTime = System.currentTimeMillis()

            if (abs(finalPrice - lastPrice) > 0.1 || abs(finalDist - lastDist) > 0.1) {
                lastPrice = finalPrice
                lastDist = finalDist

                val valPerKm = if (finalDist > 0) finalPrice / finalDist else 0.0
                val valPerHour = if (finalTime > 0) (finalPrice / finalTime) * 60 else 0.0

                var color = Color.parseColor("#FACC15")
                var message = "MÉDIA. ANALISE BEM 🤔"
                var bgAlpha = "#33FACC15"

                if (valPerKm >= goodKm && valPerHour >= goodHour) {
                    color = Color.parseColor("#4ADE80")
                    message = "BOA! ACEITA LOGO 🚀"
                    bgAlpha = "#334ADE80"
                } else if (valPerKm <= badKm && valPerHour <= badHour) {
                    color = Color.parseColor("#F87171")
                    message = "PREJUÍZO! PULA FORA 🛑"
                    bgAlpha = "#33F87171"
                }
                
                val bgDica = GradientDrawable().apply { cornerRadius = 15f; setColor(Color.parseColor(bgAlpha)) }
                showCard(finalPrice, finalDist, finalTime, valPerKm, valPerHour, color, message, bgDica)

                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", finalPrice); intent.putExtra("dist", finalDist); intent.putExtra("time", finalTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            return true
        }
        return false
    }

    override fun onDestroy() {
        // Correção aqui: super.onDestroy() e removemos referência ao controlsView
        super.onDestroy()
        isServiceRunning = false
        try { 
            if (bubbleView != null) windowManager.removeView(bubbleView)
            if (infoCardView != null) windowManager.removeView(infoCardView)
            // if (controlsView != null) windowManager.removeView(controlsView) // Removido pois não existe nessa versão
        } catch (e: Exception) {}
        try { virtualDisplay?.release(); mediaProjection?.stop(); recognizer.close() } catch (e: Exception) {}
        LocalBroadcastManager.getInstance(this).unregisterReceiver(configReceiver)
    }
}
