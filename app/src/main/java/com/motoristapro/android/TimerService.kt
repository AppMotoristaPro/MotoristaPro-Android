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
        const val CHANNEL_ID = "TimerChannel_Debug" // Alterado para forçar recriação
        const val NOTIFICATION_ID = 999
        
        const val ACTION_START = "ACTION_START"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_RESUME = "ACTION_RESUME"
        const val ACTION_STOP = "ACTION_STOP"
        const val ACTION_SYNC = "ACTION_SYNC"
        
        // Request Codes Distintos
        private const val RC_OPEN = 100
        private const val RC_STOP = 200
        private const val RC_PAUSE = 300
        private const val RC_RESUME = 400
    }

    private var startTime: Long = 0L
    private var pausedTime: Long = 0L
    private var isRunning: Boolean = false

    override fun onCreate() {
        super.onCreate()
        logToFile("onCreate chamado")
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        logToFile("onStartCommand recebido: $action")

        try {
            when (action) {
                ACTION_SYNC -> handleSync(intent)
                ACTION_START -> startTimer(System.currentTimeMillis())
                ACTION_PAUSE -> {
                    logToFile("Processando PAUSE")
                    pauseTimer()
                    sendJsCommand("if(window.forcePause) window.forcePause();")
                }
                ACTION_RESUME -> {
                    logToFile("Processando RESUME")
                    resumeTimer()
                    sendJsCommand("if(window.forceResume) window.forceResume();")
                }
                ACTION_STOP -> {
                    logToFile("Processando STOP")
                    stopTimer()
                    sendJsCommand("if(window.forceStop) window.forceStop();")
                }
                else -> logToFile("Ação desconhecida ou nula")
            }
        } catch (e: Exception) {
            logToFile("CRASH em onStartCommand: \${e.message}")
            e.printStackTrace()
        }

        return START_NOT_STICKY
    }

    private fun handleSync(intent: Intent) {
        try {
            val state = intent.getStringExtra("state") ?: "stopped"
            val incomeStartTime = intent.getLongExtra("start_ts", 0L)
            val incomeElapsed = intent.getLongExtra("elapsed", 0L)
            
            logToFile("Sync recebido. State: $state")

            if (state == "running") {
                val base = if (incomeStartTime > 0) incomeStartTime else System.currentTimeMillis()
                if (!isRunning || kotlin.math.abs(startTime - base) > 2000) {
                    startTimer(base)
                }
            } else if (state == "paused") {
                pausedTime = incomeElapsed
                if (isRunning || pausedTime > 0) {
                   pauseTimer()
                }
            } else {
                if (isRunning) stopTimer()
            }
        } catch (e: Exception) {
            logToFile("Erro em handleSync: \${e.message}")
        }
    }

    private fun startTimer(baseTime: Long) {
        logToFile("Iniciando timer em: $baseTime")
        isRunning = true
        startTime = baseTime
        updateNotification("Em Rota")
    }

    private fun pauseTimer() {
        logToFile("Pausando timer")
        if (isRunning) {
            val now = System.currentTimeMillis()
            pausedTime = now - startTime
        }
        isRunning = false
        updateNotification("Pausado")
    }

    private fun resumeTimer() {
        logToFile("Retomando timer")
        val now = System.currentTimeMillis()
        startTime = now - pausedTime
        isRunning = true
        updateNotification("Em Rota")
    }

    private fun stopTimer() {
        logToFile("Parando timer e removendo notificação")
        isRunning = false
        try {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        } catch (e: Exception) {
            logToFile("Erro ao parar serviço: \${e.message}")
        }
    }

    private fun sendJsCommand(js: String) {
        try {
            val intent = Intent("wwebview.js_command")
            intent.putExtra("js", js)
            sendBroadcast(intent)
            logToFile("Comando JS enviado: $js")
        } catch (e: Exception) {
            logToFile("Erro ao enviar broadcast JS: \${e.message}")
        }
    }

    private fun updateNotification(statusText: String) {
        try {
            logToFile("Construindo notificação: $statusText")
            val notification = buildNotification(statusText)
            
            if (Build.VERSION.SDK_INT >= 34) {
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }
            logToFile("Notificação atualizada com sucesso")
        } catch (e: Exception) {
            logToFile("ERRO CRÍTICO ao mostrar notificação: \${e.message}")
            e.printStackTrace()
        }
    }

    private fun buildNotification(statusText: String): Notification {
        // Layout Customizado
        val remoteViews = RemoteViews(packageName, R.layout.notification_timer)
        
        // 1. Intent para abrir o App (Clique na notificação)
        val openIntent = Intent(this, MainActivity::class.java)
        openIntent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        val pOpen = PendingIntent.getActivity(this, RC_OPEN, openIntent, PendingIntent.FLAG_IMMUTABLE)
        
        // 2. Configura Texto
        remoteViews.setTextViewText(R.id.notif_title, statusText)

        // 3. Configura Botões (Com tratamento de erro)
        try {
            // STOP
            val stopIntent = Intent(this, TimerService::class.java).apply { action = ACTION_STOP }
            // IMPORTANTE: Usar getService para iniciar comando no Service
            val pStop = PendingIntent.getService(this, RC_STOP, stopIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_stop, pStop)

            if (isRunning) {
                // Estado: RODANDO -> Mostrar botão PAUSE
                remoteViews.setImageViewResource(R.id.btn_toggle, R.drawable.ic_timer_pause)
                
                val pauseIntent = Intent(this, TimerService::class.java).apply { action = ACTION_PAUSE }
                val pPause = PendingIntent.getService(this, RC_PAUSE, pauseIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
                remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pPause)

                // Configura Cronômetro
                val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
                remoteViews.setChronometer(R.id.notif_chronometer, startTime - elapsedRealtimeOffset, null, true)
                
            } else {
                // Estado: PAUSADO -> Mostrar botão PLAY
                remoteViews.setImageViewResource(R.id.btn_toggle, R.drawable.ic_timer_play)
                
                val resumeIntent = Intent(this, TimerService::class.java).apply { action = ACTION_RESUME }
                val pResume = PendingIntent.getService(this, RC_RESUME, resumeIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
                remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pResume)

                // Congela tempo
                val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
                val base = System.currentTimeMillis() - pausedTime - elapsedRealtimeOffset
                remoteViews.setChronometer(R.id.notif_chronometer, base, null, false)
            }
        } catch (e: Exception) {
            logToFile("Erro ao configurar PendingIntents: \${e.message}")
        }

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setStyle(NotificationCompat.DecoratedCustomViewStyle())
            .setCustomContentView(remoteViews)
            .setContentIntent(pOpen)
            .setOnlyAlertOnce(true)
            .setOngoing(true)
            .setSilent(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "Timer Debug", NotificationManager.IMPORTANCE_LOW)
            channel.setSound(null, null)
            channel.setShowBadge(false)
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    private fun logToFile(msg: String) {
        Logger.log("TIMER_SERVICE", msg)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
