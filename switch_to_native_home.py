import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo Nativo Criado: {path}")

def main():
    print("🚀 Substituindo WebView por Dashboard Nativo...")

    base_res = "app/src/main/res/layout"
    base_java = "app/src/main/java/com/motoristapro/android"

    # ==========================================================================
    # 1. LAYOUT DASHBOARD (activity_main.xml)
    # ==========================================================================
    # Um layout moderno com Cards de resumo e botões de ação
    dashboard_xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true"
    android:background="#F1F5F9">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- CABEÇALHO -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="25dp">
            
            <ImageView
                android:layout_width="50dp"
                android:layout_height="50dp"
                android:src="@mipmap/ic_launcher_round"/>
                
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginStart="15dp">
                
                <TextView
                    android:text="Olá, Motorista"
                    android:textSize="18sp"
                    android:textStyle="bold"
                    android:textColor="#0F172A"/>
                
                <TextView
                    android:text="Visão Geral (Offline)"
                    android:textSize="12sp"
                    android:textColor="#64748B"/>
            </LinearLayout>
        </LinearLayout>

        <!-- CARD DE RESUMO FINANCEIRO -->
        <androidx.cardview.widget.CardView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            app:cardCornerRadius="20dp"
            app:cardElevation="5dp"
            android:layout_marginBottom="25dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:background="#2563EB"
                android:padding="25dp">

                <TextView
                    android:text="FATURAMENTO TOTAL"
                    android:textSize="12sp"
                    android:textColor="#93C5FD"
                    android:textStyle="bold"
                    android:letterSpacing="0.1"/>

                <TextView
                    android:id="@+id/tvTotalGanho"
                    android:text="R$ 0,00"
                    android:textSize="36sp"
                    android:textStyle="bold"
                    android:textColor="#FFFFFF"
                    android:layout_marginTop="5dp"/>
                
                <View
                    android:layout_width="match_parent"
                    android:layout_height="1dp"
                    android:background="#40FFFFFF"
                    android:layout_marginTop="15dp"
                    android:layout_marginBottom="15dp"/>

                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">
                    
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_weight="1"
                        android:layout_height="wrap_content"
                        android:orientation="vertical">
                        <TextView android:text="CORRIDAS" android:textSize="10sp" android:textColor="#93C5FD"/>
                        <TextView android:id="@+id/tvTotalCorridas" android:text="0" android:textSize="16sp" android:textColor="#FFFFFF" android:textStyle="bold"/>
                    </LinearLayout>
                    
                    <LinearLayout
                        android:layout_width="0dp"
                        android:layout_weight="1"
                        android:layout_height="wrap_content"
                        android:orientation="vertical">
                        <TextView android:text="KM TOTAL" android:textSize="10sp" android:textColor="#93C5FD"/>
                        <TextView android:id="@+id/tvTotalKm" android:text="0 km" android:textSize="16sp" android:textColor="#FFFFFF" android:textStyle="bold"/>
                    </LinearLayout>
                </LinearLayout>
            </LinearLayout>
        </androidx.cardview.widget.CardView>

        <!-- AÇÕES RÁPIDAS -->
        <TextView
            android:text="AÇÕES RÁPIDAS"
            android:textSize="12sp"
            android:textStyle="bold"
            android:textColor="#64748B"
            android:layout_marginBottom="10dp"/>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2"
            android:layout_marginBottom="15dp">

            <!-- BOTÃO LANÇAR -->
            <androidx.cardview.widget.CardView
                android:id="@+id/btnLancar"
                android:layout_width="0dp"
                android:layout_height="100dp"
                android:layout_weight="1"
                android:layout_marginEnd="8dp"
                app:cardCornerRadius="15dp"
                app:cardElevation="2dp"
                app:cardBackgroundColor="#FFFFFF">
                
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="match_parent"
                    android:gravity="center"
                    android:orientation="vertical">
                    <ImageView android:src="@android:drawable/ic_input_add" android:layout_width="30dp" android:layout_height="30dp" app:tint="#10B981"/>
                    <TextView android:text="Novo\nLançamento" android:textSize="14sp" android:textStyle="bold" android:textColor="#0F172A" android:textAlignment="center" android:layout_marginTop="5dp"/>
                </LinearLayout>
            </androidx.cardview.widget.CardView>

            <!-- BOTÃO ROBÔ -->
            <androidx.cardview.widget.CardView
                android:id="@+id/btnRobo"
                android:layout_width="0dp"
                android:layout_height="100dp"
                android:layout_weight="1"
                android:layout_marginStart="8dp"
                app:cardCornerRadius="15dp"
                app:cardElevation="2dp"
                app:cardBackgroundColor="#FFFFFF">
                
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="match_parent"
                    android:gravity="center"
                    android:orientation="vertical">
                    <ImageView android:src="@android:drawable/ic_media_play" android:layout_width="30dp" android:layout_height="30dp" app:tint="#F59E0B"/>
                    <TextView android:text="Ativar\nRobô" android:textSize="14sp" android:textStyle="bold" android:textColor="#0F172A" android:textAlignment="center" android:layout_marginTop="5dp"/>
                </LinearLayout>
            </androidx.cardview.widget.CardView>
        </LinearLayout>
        
        <TextView
            android:text="Histórico Recente"
            android:textSize="12sp"
            android:textStyle="bold"
            android:textColor="#64748B"
            android:layout_marginBottom="10dp"
            android:layout_marginTop="10dp"/>
            
        <TextView
            android:id="@+id/tvEmptyHistory"
            android:text="Nenhum lançamento encontrado.\nToque em 'Novo Lançamento' para começar."
            android:gravity="center"
            android:padding="30dp"
            android:background="#FFFFFF"
            android:textColor="#94A3B8"
            android:textSize="12sp"/>

    </LinearLayout>
</ScrollView>
"""
    write_file(f"{base_res}/activity_main.xml", dashboard_xml)

    # ==========================================================================
    # 2. LOGICA NATIVA (MainActivity.kt)
    # ==========================================================================
    # Removemos todo o código de WebView e colocamos lógica de Banco de Dados
    main_kt = """package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
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
"""
    write_file(f"{base_java}/MainActivity.kt", main_kt)
    
    print("🎉 Transição Concluída! O App agora é 100% Nativo (Sem WebView).")

if __name__ == "__main__":
    main()


