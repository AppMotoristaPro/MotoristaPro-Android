import os
import shutil
import subprocess
import re
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
PROJETO = "MotoristaPro-Android"
ARQUIVO_ALVO = "app/src/main/java/com/motoristapro/android/OcrService.kt"
ARQUIVO_GRADLE = "app/build.gradle.kts"
DIRETORIO_BACKUP = "backup_automatico"

# ==============================================================================
# CÓDIGO FONTE LIMPO E CORRIGIDO (OCR SERVICE)
# ==============================================================================
# Este código inclui:
# 1. Imports corretos (Build, Context, IntentFilter)
# 2. Correção de segurança Android 14 (RECEIVER_EXPORTED)
# 3. Lógica original intacta
# ==============================================================================

CODIGO_OCR_COMPLETO = r"""package com.motoristapro.android

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

    // --- NOVO: CONTROLE DE DUPLICIDADE ---
    // Armazena os dados da última leitura válida
    data class RideData(val price: Double, val dist: Double, val time: Double)
    private var lastRideData: RideData? = null
    // -------------------------------------

    private val hideCardReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (infoCardView?.visibility == View.VISIBLE) {
                infoCardView?.visibility = View.GONE
                bubbleView?.visibility = View.GONE 
            }
            // Reseta a última leitura ao esconder
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
        Logger.log("LIFECYCLE", "OcrService Iniciado.")
        
        // --- CORREÇÃO ANDROID 14 (API 34) ---
        // O Android 14 exige flag EXPORTED/NOT_EXPORTED para receivers dinâmicos
        
        val filterText = IntentFilter("ACTION_PROCESS_TEXT")
        val filterHide = IntentFilter("com.motoristapro.ACTION_HIDE_CARD")

        if (Build.VERSION.SDK_INT >= 33) {
            // Context.RECEIVER_EXPORTED é exigido para receivers que recebem broadcasts do sistema ou de outros apps
            // Como usamos broadcasts personalizados, precisamos definir
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
            saveLog("--- ROBÔ INICIADO ---")
        } catch (e: Exception) { e.printStackTrace() }
    }

    private fun saveLog(msg: String) { 
        try { android.util.Log.i("MotoristaPro_OCR", msg) } catch (e: Exception) {} 
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
        Logger.log("ENGINE", "Iniciando análise de dados OCR...")
        try {
            if (!isMonitoring) return

            val blocks = JSONArray(jsonString)
            var bestPrice = 0.0
            var maxPriceFontSize = 0
            var totalDist = 0.0
            var totalTime = 0.0
            
            val detectedApp = if (pkgName.contains("taxis99") || pkgName.contains("didi") || pkgName.contains("99")) "99" else "UBER"
            val ignoreTopLimit = screenHeight * 0.10

            for (i in 0 until blocks.length()) {
                val obj = blocks.getJSONObject(i)
                val rawText = obj.getString("text")
                val h = obj.getInt("h")
                val y = obj.getInt("y")
                
                if (y < ignoreTopLimit) continue

                val cleanText = sanitizeOcrErrors(rawText)

                if (cleanText.contains("ganhe r$") || cleanText.contains("a mais por") || cleanText.contains("viagens e ganhe") || cleanText.contains("meta de ganhos")) continue
                if (cleanText.contains("r$/km") || cleanText.contains("r$/h") || cleanText.contains("5h0wr00m") || cleanText.contains("showroom")) continue
                if (cleanText.contains("ma15 de 30") || cleanText.contains("mais de 30") || cleanText.contains("ma1s de 30")) continue
                if (cleanText.contains("mapa de chamada") || cleanText.contains("chamadas") || cleanText == "30 m") continue
                
                // A. PREÇO - FIX REGEX STRING ESCAPES
                val matPrice = Pattern.compile("(?:r\\$|rs)\\s*([0-9]+(?:\\.[0-9]{2})?)").matcher(cleanText)
                if (matPrice.find()) {
                    val v = matPrice.group(1)?.toDoubleOrNull() ?: 0.0
                    if (v > 4.5) {
                        if (h > maxPriceFontSize) {
                            maxPriceFontSize = h; bestPrice = v
                        } else if (h == maxPriceFontSize && v > bestPrice) {
                            bestPrice = v
                        }
                    }
                }
                if (bestPrice == 0.0 && h > 80) {
                     // FIX REGEX
                     val matPrice2 = Pattern.compile("^([0-9]+(?:\\.[0-9]{2}))$").matcher(cleanText.trim())
                     if (matPrice2.find()) {
                         val v = matPrice2.group(1)?.toDoubleOrNull() ?: 0.0
                         if (v > 5.0 && v < 500.0) { bestPrice = v; maxPriceFontSize = h }
                     }
                }

                // B. DISTÂNCIA - FIX REGEX
                val matDist = Pattern.compile("\\(?([0-9]+(?:\\.[0-9]+)?)\\s*(km|m)\\)?").matcher(cleanText)
                while (matDist.find()) {
                    val valStr = matDist.group(1) ?: "0"
                    val unit = matDist.group(2) ?: "km"
                    var value = valStr.toDoubleOrNull() ?: 0.0
                    if (unit == "m") value /= 1000.0
                    if (value > 0.1 && value < 300.0) { totalDist += value }
                }

                // C. TEMPO - FIX REGEX
                var textForTime = cleanText.replace(Regex("\\d{1,2}:\\d{2}"), " ")
                val matHour = Pattern.compile("(\\d+)\\s*(?:h|hr|hrs|hora|horas)\\b")
                val mHour = matHour.matcher(textForTime)
                while (mHour.find()) {
                    val hVal = mHour.group(1)?.toDoubleOrNull() ?: 0.0
                    if (hVal > 0 && hVal < 24) { totalTime += (hVal * 60) }
                }
                val matMin = Pattern.compile("(\\d+)\\s*(?:min|minutos|m1n|m1ns|mins)(?!in|etro|l|e|a|o)")
                val mMin = matMin.matcher(textForTime)
                while (mMin.find()) {
                    val mVal = mMin.group(1)?.toDoubleOrNull() ?: 0.0
                    if (mVal > 0 && mVal < 600) { totalTime += mVal }
                }
            }

            // D. VALIDAÇÃO E ANTI-DUPLICIDADE
            val isValidReading = (bestPrice > 0.0) && ((totalDist > 0.0) || (totalTime > 0.0))
            
            if (isValidReading) {
                // --- NOVA LÓGICA: Verifica se é a mesma leitura anterior ---
                val currentReading = RideData(bestPrice, totalDist, totalTime)
                
                if (lastRideData != null) {
                    if (lastRideData == currentReading) {
                        Logger.log("FILTER", "Leitura duplicada ignorada: R$$bestPrice")
                        return // <--- SAI AQUI SE FOR IGUAL
                    }
                }
                
                // Se for diferente, atualiza o último e exibe
                lastRideData = currentReading
                // -----------------------------------------------------------

                val safeDist = if (totalDist == 0.0) 0.1 else totalDist
                val safeTime = if (totalTime == 0.0) 1.0 else totalTime 

                val valPerKm = bestPrice / safeDist
                val valPerHour = (bestPrice / safeTime) * 60.0
                
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

        } catch (e: Exception) { e.printStackTrace() }
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
            // Reseta a duplicidade após timeout para permitir ler de novo se necessário
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
        Logger.log("LIFECYCLE", "OcrService Iniciado. Configs carregadas: KM Bom=$goodKm, Hora Boa=$goodHour")
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
"""

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def log(msg, cor="36"): # 36 = Cyan
    print(f"\033[{cor}m[{PROJETO}] {msg}\033[0m")

def criar_backup(arquivo):
    if not os.path.exists(DIRETORIO_BACKUP):
        os.makedirs(DIRETORIO_BACKUP)
    
    if os.path.exists(arquivo):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_orig = os.path.basename(arquivo)
        destino = os.path.join(DIRETORIO_BACKUP, f"{nome_orig}_{timestamp}.bak")
        shutil.copy2(arquivo, destino)
        log(f"Backup salvo: {destino}")

def git_push(msg):
    try:
        log("Executando Git Push...", "33")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Git Push Concluído.", "32")
    except:
        log("Erro no Git Push.", "31")

def atualizar_versao():
    """Incrementa versionCode"""
    if not os.path.exists(ARQUIVO_GRADLE): return None

    with open(ARQUIVO_GRADLE, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    match_code = re.search(r'(versionCode\s*=\s*)(\d+)', conteudo)
    novo_code = 0
    if match_code:
        novo_code = int(match_code.group(2)) + 1
        conteudo = re.sub(r'(versionCode\s*=\s*)(\d+)', fr'\g<1>{novo_code}', conteudo)
    
    match_name = re.search(r'(versionName\s*=\s*")([^"]+)(")', conteudo)
    if match_name:
        try:
            parts = match_name.group(2).split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            new_name = ".".join(parts)
            conteudo = re.sub(r'(versionName\s*=\s*")([^"]+)(")', fr'\g<1>{new_name}\g<3>', conteudo)
        except:
            pass

    with open(ARQUIVO_GRADLE, 'w', encoding='utf-8') as f:
        f.write(conteudo)
        
    return novo_code

# ==============================================================================
# RESTAURAÇÃO TOTAL
# ==============================================================================

def restaurar_arquivo_ocr():
    # 1. Faz backup do arquivo atual (mesmo que quebrado)
    criar_backup(ARQUIVO_ALVO)
    
    # 2. Sobrescreve com o código limpo
    try:
        with open(ARQUIVO_ALVO, 'w', encoding='utf-8') as f:
            f.write(CODIGO_OCR_COMPLETO)
        log(f"Arquivo OcrService.kt restaurado com sucesso! (Correção Android 14 aplicada)", "32")
        return True
    except Exception as e:
        log(f"Erro ao salvar arquivo: {e}", "31")
        return False

# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    print("-" * 50)
    log("Iniciando Restauração Total do OcrService...", "36")
    
    if restaurar_arquivo_ocr():
        novo_code = atualizar_versao()
        if novo_code:
            git_push(f"Full Restore OcrService + Fix Android 14 - v{novo_code}")
        
    # Auto-destruição
    try:
        os.remove(__file__)
        log("Script removido.", "32")
    except:
        pass
        
    print("-" * 50)


