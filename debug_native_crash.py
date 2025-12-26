import os

def main():
    print("🚑 Aplicando Modo de Segurança para descobrir o erro...")

    # 1. Garantir Dependência do CardView no Gradle
    gradle_path = "app/build.gradle.kts"
    if os.path.exists(gradle_path):
        with open(gradle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "androidx.cardview:cardview" not in content:
            # Adiciona a dependência
            dep = '    implementation("androidx.cardview:cardview:1.0.0")'
            if "dependencies {" in content:
                content = content.replace("dependencies {", "dependencies {\n" + dep)
                with open(gradle_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Dependência CardView adicionada.")

    # 2. Modificar MainActivity para mostrar o erro na tela
    main_path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"
    
    # Código Blindado
    safe_code = """package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
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
            // Tenta carregar o layout bonito
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
                    showError("Erro ao abrir lançamentos: " + e.message)
                }
            }

            // Botão Robô
            findViewById<CardView>(R.id.btnRobo)?.setOnClickListener {
                checkPermissionsAndStart()
            }

            // Carregar Dados Iniciais
            refreshDashboard()
            
        } catch (e: Exception) {
            // SE DER ERRO, MOSTRA NA TELA EM VEZ DE FECHAR
            showErrorFatal(e)
        }
    }

    private fun showErrorFatal(e: Exception) {
        val scroll = ScrollView(this)
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.setPadding(40, 40, 40, 40)
        
        val title = TextView(this)
        title.text = "ERRO FATAL NO APP"
        title.textSize = 20f
        title.setTextColor(android.graphics.Color.RED)
        
        val msg = TextView(this)
        msg.text = e.toString() + "\\n\\n" + e.stackTraceToString()
        msg.textSize = 14f
        
        layout.addView(title)
        layout.addView(msg)
        scroll.addView(layout)
        setContentView(scroll)
    }

    private fun showError(msg: String) {
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show()
    }

    override fun onResume() {
        super.onResume()
        try { refreshDashboard() } catch(e: Exception) {}
    }

    private fun refreshDashboard() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val db = AppDatabase.getDatabase(applicationContext)
                
                // Coleta Flow
                db.diarioDao().getAllHistorico().collect { lista ->
                    var totalGanho = 0.0
                    var totalKm = 0.0
                    var totalCorridas = 0
                    
                    for (item in lista) {
                        totalGanho += item.ganhoBruto
                        totalKm += item.kmPercorrido
                        totalCorridas += (if (item.qtdCorridas > 0) item.qtdCorridas else 1)
                    }

                    withContext(Dispatchers.Main) {
                        try {
                            val ptBr = Locale("pt", "BR")
                            tvTotalGanho.text = NumberFormat.getCurrencyInstance(ptBr).format(totalGanho)
                            tvTotalKm.text = String.format("%.0f km", totalKm)
                            tvTotalCorridas.text = totalCorridas.toString()
                            
                            if (lista.isNotEmpty()) {
                                val sdf = java.text.SimpleDateFormat("dd/MM", Locale("pt", "BR"))
                                tvEmptyHistory.text = "Último: R$ ${lista[0].ganhoBruto} em ${sdf.format(java.util.Date(lista[0].data))}"
                            }
                        } catch(e: Exception) {}
                    }
                }
            } catch (e: Exception) {
                // Erro silencioso no dashboard para não travar
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
                moveTaskToBack(true)
            } else {
                Toast.makeText(this, "Permissão negada", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
"""
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(safe_code)
    
    print("✅ MainActivity blindada contra crashes.")

    # 3. Incrementar Versão
    os.system("python3 auto_version.py")
    print("🚀 Pronto! Rode './gradlew assembleDebug'")

if __name__ == "__main__":
    main()


