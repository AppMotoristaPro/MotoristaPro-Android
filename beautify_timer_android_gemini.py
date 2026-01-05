import os
import shutil
import subprocess
import sys
from datetime import datetime

# --- CONFIGURAÇÃO ---
PROJECT_NAME = "MotoristaPro-Android"
HOME_DIR = os.path.expanduser("~")
PROJECT_PATH = os.path.join(HOME_DIR, PROJECT_NAME)
BACKUP_DIR = os.path.join(PROJECT_PATH, "backup_automatico")

# Arquivos
FILES = {
    "play": "app/src/main/res/drawable/ic_timer_play.xml",
    "pause": "app/src/main/res/drawable/ic_timer_pause.xml",
    "stop": "app/src/main/res/drawable/ic_timer_stop.xml",
    "layout": "app/src/main/res/layout/notification_timer.xml",
    "service": "app/src/main/java/com/motoristapro/android/TimerService.kt"
}

# --- CONTEÚDO DOS ÍCONES (Vector Drawables Bonitos) ---
IC_PLAY = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#2563EB" android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM10,16.5v-9l6,4.5 -6,4.5z"/>
</vector>"""

IC_PAUSE = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#2563EB" android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM11,16H9V8h2v8zm4,0h-2V8h2v8z"/>
</vector>"""

IC_STOP = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#EF4444" android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM16,16H8V8h8v8z"/>
</vector>"""

# --- CONTEÚDO DO LAYOUT XML (Refinado) ---
LAYOUT_XML = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:gravity="center_vertical"
    android:paddingStart="16dp"
    android:paddingEnd="16dp"
    android:paddingTop="8dp"
    android:paddingBottom="8dp">

    <!-- Cronômetro e Título à Esquerda -->
    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">

        <TextView
            android:id="@+id/notif_title"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Cronômetro"
            android:textSize="14sp"
            android:textStyle="bold"
            android:textColor="@android:color/black" 
            android:maxLines="1"
            android:ellipsize="end"/>

        <Chronometer
            android:id="@+id/notif_chronometer"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="20sp"
            android:fontFamily="sans-serif-medium"
            android:textColor="#333333" />
    </LinearLayout>

    <!-- Botões à Direita (Ícones Grandes) -->
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:gravity="center_vertical"
        android:orientation="horizontal">

        <ImageButton
            android:id="@+id/btn_toggle"
            android:layout_width="48dp"
            android:layout_height="48dp"
            android:background="?android:attr/selectableItemBackgroundBorderless"
            android:src="@drawable/ic_timer_pause"
            android:contentDescription="Pause/Resume"
            android:scaleType="fitCenter" />

        <Space
            android:layout_width="16dp"
            android:layout_height="wrap_content" />

        <ImageButton
            android:id="@+id/btn_stop"
            android:layout_width="48dp"
            android:layout_height="48dp"
            android:background="?android:attr/selectableItemBackgroundBorderless"
            android:src="@drawable/ic_timer_stop"
            android:contentDescription="Stop"
            android:scaleType="fitCenter" />
    </LinearLayout>

</LinearLayout>
"""

# --- SERVICE (Usando forcePause/Resume e Ícones Novos) ---
SERVICE_KT = """package com.motoristapro.android

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
        return START_NOT_STICKY
    }

    private fun handleSync(intent: Intent) {
        val state = intent.getStringExtra("state") ?: "stopped"
        val incomeStartTime = intent.getLongExtra("start_ts", 0L)
        val incomeElapsed = intent.getLongExtra("elapsed", 0L)

        if (state == "running") {
            val base = if (incomeStartTime > 0) incomeStartTime else System.currentTimeMillis()
            if (!isRunning || kotlin.math.abs(startTime - base) > 1000) startTimer(base)
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
        val remoteViews = RemoteViews(packageName, R.layout.notification_timer)
        
        val openIntent = Intent(this, MainActivity::class.java)
        openIntent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
        val pOpen = PendingIntent.getActivity(this, 0, openIntent, PendingIntent.FLAG_IMMUTABLE)
        
        val stopIntent = Intent(this, TimerService::class.java).apply { action = ACTION_STOP }
        val pStop = PendingIntent.getService(this, 1, stopIntent, PendingIntent.FLAG_IMMUTABLE)
        remoteViews.setOnClickPendingIntent(R.id.btn_stop, pStop)

        if (isRunning) {
            remoteViews.setTextViewText(R.id.notif_title, "Em Rota")
            remoteViews.setImageViewResource(R.id.btn_toggle, R.drawable.ic_timer_pause)
            
            val pauseIntent = Intent(this, TimerService::class.java).apply { action = ACTION_PAUSE }
            val pPause = PendingIntent.getService(this, 2, pauseIntent, PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pPause)

            val elapsedRealtimeOffset = System.currentTimeMillis() - SystemClock.elapsedRealtime()
            remoteViews.setChronometer(R.id.notif_chronometer, startTime - elapsedRealtimeOffset, null, true)
        } else {
            remoteViews.setTextViewText(R.id.notif_title, "Pausado")
            remoteViews.setImageViewResource(R.id.btn_toggle, R.drawable.ic_timer_play)
            
            val resumeIntent = Intent(this, TimerService::class.java).apply { action = ACTION_RESUME }
            val pResume = PendingIntent.getService(this, 3, resumeIntent, PendingIntent.FLAG_IMMUTABLE)
            remoteViews.setOnClickPendingIntent(R.id.btn_toggle, pResume)

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
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
"""

def write_file(rel_path, content):
    path = os.path.join(PROJECT_PATH, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📝 Criado/Atualizado: {rel_path}")

def main():
    print(f"🚀 Iniciando Beautify Android em: {PROJECT_NAME}")
    if not os.path.exists(PROJECT_PATH):
        print("❌ Projeto não encontrado."); return

    # 1. BACKUP
    if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
    
    # 2. ESCREVER ARQUIVOS
    write_file(FILES["play"], IC_PLAY)
    write_file(FILES["pause"], IC_PAUSE)
    write_file(FILES["stop"], IC_STOP)
    write_file(FILES["layout"], LAYOUT_XML)
    write_file(FILES["service"], SERVICE_KT)

    # 3. GIT
    os.system(f'cd {PROJECT_PATH} && git add . && git commit -m "Feat: Beautiful Native Timer Icons & Logic" && git push')

    # 4. LIMPEZA
    try: os.remove(sys.argv[0]) 
    except: pass

if __name__ == "__main__":
    main()


