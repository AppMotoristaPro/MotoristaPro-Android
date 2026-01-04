import os
import shutil
import subprocess
from datetime import datetime

# --- CONFIGURAÇÕES ---
COMMIT_MSG = "Fix: Crash TimerService Android 14 (SDK 34) Permissions"
BACKUP_DIR = "backup_automatico"

# CONTEÚDO: AndroidManifest.xml (Adicionada permissão SPECIAL_USE e Tipo no Service)
MANIFEST_CONTENT = r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.MotoristaProAndroid"
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".TimerService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="specialUse" />

        <service
            android:name=".OverlayService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="specialUse" />
            
        <service
            android:name=".MyFirebaseMessagingService"
            android:exported="false">
            <intent-filter>
                <action android:name="com.google.firebase.MESSAGING_EVENT" />
            </intent-filter>
        </service>

    </application>

</manifest>
"""

# CONTEÚDO: TimerService.kt (Compatibilidade SDK 34)
TIMER_SERVICE_CONTENT = r"""package com.motoristapro.android

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
        const val ACTION_START = "ACTION_START"
        const val ACTION_STOP = "ACTION_STOP"
        const val ACTION_PAUSE = "ACTION_PAUSE"
        const val ACTION_SYNC = "ACTION_SYNC"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        
        // Dados vindos do WebApp
        val startTime = intent?.getLongExtra("start_time", 0L) ?: 0L
        val elapsed = intent?.getLongExtra("elapsed", 0L) ?: 0L
        val state = intent?.getStringExtra("state") ?: "stopped"

        if (action == ACTION_SYNC || action == ACTION_START) {
            val notification = createNotification(state, startTime, elapsed)
            
            // CORREÇÃO CRÍTICA ANDROID 14 (SDK 34)
            if (Build.VERSION.SDK_INT >= 34) { // Android 14+
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) { // Android 10+
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }
        } else if (action == ACTION_STOP) {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }

        return START_NOT_STICKY
    }

    private fun createNotification(state: String, startTs: Long, pausedElapsed: Long): Notification {
        val title = if (state == "running") "Em Rota" else "Pausado"
        
        // Cálculo do tempo para exibir
        val totalMs = if (state == "running") {
            System.currentTimeMillis() - startTs
        } else {
            pausedElapsed
        }
        
        val seconds = (totalMs / 1000) % 60
        val minutes = (totalMs / (1000 * 60)) % 60
        val hours = (totalMs / (1000 * 60 * 60))
        val timeString = String.format(Locale.getDefault(), "%02d:%02d:%02d", hours, minutes, seconds)

        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE)

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(timeString)
            .setSmallIcon(R.mipmap.ic_launcher) // Certifique-se que existe, senão use android.R.drawable.ic_media_play
            .setContentIntent(pendingIntent)
            .setOnlyAlertOnce(true)
            .setOngoing(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID,
                "Cronômetro de Rota",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(serviceChannel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
"""

FILES_TO_MODIFY = {
    "app/src/main/AndroidManifest.xml": MANIFEST_CONTENT,
    "app/src/main/java/com/motoristapro/android/TimerService.kt": TIMER_SERVICE_CONTENT
}

def run_cmd(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao executar: {command}")
        exit(1)

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, timestamp)
    
    print(f"🚀 Iniciando Correção Android 14 (Timer Crash)...")

    # 1. BACKUP
    print(f"📦 Criando backup em: {backup_path}")
    for file_path in FILES_TO_MODIFY.keys():
        if os.path.exists(file_path):
            dest = os.path.join(backup_path, file_path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(file_path, dest)

    # 2. APLICAR MUDANÇAS
    print("📝 Reescrevendo arquivos...")
    for file_path, content in FILES_TO_MODIFY.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ Atualizado: {file_path}")

    # 3. GIT PUSH
    print("☁️ Subindo para o GitHub...")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{COMMIT_MSG}"')
    run_cmd("git push")

    # 4. AUTO-DESTRUIÇÃO
    print("💥 Limpando script...")
    os.remove(__file__)
    print("✅ Concluído! Recompile o app no Android Studio.")

if __name__ == "__main__":
    main()

