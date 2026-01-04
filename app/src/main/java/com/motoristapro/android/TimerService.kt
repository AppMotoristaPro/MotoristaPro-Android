package com.motoristapro.android

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat

class TimerService : Service() {

    private val CHANNEL_ID = "timer_channel"
    private val NOTIF_ID = 777
    private val handler = Handler(Looper.getMainLooper())
    
    private var startTime = 0L
    private var accumulatedTime = 0L
    private var isRunning = false
    
    private lateinit var notificationManager: NotificationManager

    companion object {
        const val ACTION_START = "ACTION_START"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_RESUME = "ACTION_RESUME"
        const val ACTION_STOP = "ACTION_STOP"
        const val ACTION_SYNC = "ACTION_SYNC" 
    }

    private val updateRunnable = object : Runnable {
        override fun run() {
            if (isRunning) {
                updateNotification()
                handler.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        createChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        
        when (action) {
            ACTION_SYNC -> {
                val state = intent.getStringExtra("state") ?: "stopped"
                val startTs = intent.getLongExtra("start_ts", 0L)
                val elapsed = intent.getLongExtra("elapsed", 0L)
                
                if (state == "running") {
                    startTime = startTs
                    accumulatedTime = 0 
                    if (!isRunning) {
                        isRunning = true
                        startForeground(NOTIF_ID, buildNotification())
                        handler.post(updateRunnable)
                    }
                } else if (state == "paused") {
                    isRunning = false
                    accumulatedTime = elapsed
                    startTime = 0
                    updateNotification()
                } else {
                    stopSelf()
                }
            }
            ACTION_PAUSE -> {
                isRunning = false
                accumulatedTime = System.currentTimeMillis() - startTime
                updateNotification()
                sendToJs("window.toggleTimer();") 
            }
            ACTION_RESUME -> {
                startTime = System.currentTimeMillis() - accumulatedTime
                isRunning = true
                handler.post(updateRunnable)
                sendToJs("window.toggleTimer();")
            }
            ACTION_STOP -> {
                val totalMs = if (isRunning) System.currentTimeMillis() - startTime else accumulatedTime
                val totalSec = totalMs / 1000
                val h = totalSec / 3600
                val m = (totalSec % 3600) / 60
                
                stopSelf()
                
                val activityIntent = Intent(this, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                    action = "OPEN_ADD_SCREEN"
                    putExtra("h_val", h.toInt())
                    putExtra("m_val", m.toInt())
                }
                startActivity(activityIntent)
            }
        }
        return START_NOT_STICKY
    }

    private fun sendToJs(js: String) {
        val intent = Intent("wwebview.js_command")
        intent.putExtra("js", js)
        sendBroadcast(intent)
    }

    private fun updateNotification() {
        notificationManager.notify(NOTIF_ID, buildNotification())
    }

    private fun buildNotification(): android.app.Notification {
        val ms = if (isRunning) System.currentTimeMillis() - startTime else accumulatedTime
        val s = ms / 1000
        val h = s / 3600
        val m = (s % 3600) / 60
        val sec = s % 60
        val timeStr = String.format("%02d:%02d:%02d", h, m, sec)

        val openIntent = Intent(this, MainActivity::class.java)
        val pendingOpen = PendingIntent.getActivity(this, 0, openIntent, PendingIntent.FLAG_IMMUTABLE)

        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Cronômetro Ativo")
            .setContentText(timeStr)
            .setSmallIcon(android.R.drawable.ic_menu_recent_history)
            .setOnlyAlertOnce(true)
            .setContentIntent(pendingOpen)
            .setOngoing(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)

        if (isRunning) {
            val pauseIntent = Intent(this, TimerService::class.java).apply { action = ACTION_PAUSE }
            val pPause = PendingIntent.getService(this, 1, pauseIntent, PendingIntent.FLAG_IMMUTABLE)
            builder.addAction(android.R.drawable.ic_media_pause, "Pausar", pPause)
        } else {
            val resumeIntent = Intent(this, TimerService::class.java).apply { action = ACTION_RESUME }
            val pResume = PendingIntent.getService(this, 2, resumeIntent, PendingIntent.FLAG_IMMUTABLE)
            builder.addAction(android.R.drawable.ic_media_play, "Retomar", pResume)
        }

        val stopIntent = Intent(this, TimerService::class.java).apply { action = ACTION_STOP }
        val pStop = PendingIntent.getService(this, 3, stopIntent, PendingIntent.FLAG_IMMUTABLE)
        builder.addAction(android.R.drawable.ic_delete, "Parar", pStop)

        return builder.build()
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "Cronômetro", NotificationManager.IMPORTANCE_LOW)
            notificationManager.createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
    override fun onDestroy() { handler.removeCallbacks(updateRunnable); super.onDestroy() }
}