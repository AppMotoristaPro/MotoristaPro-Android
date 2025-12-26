import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo Corrigido: {path}")

def main():
    print("🚑 Corrigindo erros de chaves {} no MainActivity.kt...")
    
    path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"
    
    # Código verificado linha a linha
    code = """package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.media.projection.MediaProjectionManager
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.motoristapro.android.data.DailyRepository
import java.text.NumberFormat
import java.util.Locale

class MainActivity : AppCompatActivity() {

    private var tvTotalGanho: TextView? = null
    private var tvTotalCorridas: TextView? = null
    private var tvTotalKm: TextView? = null
    private var tvEmptyHistory: TextView? = null
    
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            setContentView(R.layout.activity_main)

            tvTotalGanho = findViewById(R.id.tvTotalGanho)
            tvTotalCorridas = findViewById(R.id.tvTotalCorridas)
            tvTotalKm = findViewById(R.id.tvTotalKm)
            tvEmptyHistory = findViewById(R.id.tvEmptyHistory)

            // Botão Lançar
            findViewById<View>(R.id.btnLancar)?.setOnClickListener {
                try {
                    startActivity(Intent(this, AddDailyActivity::class.java))
                } catch (e: Exception) {
                    Toast.makeText(this, "Erro ao abrir: " + e.message, Toast.LENGTH_SHORT).show()
                }
            }

            // Botão Robô
            findViewById<View>(R.id.btnRobo)?.setOnClickListener {
                checkPermissionsAndStart()
            }
            
            // Botão Histórico (no card inferior)
            findViewById<View>(R.id.tvEmptyHistory)?.setOnClickListener {
                try {
                    startActivity(Intent(this, HistoryActivity::class.java))
                } catch (e: Exception) {
                    // Ignora se falhar
                }
            }
            
            // Carrega dados se UI estiver pronta
            if (tvTotalGanho != null) {
                refreshDashboard()
            }

        } catch (e: Exception) {
            Toast.makeText(this, "Erro Fatal UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    override fun onResume() {
        super.onResume()
        if (tvTotalGanho != null) {
            refreshDashboard()
        }
    }

    private fun refreshDashboard() {
        try {
            val repo = DailyRepository(this)
            val summary = repo.getMonthSummary()

            val ptBr = Locale("pt", "BR")
            
            tvTotalGanho?.text = NumberFormat.getCurrencyInstance(ptBr).format(summary.totalEarnings)
            tvTotalKm?.text = String.format(Locale.US, "%.0f km", summary.totalKm)
            tvTotalCorridas?.text = summary.totalRuns.toString()
            
            if (summary.lastEntry != null) {
                val valStr = NumberFormat.getCurrencyInstance(ptBr).format(summary.lastEntry.totalAmount)
                tvEmptyHistory?.text = "Último: $valStr em ${summary.lastEntry.dateString}"
            } else {
                tvEmptyHistory?.text = "Nenhum lançamento recente."
            }

        } catch (e: Exception) {
            tvEmptyHistory?.text = "Dados vazios."
        }
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
        
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
                moveTaskToBack(true)
            } else {
                Toast.makeText(this, "Permissão negada", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
"""
    write_file(path, code)
    
    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("🚀 Sintaxe corrigida! Compile agora.")

if __name__ == "__main__":
    main()


