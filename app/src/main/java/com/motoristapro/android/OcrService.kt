package com.motoristapro.android

import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.graphics.Color
import android.graphics.Outline
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Environment
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewOutlineProvider
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.NotificationCompat
import org.json.JSONArray
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.regex.Pattern
import kotlin.math.abs

class OcrService : Service() {

    private lateinit var windowManager: WindowManager
    private val autoHideHandler = Handler(Looper.getMainLooper())
    private val autoHideRunnable = Runnable { hideCard() }
    
    private val AUTO_HIDE_DELAY = 7000L 

    private var bubbleView: View? = null
    private var menuView: View? = null
    private var settingsView: View? = null
    private var infoCardView: LinearLayout? = null
    private var iconView: ImageView? = null
    
    private var tvMenuPauseTitle: TextView? = null
    private var tvMenuPauseIcon: TextView? = null
    
    private lateinit var tvAppBadge: TextView
    private lateinit var tvValorTopo: TextView
    private lateinit var tvDadosMeio: TextView
    private lateinit var tvResultadosBaixo: TextView
    private lateinit var tvDicaAcao: TextView
    
    private lateinit var etGoodKm: EditText
    private lateinit var etBadKm: EditText
    private lateinit var etGoodHour: EditText
    private lateinit var etBadHour: EditText

    private var goodKm: Double = 2.0
    private var badKm: Double = 1.5
    private var goodHour: Double = 60.0
    private var badHour: Double = 40.0
    
    private var isMonitoring: Boolean = true
    private var isMenuOpen: Boolean = false
    private var isSettingsOpen: Boolean = false
    
    private lateinit var bubbleParams: WindowManager.LayoutParams
    private lateinit var menuParams: WindowManager.LayoutParams
    private lateinit var settingsParams: WindowManager.LayoutParams
    private lateinit var cardParams: WindowManager.LayoutParams

    // --- CONTROLE DE DUPLICIDADE ---
    data class RideData(val price: Double, val dist: Double, val time: Double)
    private var lastRideData: RideData? = null

    private val hideCardReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (infoCardView?.visibility == View.VISIBLE) {
                infoCardView?.visibility = View.GONE
                bubbleView?.visibility = View.GONE 
            }
            lastRideData = null
        }
    }
    
    private val textReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val jsonData = intent?.getStringExtra("JSON_DATA")
            val pkg = intent?.getStringExtra("APP_PACKAGE") ?: ""
            val screenH = intent?.getIntExtra("SCREEN_HEIGHT", 2000) ?: 2000
            
            if (!jsonData.isNullOrEmpty()) {
                analyzeSmartData(jsonData, pkg, screenH)
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        loadConfigs()
        saveLog("LIFECYCLE: OcrService Iniciado.")
        
        val filterText = IntentFilter("ACTION_PROCESS_TEXT")
        val filterHide = IntentFilter("com.motoristapro.ACTION_HIDE_CARD")

        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(textReceiver, filterText, Context.RECEIVER_EXPORTED)
            registerReceiver(hideCardReceiver, filterHide, Context.RECEIVER_EXPORTED)
        } else {
            registerReceiver(textReceiver, filterText)
            registerReceiver(hideCardReceiver, filterHide)
        }
        
        try {
            startForegroundServiceCompat()
            createBubble()
            createMenu()
            createSettingsView()
            createInfoCard()
            saveLog("--- ROBÔ INICIADO (LOGS ATIVOS EM DOWNLOADS) ---")
        } catch (e: Exception) { e.printStackTrace() }
    }

    // =========================================================================
    // FUNÇÃO DE LOG (SALVA NA PASTA DOWNLOADS)
    // =========================================================================
    private fun saveLog(msg: String) {
        // 1. Logcat (Sistema)
        try { android.util.Log.i("MotoristaPro_OCR", msg) } catch (e: Exception) {}

        // 2. Arquivo TXT (Downloads)
        try {
            val time = SimpleDateFormat("dd/MM HH:mm:ss", Locale.getDefault()).format(Date())
            val line = "[$time] $msg\n"
            
            val path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            val file = File(path, "motorista_pro_logs.txt")
            
            // Cria se não existir
            if (!file.exists()) {
                file.createNewFile()
            }
            
            // Escreve no final do arquivo (append = true)
            val writer = FileWriter(file, true)
            writer.append(line)
            writer.flush()
            writer.close()
        } catch (e: Exception) {
            android.util.Log.e("MotoristaPro_OCR", "Erro ao salvar log no arquivo: ${e.message}")
        }
    }

    private fun startForegroundServiceCompat() {
        val channelId = "ocr_service_channel"
        val channel = NotificationChannel(channelId, "Motorista Pro", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        val stopIntent = Intent(this, OcrService::class.java).apply { action = "STOP_SERVICE" }
        val stopPendingIntent = PendingIntent.getService(this, 0, stopIntent, PendingIntent.FLAG_IMMUTABLE)
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Motorista Pro")
            .setSmallIcon(R.mipmap.ic_launcher)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Parar", stopPendingIntent)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        } else {
            startForeground(1, notification)
        }
    }

    private fun sanitizeOcrErrors(input: String): String {
        var text = input.lowercase().replace("\n", " ").replace(",", ".")
        text = text.replace(Regex("m[1i]nut[o0]5?"), "min")
                   .replace(Regex("m[1i]n"), "min")
        if (text.contains("km") || text.contains("min") || text.contains("m ") || text.contains("h")) {
            text = text.replace("o", "0")
                       .replace("l", "1")
                       .replace("i", "1")
                       .replace("s", "5")
                       .replace("b", "8")
        }
        return text
    }

    private fun analyzeSmartData(jsonString: String, pkgName: String, screenHeight: Int) {
        try {
            if (!isMonitoring) return

            val blocks = JSONArray(jsonString)
            var bestPrice = 0.0
            var maxPriceFontSize = 0
            
            // Variáveis para evitar duplicidade de soma no mesmo frame
            var pickupDist = 0.0
            var tripDist = 0.0
            var pickupTime = 0.0
            var tripTime = 0.0
            
            val detectedApp = if (pkgName.contains("taxis99") || pkgName.contains("didi") || pkgName.contains("99")) "99" else "UBER"
            val ignoreTopLimit = screenHeight * 0.10

            // saveLog("\n=== NOVA LEITURA ($detectedApp) ===")

            for (i in 0 until blocks.length()) {
                val obj = blocks.getJSONObject(i)
                val rawText = obj.getString("text")
                val h = obj.getInt("h")
                val y = obj.getInt("y")
                
                if (y < ignoreTopLimit) continue

                val cleanText = sanitizeOcrErrors(rawText)

                // --- FILTROS DE SEGURANÇA (ANTI-ESPELHO) ---
                // Ignora textos que parecem ser logs do próprio sistema ou notificações
                if (cleanText.startsWith("[") && cleanText.contains("]")) continue // Ignora timestamp de log
                if (cleanText.contains("lido:") || cleanText.contains("limpo:") || cleanText.contains("conclusão:")) continue
                if (cleanText.contains("candidato") || cleanText.contains("detectada:")) continue
                if (cleanText.contains("motorista pro") || cleanText.contains("configurações")) continue
                
                // Filtros de palavras irrelevantes dos apps
                if (cleanText.contains("ganhe r$") || cleanText.contains("meta de ganhos")) continue
                if (cleanText.contains("r$/km") || cleanText.contains("r$/h")) continue // Evita ler o card flutuante antigo

                // A. PREÇO (Lógica Mantida)
                val matPrice = Pattern.compile("(?:r\\$|rs)\\s*([0-9]+(?:\\.[0-9]{2})?)").matcher(cleanText)
                if (matPrice.find()) {
                    val v = matPrice.group(1)?.toDoubleOrNull() ?: 0.0
                    if (v > 4.5 && v < 2000.0) { // Preço máximo razoável
                        if (h > maxPriceFontSize) {
                            maxPriceFontSize = h; bestPrice = v
                        } else if (h == maxPriceFontSize && v > bestPrice) {
                            bestPrice = v
                        }
                    }
                }
                // Fallback Preço (Numero isolado grande)
                if (bestPrice == 0.0 && h > 75) { // Reduzi um pouco a altura mínima
                     val matPrice2 = Pattern.compile("^([0-9]+(?:\\.[0-9]{2}))$").matcher(cleanText.trim())
                     if (matPrice2.find()) {
                         val v = matPrice2.group(1)?.toDoubleOrNull() ?: 0.0
                         if (v > 5.0 && v < 600.0) { 
                             bestPrice = v; maxPriceFontSize = h 
                         }
                     }
                }

                // B. DISTÂNCIA (Lógica Refinada: Separa Pickup de Trip)
                // O padrão da Uber geralmente coloca a distância de busca antes (Y menor) ou depois. 
                // Mas para simplificar, vamos somar apenas valores razoáveis e não repetidos.
                val matDist = Pattern.compile("\\(?([0-9]+(?:\\.[0-9]+)?)\\s*(km|m)\\)?").matcher(cleanText)
                while (matDist.find()) {
                    val valStr = matDist.group(1) ?: "0"
                    val unit = matDist.group(2) ?: "km"
                    var value = valStr.toDoubleOrNull() ?: 0.0
                    if (unit == "m") value /= 1000.0
                    
                    if (value > 0.0 && value < 800.0) { // Limite de 800km para evitar erros bizarros
                        // Se for a primeira distância encontrada, assume busca ou viagem
                        if (pickupDist == 0.0) pickupDist = value
                        else if (tripDist == 0.0) tripDist = value
                        else {
                            // Se já tem 2 distâncias, pode ser um erro de leitura duplicada ou uma terceira parada
                            // Vamos somar apenas se for diferente das anteriores para evitar ler a mesma linha 2x
                            if (value != pickupDist && value != tripDist) {
                                tripDist += value
                            }
                        }
                        // saveLog("  -> DIST: $value km (Raw: $valStr $unit)")
                    }
                }

                // C. TEMPO
                var textForTime = cleanText.replace(Regex("\\d{1,2}:\\d{2}"), " ") // Remove horas tipo 12:30
                
                // Horas
                val matHour = Pattern.compile("(\\d+)\\s*(?:h|hr|hrs|hora|horas)\\b")
                val mHour = matHour.matcher(textForTime)
                while (mHour.find()) {
                    val hVal = mHour.group(1)?.toDoubleOrNull() ?: 0.0
                    if (hVal > 0 && hVal < 24) { 
                        if (pickupTime == 0.0) pickupTime = hVal * 60
                        else tripTime += hVal * 60
                    }
                }
                
                // Minutos
                val matMin = Pattern.compile("(\\d+)\\s*(?:min|minutos|m1n|m1ns|mins)(?!in|etro|l|e|a|o)")
                val mMin = matMin.matcher(textForTime)
                while (mMin.find()) {
                    val mVal = mMin.group(1)?.toDoubleOrNull() ?: 0.0
                    if (mVal > 0 && mVal < 600) { 
                        // Adiciona aos minutos (se já tiver horas no pickupTime, soma lá, senão tripTime)
                        // Logica simplificada: Soma tudo no final, mas tenta evitar duplicatas exatas na mesma linha
                        if (tripTime == 0.0 && pickupTime > 0) tripTime += mVal
                        else if (pickupTime == 0.0) pickupTime = mVal
                        else tripTime += mVal
                    }
                }
            }

            // D. CONSOLIDAÇÃO
            val totalDist = pickupDist + tripDist
            val totalTime = pickupTime + tripTime

            // E. VALIDAÇÃO FINAL
            if (bestPrice > 0.0) {
                // saveLog("PARCIAL: R$ $bestPrice | Dist: $pickupDist + $tripDist | Tempo: $pickupTime + $tripTime")
                
                if ((totalDist > 0.0) || (totalTime > 0.0)) {
                    val currentReading = RideData(bestPrice, totalDist, totalTime)
                    
                    // Anti-Duplicidade de evento (mesma tela processada várias vezes)
                    if (lastRideData != null && lastRideData == currentReading) {
                        return
                    }
                    lastRideData = currentReading

                    val safeDist = if (totalDist == 0.0) 0.1 else totalDist
                    val safeTime = if (totalTime == 0.0) 1.0 else totalTime 
                    val valPerKm = bestPrice / safeDist
                    val valPerHour = (bestPrice / safeTime) * 60.0
                    
                    saveLog("SUCESSO: R$ $bestPrice | $totalDist km | $totalTime min")
                    
                    val resultStyle = if (valPerKm >= goodKm && valPerHour >= goodHour) {
                        Triple(Color.parseColor("#4ADE80"), "ÓTIMA 🚀", "#334ADE80")
                    } else if (valPerKm <= badKm && valPerHour <= badHour) {
                        Triple(Color.parseColor("#F87171"), "RECUSAR 🛑", "#33F87171")
                    } else {
                        Triple(Color.parseColor("#FACC15"), "ANALISAR 🤔", "#33FACC15")
                    }
                    
                    val (finalColor, finalMsg, finalAlpha) = resultStyle
                    val bgDica = GradientDrawable().apply { cornerRadius = 15f; setColor(Color.parseColor(finalAlpha)) }
                    
                    showCard(bestPrice, totalDist, totalTime, valPerKm, valPerHour, finalColor, finalMsg, bgDica, detectedApp)
                }
            }

        } catch (e: Exception) { 
            e.printStackTrace()
            // saveLog("ERRO: ${e.message}")
        }
    }

    private fun showCard(price: Double, dist: Double, time: Double, valKm: Double, valHora: Double, color: Int, msg: String, bgDica: Drawable, detectedApp: String) {
        Handler(Looper.getMainLooper()).post {
            autoHideHandler.removeCallbacks(autoHideRunnable)
            
            bubbleView?.visibility = View.GONE
            infoCardView?.visibility = View.VISIBLE
            
            val badgeBg = GradientDrawable().apply { cornerRadius = 10f }

            if (detectedApp == "UBER") {
                tvAppBadge.visibility = View.VISIBLE; tvAppBadge.text = "UBER"; tvAppBadge.setTextColor(Color.WHITE); badgeBg.setColor(Color.BLACK)
            } else if (detectedApp == "99") {
                tvAppBadge.visibility = View.VISIBLE; tvAppBadge.text = "99"; tvAppBadge.setTextColor(Color.BLACK); badgeBg.setColor(Color.parseColor("#F7C948"))
            } else {
                tvAppBadge.visibility = View.GONE
            }

            tvAppBadge.background = badgeBg
            tvValorTopo.text = String.format("R$ %.2f", price)
            tvValorTopo.setTextColor(color) 
            
            tvDadosMeio.text = String.format("%.1f km • %.0f min", dist, time)
            tvResultadosBaixo.text = String.format("R$ %.2f/km • R$ %.0f/h", valKm, valHora)
            tvResultadosBaixo.setTextColor(color)
            tvDicaAcao.text = msg
            tvDicaAcao.setTextColor(color)
            tvDicaAcao.background = bgDica
            
            autoHideHandler.postDelayed(autoHideRunnable, AUTO_HIDE_DELAY)
        }
    }
    
    private fun hideCard() { 
        Handler(Looper.getMainLooper()).post { 
            autoHideHandler.removeCallbacks(autoHideRunnable)
            infoCardView?.visibility = View.GONE
            if (isMonitoring) bubbleView?.visibility = View.VISIBLE 
            lastRideData = null 
        } 
    }
    
    private fun createInfoCard() {
        val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
        val savedX = prefs.getInt("card_x", 0)
        val savedY = prefs.getInt("card_y", 100)
        infoCardView = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(30, 25, 30, 25); visibility = View.GONE; background = GradientDrawable().apply { cornerRadius = 40f; setColor(Color.parseColor("#E6334155")); setStroke(2, Color.parseColor("#33FFFFFF")) } }
        tvAppBadge = TextView(this).apply { text="APP"; setTextColor(Color.WHITE); gravity=Gravity.CENTER; textSize=10f; typeface=Typeface.DEFAULT_BOLD; setPadding(20,5,20,5); layoutParams=LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply { gravity=Gravity.CENTER_HORIZONTAL; bottomMargin=10 } }
        tvValorTopo = TextView(this).apply { text="--"; textSize=26f; setTextColor(Color.WHITE); typeface=Typeface.DEFAULT_BOLD; gravity=Gravity.CENTER }
        tvDadosMeio = TextView(this).apply { text="--"; textSize=14f; setTextColor(Color.LTGRAY); gravity=Gravity.CENTER }
        tvResultadosBaixo = TextView(this).apply { text="--"; textSize=18f; typeface=Typeface.DEFAULT_BOLD; gravity=Gravity.CENTER }
        tvDicaAcao = TextView(this).apply { text="..."; textSize=14f; typeface=Typeface.DEFAULT_BOLD; gravity=Gravity.CENTER; setPadding(10,5,10,5) }
        infoCardView!!.addView(tvAppBadge); infoCardView!!.addView(tvValorTopo); infoCardView!!.addView(tvDadosMeio); infoCardView!!.addView(tvResultadosBaixo); infoCardView!!.addView(tvDicaAcao)
        cardParams = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT).apply { gravity = Gravity.TOP or Gravity.START; x = savedX; y = savedY; width = (resources.displayMetrics.widthPixels * 0.65).toInt() }
        
        infoCardView!!.setOnTouchListener(object : View.OnTouchListener {
            private var iX=0; private var iY=0; private var iTX=0f; private var iTY=0f; private var isDrag=false
            override fun onTouch(v: View?, event: MotionEvent?): Boolean {
                if (event == null) return false
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> { iX = cardParams.x; iY = cardParams.y; iTX = event.rawX; iTY = event.rawY; isDrag = false; return true }
                    MotionEvent.ACTION_MOVE -> { val dx = (event.rawX - iTX).toInt(); val dy = (event.rawY - iTY).toInt(); if (abs(dx) > 10 || abs(dy) > 10) { isDrag = true; cardParams.x = iX + dx; cardParams.y = iY + dy; windowManager.updateViewLayout(infoCardView, cardParams) }; return true }
                    MotionEvent.ACTION_UP -> { if (isDrag) { prefs.edit().putInt("card_x", cardParams.x).putInt("card_y", cardParams.y).apply() } else { hideCard() }; return true }
                }
                return false
            }
        })
        windowManager.addView(infoCardView, cardParams)
    }

    private fun toggleMonitoring() { isMonitoring = !isMonitoring; iconView?.alpha = if(isMonitoring) 1f else 0.5f; if(!isMonitoring) hideCard(); Toast.makeText(this, if(isMonitoring) "Ativo" else "Pausado", Toast.LENGTH_SHORT).show() }
    private fun toggleMenu() { if(isMenuOpen) closeMenu() else openMenu() }
    private fun openSettings() { isSettingsOpen = true; settingsView!!.visibility = View.VISIBLE; windowManager.updateViewLayout(settingsView, settingsParams) }
    private fun closeSettings() { isSettingsOpen = false; settingsView!!.visibility = View.GONE }
    private fun openMenu() { 
        isMenuOpen = true; menuParams.x = bubbleParams.x; menuParams.y = bubbleParams.y + bubbleView!!.height + 15
        if (isMonitoring) { tvMenuPauseTitle?.text = "Pausar Leitura"; tvMenuPauseIcon?.text = "⏸" } else { tvMenuPauseTitle?.text = "Retomar Leitura"; tvMenuPauseIcon?.text = "▶️" }
        menuView!!.visibility = View.VISIBLE; windowManager.updateViewLayout(menuView, menuParams); Handler(Looper.getMainLooper()).postDelayed({ if (isMenuOpen) closeMenu() }, 5000) 
    }
    private fun closeMenu() { isMenuOpen = false; menuView!!.visibility = View.GONE }
    private fun openApp(target: String) { try { val i = packageManager.getLaunchIntentForPackage(packageName); i?.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); startActivity(i); closeMenu() } catch (e: Exception) { Toast.makeText(this, "Erro", Toast.LENGTH_SHORT).show() } }

    private fun createBubble() {
        val bubbleLayout = FrameLayout(this)
        iconView = ImageView(this).apply { setImageResource(R.mipmap.ic_launcher_round); scaleType = ImageView.ScaleType.CENTER_CROP; clipToOutline = true; outlineProvider = object : ViewOutlineProvider() { override fun getOutline(view: View, outline: Outline) { outline.setOval(0, 0, view.width, view.height) } }; elevation = 20f }
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(150, 150))
        bubbleLayout.setOnTouchListener(object : View.OnTouchListener {
            private var iX=0; private var iY=0; private var iTX=0f; private var iTY=0f; private var drag=false
            override fun onTouch(v: View?, e: MotionEvent?): Boolean {
                when(e!!.action) {
                    MotionEvent.ACTION_DOWN->{iX=bubbleParams.x;iY=bubbleParams.y;iTX=e.rawX;iTY=e.rawY;drag=false;return true}
                    MotionEvent.ACTION_MOVE->{val dx=(e.rawX-iTX).toInt();val dy=(e.rawY-iTY).toInt();if(abs(dx)>10||abs(dy)>10){drag=true;bubbleParams.x=iX+dx;bubbleParams.y=iY+dy;windowManager.updateViewLayout(bubbleView,bubbleParams);if(isMenuOpen)closeMenu()};return true}
                    MotionEvent.ACTION_UP->{if(!drag)toggleMenu();return true}
                }
                return false
            }
        })
        bubbleView = bubbleLayout
        bubbleParams = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT).apply { gravity = Gravity.TOP or Gravity.START; x = 20; y = 300 }
        windowManager.addView(bubbleView, bubbleParams)
    }

    private fun createMenu() {
        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(0, 20, 0, 20); background = GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = 30f; setStroke(1, Color.parseColor("#E2E8F0")) }; elevation = 40f }
        layout.addView(TextView(this).apply { text = "MOTORISTA PRO"; textSize = 12f; setTextColor(Color.parseColor("#64748B")); typeface = Typeface.DEFAULT_BOLD; gravity = Gravity.CENTER; setPadding(0, 10, 0, 25) })
        layout.addView(View(this).apply { layoutParams = LinearLayout.LayoutParams(-1, 2); setBackgroundColor(Color.parseColor("#F1F5F9")) })
        val btnPause = createMenuItem("⏯", "Pausar Leitura", Color.parseColor("#0F172A")) { toggleMonitoring(); closeMenu() }
        tvMenuPauseIcon = btnPause.getChildAt(0) as TextView; tvMenuPauseTitle = btnPause.getChildAt(1) as TextView; layout.addView(btnPause)
        layout.addView(createMenuItem("⚙️", "Configurações", Color.parseColor("#0F172A")) { closeMenu(); openSettings() })
        layout.addView(createMenuItem("📱", "Abrir Aplicativo", Color.parseColor("#2563EB")) { openApp("home"); closeMenu() })
        layout.addView(View(this).apply { layoutParams = LinearLayout.LayoutParams(-1, 2).apply { setMargins(40, 15, 40, 15) }; setBackgroundColor(Color.parseColor("#F1F5F9")) })
        layout.addView(createMenuItem("❌", "Encerrar Tudo", Color.parseColor("#EF4444")) { stopSelf() })
        menuView = layout
        menuParams = WindowManager.LayoutParams(600, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT).apply { gravity = Gravity.TOP or Gravity.START }
        menuView!!.visibility = View.GONE
        windowManager.addView(menuView, menuParams)
    }
    
    private fun createMenuItem(icon: String, text: String, textColor: Int, onClick: () -> Unit): LinearLayout {
        val container = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; setPadding(50, 35, 50, 35); isClickable = true; setBackgroundColor(Color.TRANSPARENT); setOnClickListener { onClick() } }
        val tvIcon = TextView(this).apply { this.text = icon; textSize = 20f; setPadding(0, 0, 40, 0); setTextColor(textColor) }
        val tvText = TextView(this).apply { this.text = text; textSize = 15f; setTextColor(textColor); typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL) }
        container.addView(tvIcon); container.addView(tvText)
        return container
    }

    private fun createSettingsView() {
        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(50, 50, 50, 50); background = GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = 45f } }
        val txtExpl = TextView(this).apply { text="COMO FUNCIONA A LÓGICA DE CORES:\n\n🟢 VERDE: Se (R$/KM >= Meta) E (R$/H >= Meta)\n🔴 VERMELHO: Se (R$/KM <= Ruim) E (R$/H <= Ruim)\n🟡 AMARELO: Qualquer outra combinação mista."; textSize=12f; setTextColor(Color.parseColor("#64748B")); setPadding(0,0,0,30) }
        layout.addView(txtExpl)
        fun mkInp(t: String, v: Double): EditText { val et = EditText(this).apply { setText(v.toString()); inputType = 8194; setTextColor(Color.BLACK) }; layout.addView(TextView(this).apply { text = t; setTextColor(Color.GRAY) }); layout.addView(et); return et }
        etGoodKm = mkInp("KM Bom", goodKm); etBadKm = mkInp("KM Ruim", badKm); etGoodHour = mkInp("Hora Boa", goodHour); etBadHour = mkInp("Hora Ruim", badHour)
        val btnSave = Button(this).apply { text = "SALVAR"; setOnClickListener { saveConfigsLocally() } }; layout.addView(btnSave)
        settingsView = layout
        settingsParams = WindowManager.LayoutParams(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_DIM_BEHIND, PixelFormat.TRANSLUCENT).apply { dimAmount = 0.5f; gravity = Gravity.CENTER }
        settingsView!!.visibility = View.GONE
        windowManager.addView(settingsView, settingsParams)
    }

    private fun saveConfigsLocally() {
        try {
            val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
            goodKm = etGoodKm.text.toString().toDoubleOrNull() ?: 2.0; badKm = etBadKm.text.toString().toDoubleOrNull() ?: 1.5; goodHour = etGoodHour.text.toString().toDoubleOrNull() ?: 60.0; badHour = etBadHour.text.toString().toDoubleOrNull() ?: 40.0
            prefs.edit().putFloat("good_km", goodKm.toFloat()).putFloat("bad_km", badKm.toFloat()).putFloat("good_hour", goodHour.toFloat()).putFloat("bad_hour", badHour.toFloat()).apply()
            closeSettings(); Toast.makeText(this, "Salvo", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {}
    }
    
    private fun loadConfigs() {
        saveLog("Configs carregadas: KM Bom=$goodKm, Hora Boa=$goodHour")
        val prefs = getSharedPreferences("OCR_PREFS", Context.MODE_PRIVATE)
        goodKm = prefs.getFloat("good_km", 2.0f).toDouble(); badKm = prefs.getFloat("bad_km", 1.5f).toDouble(); goodHour = prefs.getFloat("good_hour", 60.0f).toDouble(); badHour = prefs.getFloat("bad_hour", 40.0f).toDouble()
    }

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(textReceiver)
        try { 
            if (bubbleView != null) windowManager.removeView(bubbleView)
            if (menuView != null) windowManager.removeView(menuView)
            if (settingsView != null) windowManager.removeView(settingsView)
            if (infoCardView != null) windowManager.removeView(infoCardView)
        } catch (e: Exception) {}
    }
}
