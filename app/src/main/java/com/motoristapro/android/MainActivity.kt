package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.media.projection.MediaProjectionManager
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import com.motoristapro.android.data.DailyRepository
import java.text.NumberFormat
import java.util.Locale

class MainActivity : AppCompatActivity() {

    private lateinit var tvTotalGanho: TextView
    private lateinit var tvTotalCorridas: TextView
    private lateinit var tvTotalKm: TextView
    private lateinit var tvEmptyHistory: TextView
    
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

            findViewById<CardView>(R.id.btnLancar)?.setOnClickListener {
                startActivity(Intent(this, AddDailyActivity::class.java))
            }

            findViewById<CardView>(R.id.btnRobo)?.setOnClickListener {
                checkPermissionsAndStart()
            }

        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    override fun onResume() {
        super.onResume()
        refreshDashboard()
    }

    private fun refreshDashboard() {
        try {
            val repo = DailyRepository(this)
            val summary = repo.getMonthSummary()

            val ptBr = Locale("pt", "BR")
            tvTotalGanho.text = NumberFormat.getCurrencyInstance(ptBr).format(summary.totalEarnings)
            tvTotalKm.text = String.format("%.0f km", summary.totalKm)
            tvTotalCorridas.text = summary.totalRuns.toString()
            
            if (summary.lastEntry != null) {
                tvEmptyHistory.text = "Último: R$ ${summary.lastEntry.totalAmount} em ${summary.lastEntry.dateString}"
            } else {
                tvEmptyHistory.text = "Nenhum lançamento."
            }

        } catch (e: Exception) {
            tvEmptyHistory.text = "Erro ao carregar dados."
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
                moveTaskToBack(true) // Minimiza o app
            }
        }
    }
}
