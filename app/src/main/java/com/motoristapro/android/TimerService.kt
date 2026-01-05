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
import androidx.core.app.NotificationCompat
import java.util.Locale

class TimerService : Service() {

    companion object {
        const val CHANNEL_ID = "TimerChannel"
        const val NOTIFICATION_ID = 1
        
        // Ações internas para os botões da notificação
        const val ACTION_START = "ACTION_START"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_RESUME = "ACTION_RESUME"
        const val ACTION_STOP = "ACTION_STOP"
        const val ACTION_SYNC = "ACTION_SYNC" // Sincronização vinda do WebApp
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
            ACTION_START -> {
                // Início limpo
                startTimer(System.currentTimeMillis())
            }
            ACTION_PAUSE -> pauseTimer()
            ACTION_RESUME -> resumeTimer()
            ACTION_STOP -> stopTimer()
        }

        return START_NOT_STICKY
    }

    private fun handleSync(intent: Intent) {
        val state = intent.getStringExtra("state") ?: "stopped"
        // Tempos vindos do JS (WebView)
        val incomeStartTime = intent.getLongExtra("start_ts", 0L)
        val incomeElapsed = intent.getLongExtra("elapsed", 0L)

        if (state == "running") {
            // Se o web diz que está rodando, usamos o start_ts dele como base
            val base = if (incomeStartTime > 0) incomeStartTime else System.currentTimeMillis()
            // Se já estiver rodando, só atualizamos se a base for muito diferente (evita flickers)
            if (!isRunning || kotlin.math.abs(startTime - base) > 1000) {
                startTimer(base)
            }
        } else if (state == "paused") {
            pausedTime = incomeElapsed
            pauseTimer()
        } else {
            stopTimer()
        }
    }

    private fun startTimer(baseTime: Long) {
        isRunning = true
        startTime = baseTime
        updateNotification()
    }

    private fun pauseTimer() {
        if (isRunning) {
            // Calcula quanto tempo correu até agora para congelar o texto
            val now = System.currentTimeMillis()
            pausedTime = now - startTime
        }
        isRunning = false
        updateNotification()
        
        // Opcional: Enviar broadcast de volta para o WebView se precisar manter sincronia bidirecional
        sendBroadcastToWeb("pause")
    }

    private fun resumeTimer() {
        // Ao retomar, ajustamos o startTime para descontar o tempo que ficou pausado
        // Fórmula: NovoBase = Agora - TempoQueJáTinhaCorrido
        val now = System.currentTimeMillis()
        startTime = now - pausedTime
        isRunning = true
        updateNotification()
        
        sendBroadcastToWeb("resume")
    }

    private fun stopTimer() {
        isRunning = false
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
        sendBroadcastToWeb("stop")
    }

    private fun sendBroadcastToWeb(action: String) {
        // Envia um broadcast que a MainActivity pode interceptar para injetar JS na WebView
        val intent = Intent("com.motoristapro.TIMER_ACTION")
        intent.putExtra("action", action)
        sendBroadcast(intent)
    }

    private fun updateNotification() {
        val notification = buildNotification()
        
        // Compatibilidade Android 14 (Foreground Service Type)
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun buildNotification(): Notification {
        // Intent para abrir o App ao clicar na notificação
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentIntent(pendingIntent)
            .setOnlyAlertOnce(true) // Não toca som a cada atualização
            .setOngoing(true) // Impede arrastar para fechar
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)

        // --- LÓGICA DE ESTILO SAMSUNG ---
        if (isRunning) {
            builder.setContentTitle("Em Rota")
            // A mágica: Deixa o sistema contar o tempo na barra
            builder.setUsesChronometer(true)
            builder.setWhen(startTime)
            builder.setShowWhen(true)
            
            // Botão PAUSAR
            val pPause = PendingIntent.getService(
                this, 1, 
                Intent(this, TimerService::class.java).apply { action = ACTION_PAUSE }, 
                PendingIntent.FLAG_IMMUTABLE
            )
            builder.addAction(android.R.drawable.ic_media_pause, "Pausar", pPause)

        } else {
            builder.setContentTitle("Pausado")
            builder.setUsesChronometer(false)
            builder.setShowWhen(false)
            
            // Mostra o tempo estático congelado
            builder.setContentText(formatElapsedTime(pausedTime))

            // Botão RETOMAR
            val pResume = PendingIntent.getService(
                this, 2, 
                Intent(this, TimerService::class.java).apply { action = ACTION_RESUME }, 
                PendingIntent.FLAG_IMMUTABLE
            )
            builder.addAction(android.R.drawable.ic_media_play, "Retomar", pResume)
        }

        // Botão PARAR (Sempre visível)
        val pStop = PendingIntent.getService(
            this, 3, 
            Intent(this, TimerService::class.java).apply { action = ACTION_STOP }, 
            PendingIntent.FLAG_IMMUTABLE
        )
        builder.addAction(android.R.drawable.ic_menu_close_clear_cancel, "Parar", pStop)

        return builder.build()
    }

    private fun formatElapsedTime(ms: Long): String {
        val seconds = (ms / 1000) % 60
        val minutes = (ms / (1000 * 60)) % 60
        val hours = (ms / (1000 * 60 * 60))
        return String.format(Locale.getDefault(), "%02d:%02d:%02d", hours, minutes, seconds)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID,
                "Cronômetro de Rota",
                NotificationManager.IMPORTANCE_LOW // Low para não fazer som/vibração intrusiva
            )
            serviceChannel.description = "Controle de tempo de rota na barra de status"
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(serviceChannel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
