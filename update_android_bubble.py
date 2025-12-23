import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- 1. MAIN ACTIVITY ---
main_activity_content = """
package com.motoristapro.android

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.localbroadcastmanager.content.LocalBroadcastManager

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    inner class WebAppInterface(private val mContext: Context) {
        @JavascriptInterface
        fun requestPermission() {
            runOnUiThread { checkPermissionsAndStart() }
        }
        
        @JavascriptInterface
        fun updateConfig(minKm: Double, minHora: Double) {
            val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
            prefs.edit().putFloat("min_km", minKm.toFloat()).putFloat("min_hora", minHora.toFloat()).apply()
            val intent = Intent("OCR_CONFIG_UPDATED")
            LocalBroadcastManager.getInstance(mContext).sendBroadcast(intent)
            runOnUiThread { Toast.makeText(mContext, "Configurações atualizadas!", Toast.LENGTH_SHORT).show() }
        }
    }

    private val ocrReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == "OCR_DATA_DETECTED") {
                val price = intent.getDoubleExtra("price", 0.0)
                val dist = intent.getDoubleExtra("dist", 0.0)
                val time = intent.getDoubleExtra("time", 0.0)
                injectDataIntoSite(price, dist, time)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = FrameLayout(this)
        setContentView(root)

        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.databaseEnabled = true
        webView.settings.userAgentString = webView.settings.userAgentString + " MotoristaProApp"
        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                view?.loadUrl(url ?: return false)
                return true
            }
        }
        
        webView.loadUrl("https://refactored-space-tribble-v69ggpvvvj94hxprw-5000.app.github.dev")
        root.addView(webView)

        LocalBroadcastManager.getInstance(this).registerReceiver(ocrReceiver, IntentFilter("OCR_DATA_DETECTED"))
    }

    private fun injectDataIntoSite(price: Double, dist: Double, time: Double) {
        val currentUrl = webView.url ?: ""
        if (currentUrl.contains("/adicionar")) {
            val jsCommand = "if(window.MotoristaProBridge) { window.MotoristaProBridge.preencherDados($price, $dist, $time); }"
            webView.evaluateJavascript(jsCommand, null)
        }
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
        startProjectionRequest()
    }

    private fun startProjectionRequest() {
        val mpManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(mpManager.createScreenCaptureIntent(), REQUEST_MEDIA_PROJECTION)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_MEDIA_PROJECTION) {
            if (resultCode == RESULT_OK && data != null) {
                val serviceIntent = Intent(this, OcrService::class.java).apply {
                    putExtra("RESULT_CODE", resultCode)
                    putExtra("RESULT_DATA", data)
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    startForegroundService(serviceIntent)
                } else {
                    startService(serviceIntent)
                }
            } else {
                Toast.makeText(this, "Permissão negada.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onBackPressed() { if (webView.canGoBack()) webView.goBack() else super.onBackPressed() }
    override fun onDestroy() { super.onDestroy(); LocalBroadcastManager.getInstance(this).unregisterReceiver(ocrReceiver) }
}
"""

# --- 2. OCR SERVICE (BOLHA FLUTUANTE) ---
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
    private var bubbleView: View? = null
    private var infoCardView: LinearLayout? = null
    private var controlsView: LinearLayout? = null

    private lateinit var tvValorTopo: TextView
    private lateinit var tvDadosMeio: TextView
    private lateinit var tvResultadosBaixo: TextView

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    
    private var isRunning = false
    private var screenWidth = 0
    private var screenHeight = 0
    
    private var minKm = 2.0
    private var minHora = 60.0
    
    private var lastPrice = 0.0
    private var lastDist = 0.0
    private var sameFrameCount = 0

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

    private fun createBubble() {
        val bubbleLayout = FrameLayout(this)
        val icon = ImageView(this)
        icon.setImageResource(R.drawable.ic_launcher_foreground)
        val bg = GradientDrawable()
        bg.shape = GradientDrawable.OVAL
        bg.setColor(Color.parseColor("#2563EB"))
        bg.setStroke(2, Color.WHITE)
        icon.background = bg
        icon.setPadding(15,15,15,15)
        bubbleLayout.addView(icon, FrameLayout.LayoutParams(120, 120))
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.TOP or Gravity.START; params.x = 20; params.y = 200
        bubbleLayout.setOnClickListener { showControls() }
        bubbleView = bubbleLayout
        windowManager.addView(bubbleView, params)
    }

    private fun createControls() {
        controlsView = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(20, 10, 20, 10)
            visibility = View.GONE
            background = GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = 50f; setStroke(1, Color.LTGRAY) }
        }
        val btnStop = Button(this).apply { text = "PARAR"; textSize = 11f; setTextColor(Color.WHITE); background = GradientDrawable().apply { setColor(Color.RED); cornerRadius = 40f }; setOnClickListener { stopSelf() } }
        val btnClose = Button(this).apply { text = "FECHAR"; textSize = 11f; setTextColor(Color.GRAY); background = null; setOnClickListener { hideControls() } }
        controlsView!!.addView(btnStop, LinearLayout.LayoutParams(200, 100))
        controlsView!!.addView(btnClose, LinearLayout.LayoutParams(200, 100))
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.TOP or Gravity.START; params.x = 20; params.y = 200
        windowManager.addView(controlsView, params)
    }

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
        infoCardView!!.addView(tvValorTopo); infoCardView!!.addView(tvDadosMeio); infoCardView!!.addView(tvResultadosBaixo)
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        params.gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL; params.y = 80; params.width = (resources.displayMetrics.widthPixels * 0.90).toInt()
        windowManager.addView(infoCardView, params)
    }

    private fun showControls() { bubbleView?.visibility = View.GONE; controlsView?.visibility = View.VISIBLE }
    private fun hideControls() { controlsView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE }
    
    private fun showCard(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double) {
        Handler(Looper.getMainLooper()).post {
            bubbleView?.visibility = View.GONE; controlsView?.visibility = View.GONE; infoCardView?.visibility = View.VISIBLE
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvDadosMeio.text = String.format("%.1f km  •  %.0f min", dist, time)
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.2f/h", valKm, valHora)
            val color = when { valKm >= minKm -> Color.parseColor("#4ADE80"); valKm >= (minKm * 0.75) -> Color.parseColor("#FACC15"); else -> Color.parseColor("#F87171") }
            tvResultadosBaixo.setTextColor(color)
        }
    }
    
    private fun hideCard() { Handler(Looper.getMainLooper()).post { infoCardView?.visibility = View.GONE; bubbleView?.visibility = View.VISIBLE } }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val resultCode = intent?.getIntExtra("RESULT_CODE", 0) ?: 0
        val resultData = intent?.getParcelableExtra<Intent>("RESULT_DATA")
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
            while (isRunning) {
                var image = try { imageReader?.acquireLatestImage() } catch (e: Exception) { null }
                var shouldWait = false
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
                            while (!task.isComplete) { delay(50) }
                            if (task.isSuccessful) shouldWait = analyzeScreen(task.result.text)
                        }
                    } catch (e: Exception) { try { image.close() } catch (x: Exception) {} }
                }
                delay(if (shouldWait) 5000 else 1000)
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
            if (isSameAsLast(framePrice, frameDist)) {
                sameFrameCount++
                if (sameFrameCount >= 2) { hideCard(); return false }
                return true
            } else {
                sameFrameCount = 0; lastPrice = framePrice; lastDist = frameDist
                val valPerKm = if (frameDist > 0) framePrice / frameDist else 0.0
                val valPerHour = if (frameTime > 0) (framePrice / frameTime) * 60 else 0.0
                showCard(framePrice, frameDist, frameTime, valPerKm, valPerHour)
                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", framePrice); intent.putExtra("dist", frameDist); intent.putExtra("time", frameTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
                return true
            }
        } else { sameFrameCount = 0; hideCard(); return false }
    }

    private fun isSameAsLast(p: Double, d: Double): Boolean { return (abs(p - lastPrice) < 0.1 && abs(d - lastDist) < 0.5) }

    override fun onDestroy() {
        super.onDestroy(); isRunning = false
        try { if (bubbleView != null) windowManager.removeView(bubbleView); if (infoCardView != null) windowManager.removeView(infoCardView); if (controlsView != null) windowManager.removeView(controlsView) } catch (e: Exception) {}
        try { virtualDisplay?.release(); mediaProjection?.stop(); recognizer.close() } catch (e: Exception) {}
        LocalBroadcastManager.getInstance(this).unregisterReceiver(configReceiver)
    }
}
"""

print("--- Android Atualizado: Bolha e Configs ---")
create_file("app/src/main/java/com/motoristapro/android/MainActivity.kt", main_activity_content)
create_file("app/src/main/java/com/motoristapro/android/OcrService.kt", ocr_service_content)

print("\nConcluído!")
print("1. git add .")
print("2. git commit -m 'Feat: Bubble and Config'")
print("3. git push")


