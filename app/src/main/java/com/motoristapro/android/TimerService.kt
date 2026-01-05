package com.motoristapro.android

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.SystemClock
import android.widget.RemoteViews
import androidx.core.app.NotificationCompat

class TimerService : Service() {

    companion object {
        const val CHANNEL_ID = "TimerChannel"
        const val NOTIFICATION_ID = 1
        
        const val ACTION_START = "ACTION_START"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_RESUME = "ACTION_RESUME"
        const val ACTION_STOP = "ACTION_STOP"
        const val ACTION_SYNC = "ACTION_SYNC"
    }

    private var startTime: Long = 0L
    private var pausedTime: Long = 0L
    private var isRunning: Boolean = false

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action

        when (action) {
            ACTION_SYNC -> handleSync(intent)
            ACTION_START -> startTimer(System.currentTimeMillis())
            ACTION_PAUSE -> {
                pauseTimer()
                sendJsCommand("if(window.toggleTimer) window.toggleTimer();") 
            }
            ACTION_RESUME -> {
                resumeTimer()
                sendJsCommand("if(window.toggleTimer) window.toggleTimer();")
            }
            ACTION_STOP -> {
                stopTimer()
                sendJsCommand("if(window.stopTimer) window.stopTimer();")
            }
        }

        return START_NOT_STICKY
    }

    private fun handleSync(intent: Intent) {
        val state = intent.getStringExtra("state") ?: "stopped"
        val incomeStartTime = intent.getLongExtra("start_ts", 0L)
        val incomeElapsed = intent.getLongExtra("elapsed", 0L)

        if (state == "running") {
            val base = if (incomeStartTime > 0) incomeStartTime else System.currentTimeMillis()
            if (!isRunning || kotlin.math.abs(startTime - base) > 1000) {
                startTimer(base)
            }
        } else if (state == "paused") {
            pausedTime = incomeElapsed
            if (isRunning || pausedTime > 0) {
               pauseTimer(forceUpdate = true)
            }
        } else {
            stopTimer()
        }
    }

    private fun startTimer(baseTime: Long) {
        isRunning = true
        startTime = baseTime
        updateNotification()
    }

    private fun pauseTimer(forceUpdate: Boolean = false) {
        if (isRunning) {
            val now = System.currentTimeMillis()
            pausedTime = now - startTime
        }
        isRunning = false
        updateNotification()
    }

    private fun resumeTimer() {
        val now = System.currentTimeMillis()
        startTime = now - pausedTime
        isRunning = true
        updateNotification()
    }

    private fun stopTimer() {
        isRunning = false
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    // Envia comando JS para a MainActivity injetar na WebView
    private fun sendJsCommand(js: String) {
        val intent = Intent("wwebview.js_command")
        intent.putExtra("js", js)
        sendBroadcast(intent)
    }

    private fun updateNotification() {
        val notification = buildNotification()
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun buildNotification(): Notification {
        // Layout Customizado
        val remoteViews = RemoteViews(packageName, R.layout.notification_timer)
        
        // Configura o Intent de clique na notificação (abrir app)
        val openIntent = Intent(this, MainActivity::class.java)
        openIntent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
        val pOpen = PendingIntent.getActivity(this, 0, openIntent, PendingIntent.FLAG_IMMUTABLE)
        
        // Configura Botão Stop
        val stopIntent = Intent(this, TimerService::class.java).apply { action = ACTION_STOP }
        val pStop = PendingIntent.getService(this, 1, stopIntent, PendingIntent.FLAG_IMMUTABLE)
        remoteViews.setOnClickPendingIntent(R.id.btn_stop, pStop)

        // Lógica de UI (Play/Pause)
        if (isRunning) {
            remoteViews.setTextViewText(R.id.notif_title, "Em Rota")
            remoteViews.setImageViewResource(R.id.btn_toggle, android.R.drawable.ic_media_pause)
            
            // Configura Pause
            val pauseIntent = Intent(this, TimerService::class.java).apply { action = ACTION_PAUSE }
            val pPause = PendingIntent.getService(this, 2, pauseIntent, PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pPause)

            // Configura Cronômetro Rodando
            // Chronometer base precisa ser setado relativo ao SystemClock.elapsedRealtime()
            val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
            remoteViews.setChronometer(R.id.notif_chronometer, startTime - elapsedRealtimeOffset, null, true)
            
        } else {
            remoteViews.setTextViewText(R.id.notif_title, "Pausado")
            remoteViews.setImageViewResource(R.id.btn_toggle, android.R.drawable.ic_media_play)
            
            // Configura Resume
            val resumeIntent = Intent(this, TimerService::class.java).apply { action = ACTION_RESUME }
            val pResume = PendingIntent.getService(this, 3, resumeIntent, PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pResume)

            // Configura Cronômetro Parado (Mostra tempo fixo)
            // Truque: Setar base para (Agora - TempoPausado) e parar contagem mostra o tempo corrido
            val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
            val base = System.currentTimeMillis() - pausedTime - elapsedRealtimeOffset
            remoteViews.setChronometer(R.id.notif_chronometer, base, null, false)
        }

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setStyle(NotificationCompat.DecoratedCustomViewStyle()) // Estilo nativo para custom views
            .setCustomContentView(remoteViews)
            .setContentIntent(pOpen)
            .setOnlyAlertOnce(true)
            .setOngoing(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "Timer", NotificationManager.IMPORTANCE_LOW)
            channel.setSound(null, null)
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
