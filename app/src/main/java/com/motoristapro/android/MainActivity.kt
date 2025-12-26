package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.media.projection.MediaProjectionManager
import android.provider.Settings
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import androidx.lifecycle.lifecycleScope
import com.motoristapro.android.data.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
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
        setContentView(R.layout.activity_main)

        // Inicializar Views
        tvTotalGanho = findViewById(R.id.tvTotalGanho)
        tvTotalCorridas = findViewById(R.id.tvTotalCorridas)
        tvTotalKm = findViewById(R.id.tvTotalKm)
        tvEmptyHistory = findViewById(R.id.tvEmptyHistory)

        // Botão Lançar (Abre a tela nativa do Módulo 2)
        findViewById<CardView>(R.id.btnLancar).setOnClickListener {
            startActivity(Intent(this, AddDailyActivity::class.java))
        }

        // Botão Robô
        findViewById<CardView>(R.id.btnRobo).setOnClickListener {
            checkPermissionsAndStart()
        }

        // Carregar Dados Iniciais
        refreshDashboard()
    }

    override fun onResume() {
        super.onResume()
        // Recarrega os dados toda vez que voltar para esta tela (ex: após salvar um ganho)
        refreshDashboard()
    }

    private fun refreshDashboard() {
        lifecycleScope.launch(Dispatchers.IO) {
            val db = AppDatabase.getDatabase(applicationContext)
            
            // Consulta: Soma tudo o que já foi lançado
            // Nota: collect() é para Flow, aqui vamos usar uma query direta se possível ou coletar o flow
            // Como definimos getAllHistorico como Flow, vamos apenas pegar o primeiro valor para simplificar o dashboard estático
            
            // Para simplificar a demonstração, vamos apenas somar tudo na memória ou criar uma query de soma no DAO
            // Vamos usar o Flow que já existe e pegar o valor atual
            
            try {
                // Pegamos o histórico completo
                db.diarioDao().getAllHistorico().collect { lista ->
                    var totalGanho = 0.0
                    var totalKm = 0.0
                    var totalCorridas = 0
                    
                    for (item in lista) {
                        totalGanho += item.ganhoBruto
                        totalKm += item.kmPercorrido
                        totalCorridas += (if (item.qtdCorridas > 0) item.qtdCorridas else 1) // Estimativa simples se qtd for 0
                    }

                    withContext(Dispatchers.Main) {
                        val ptBr = Locale("pt", "BR")
                        tvTotalGanho.text = NumberFormat.getCurrencyInstance(ptBr).format(totalGanho)
                        tvTotalKm.text = String.format("%.0f km", totalKm)
                        tvTotalCorridas.text = totalCorridas.toString()
                        
                        if (lista.isNotEmpty()) {
                            tvEmptyHistory.text = "Último lançamento: R$ ${lista[0].ganhoBruto} em ${java.text.SimpleDateFormat("dd/MM").format(java.util.Date(lista[0].data))}"
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
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
                // Minimizar
                moveTaskToBack(true)
            } else {
                Toast.makeText(this, "Permissão negada", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
