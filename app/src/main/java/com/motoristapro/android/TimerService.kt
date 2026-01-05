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
import android.util.Log

class TimerService : Service() {

    companion object {
        const val CHANNEL_ID = "TimerChannel"
        const val NOTIFICATION_ID = 12345 // ID fixo e único
        
        const val ACTION_START = "ACTION_START"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_RESUME = "ACTION_RESUME"
        const val ACTION_STOP = "ACTION_STOP"
        const val ACTION_SYNC = "ACTION_SYNC"
        
        // Request Codes para evitar conflito de intents
        private const val RC_OPEN = 100
        private const val RC_STOP = 101
        private const val RC_PAUSE = 102
        private const val RC_RESUME = 103
    }

    private var startTime: Long = 0L
    private var pausedTime: Long = 0L
    private var isRunning: Boolean = false

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            val action = intent?.action
            Log.d("TimerService", "Action received: $action")

            when (action) {
                ACTION_SYNC -> handleSync(intent)
                ACTION_START -> startTimer(System.currentTimeMillis())
                ACTION_PAUSE -> {
                    pauseTimer()
                    sendJsCommand("if(window.forcePause) window.forcePause();")
                }
                ACTION_RESUME -> {
                    resumeTimer()
                    sendJsCommand("if(window.forceResume) window.forceResume();")
                }
                ACTION_STOP -> {
                    stopTimer()
                    sendJsCommand("if(window.forceStop) window.forceStop();")
                }
            }
        } catch (e: Exception) {
            Log.e("TimerService", "Error in onStartCommand", e)
        }
        return START_NOT_STICKY
    }

    private fun handleSync(intent: Intent) {
        val state = intent.getStringExtra("state") ?: "stopped"
        val incomeStartTime = intent.getLongExtra("start_ts", 0L)
        val incomeElapsed = intent.getLongExtra("elapsed", 0L)

        if (state == "running") {
            val base = if (incomeStartTime > 0) incomeStartTime else System.currentTimeMillis()
            // Sincroniza se não estiver rodando ou se a diferença for grande (>2s)
            if (!isRunning || kotlin.math.abs(startTime - base) > 2000) {
                startTimer(base)
            }
        } else if (state == "paused") {
            pausedTime = incomeElapsed
            if (isRunning || pausedTime > 0) {
               pauseTimer()
            }
        } else {
            // Se o site diz stopped, paramos.
            if (isRunning) stopTimer()
        }
    }

    private fun startTimer(baseTime: Long) {
        isRunning = true
        startTime = baseTime
        updateNotification()
    }

    private fun pauseTimer() {
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
        try {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        } catch (e: Exception) {
            Log.e("TimerService", "Error stopping service", e)
        }
    }

    private fun sendJsCommand(js: String) {
        val intent = Intent("wwebview.js_command")
        intent.putExtra("js", js)
        sendBroadcast(intent)
    }

    private fun updateNotification() {
        try {
            val notification = buildNotification()
            if (Build.VERSION.SDK_INT >= 34) {
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }
        } catch (e: Exception) {
            Log.e("TimerService", "Error building/showing notification", e)
        }
    }

    private fun buildNotification(): Notification {
        // Layout Customizado
        val remoteViews = RemoteViews(packageName, R.layout.notification_timer)
        
        // Intent para abrir o App
        val openIntent = Intent(this, MainActivity::class.java)
        openIntent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        val pOpen = PendingIntent.getActivity(this, RC_OPEN, openIntent, PendingIntent.FLAG_IMMUTABLE)
        
        // Intent para Parar (Stop)
        val stopIntent = Intent(this, TimerService::class.java).apply { action = ACTION_STOP }
        val pStop = PendingIntent.getService(this, RC_STOP, stopIntent, PendingIntent.FLAG_IMMUTABLE)
        remoteViews.setOnClickPendingIntent(R.id.btn_stop, pStop)

        if (isRunning) {
            remoteViews.setTextViewText(R.id.notif_title, "Em Rota")
            remoteViews.setImageViewResource(R.id.btn_toggle, R.drawable.ic_timer_pause)
            
            // Configura botão para PAUSAR
            val pauseIntent = Intent(this, TimerService::class.java).apply { action = ACTION_PAUSE }
            val pPause = PendingIntent.getService(this, RC_PAUSE, pauseIntent, PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pPause)

            // Configura Cronômetro Rodando (Realtime base)
            val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
            remoteViews.setChronometer(R.id.notif_chronometer, startTime - elapsedRealtimeOffset, null, true)
            
        } else {
            remoteViews.setTextViewText(R.id.notif_title, "Pausado")
            remoteViews.setImageViewResource(R.id.btn_toggle, R.drawable.ic_timer_play)
            
            // Configura botão para RETOMAR
            val resumeIntent = Intent(this, TimerService::class.java).apply { action = ACTION_RESUME }
            val pResume = PendingIntent.getService(this, RC_RESUME, resumeIntent, PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pResume)

            // Configura Cronômetro Parado (Estático)
            val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
            val base = System.currentTimeMillis() - pausedTime - elapsedRealtimeOffset
            remoteViews.setChronometer(R.id.notif_chronometer, base, null, false)
        }

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setStyle(NotificationCompat.DecoratedCustomViewStyle())
            .setCustomContentView(remoteViews)
            .setContentIntent(pOpen)
            .setOnlyAlertOnce(true)
            .setOngoing(true)
            .setSilent(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "Timer", NotificationManager.IMPORTANCE_LOW)
            channel.setSound(null, null)
            channel.setShowBadge(false)
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
