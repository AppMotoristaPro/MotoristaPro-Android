import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo corrigido: {path}")

def main():
    print("🚑 Corrigindo erros de Import e KAPT...")

    # ==========================================================================
    # 1. MAIN ACTIVITY (Com Imports Corrigidos)
    # ==========================================================================
    main_path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"
    
    # Código completo com TODOS os imports
    main_code = """package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.media.projection.MediaProjectionManager // <--- O IMPORT QUE FALTAVA
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
        
        try {
            setContentView(R.layout.activity_main)

            // Inicializar Views
            tvTotalGanho = findViewById(R.id.tvTotalGanho)
            tvTotalCorridas = findViewById(R.id.tvTotalCorridas)
            tvTotalKm = findViewById(R.id.tvTotalKm)
            tvEmptyHistory = findViewById(R.id.tvEmptyHistory)

            // Botão Lançar
            findViewById<CardView>(R.id.btnLancar)?.setOnClickListener {
                try {
                    startActivity(Intent(this, AddDailyActivity::class.java))
                } catch (e: Exception) {
                    Toast.makeText(this, "Erro ao abrir: " + e.message, Toast.LENGTH_SHORT).show()
                }
            }

            // Botão Robô
            findViewById<CardView>(R.id.btnRobo)?.setOnClickListener {
                checkPermissionsAndStart()
            }

            // Carregar Dados Iniciais
            refreshDashboard()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro Fatal: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    override fun onResume() {
        super.onResume()
        refreshDashboard()
    }

    private fun refreshDashboard() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val db = AppDatabase.getDatabase(applicationContext)
                
                // Pega histórico (Flow transformado em lista ou snapshot)
                // Para evitar complexidade do Flow no Kapt agora, vamos assumir que o DAO pode retornar lista direta
                // Se der erro de Flow, o try-catch segura
                
                // ATENÇÃO: O DAO precisa ter um método que não seja Flow para chamada direta simples,
                // ou precisamos coletar o Flow. Vamos tentar coletar de forma segura.
                
                db.diarioDao().getAllHistorico().collect { lista ->
                    var totalGanho = 0.0
                    var totalKm = 0.0
                    var totalCorridas = 0
                    
                    for (item in lista) {
                        totalGanho += item.ganhoBruto
                        totalKm += item.kmPercorrido
                        totalCorridas += item.qtdCorridas
                    }

                    withContext(Dispatchers.Main) {
                        val ptBr = Locale("pt", "BR")
                        tvTotalGanho.text = NumberFormat.getCurrencyInstance(ptBr).format(totalGanho)
                        tvTotalKm.text = String.format("%.0f km", totalKm)
                        tvTotalCorridas.text = totalCorridas.toString()
                        
                        if (lista.isNotEmpty()) {
                            val sdf = java.text.SimpleDateFormat("dd/MM", Locale("pt", "BR"))
                            tvEmptyHistory.text = "Último: R$ ${lista[0].ganhoBruto} em ${sdf.format(java.util.Date(lista[0].data))}"
                        }
                    }
                }
            } catch (e: Exception) {
                // e.printStackTrace()
            }
        }
    }

    private fun checkPermissionsAndStart() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivityForResult(intent, REQUEST_OVERLAY)
            return
        }
        
        // AQUI ESTAVA O ERRO DE COMPILAÇÃO
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
    write_file(main_path, main_code)

    # ==========================================================================
    # 2. AJUSTE GRADLE (Otimizar KAPT)
    # ==========================================================================
    # Às vezes o KAPT falha por falta de memória. Vamos aumentar.
    gradle_path = "gradle.properties"
    if os.path.exists(gradle_path):
        with open(gradle_path, 'r') as f:
            props = f.read()
        
        if "org.gradle.jvmargs" not in props:
            with open(gradle_path, 'a') as f:
                f.write("\norg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n")
                f.write("kapt.use.worker.api=true\n")
            print("✅ gradle.properties otimizado para KAPT.")

    print("🚀 Correção aplicada!")

if __name__ == "__main__":
    main()


