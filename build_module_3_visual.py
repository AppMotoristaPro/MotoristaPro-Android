import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Criado: {path}")

def main():
    print("📜 Iniciando Módulo 3: Tela de Histórico (Réplica do Site)...")

    base_res = "app/src/main/res/layout"
    base_java = "app/src/main/java/com/motoristapro/android"

    # ==========================================================================
    # 1. ITEM DA LISTA (item_history.xml)
    # Réplica exata do card do site: Data Esq | Info Meio | R$ Dir
    # ==========================================================================
    item_xml = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:background="@drawable/bg_glass_card"
    android:padding="15dp"
    android:layout_marginBottom="12dp"
    android:gravity="center_vertical"
    android:elevation="2dp">

    <!-- DATA (Box Branco Pequeno) -->
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:gravity="center"
        android:background="@drawable/bg_input_field"
        android:padding="8dp"
        android:layout_marginEnd="15dp"
        android:minWidth="50dp">
        
        <TextView
            android:id="@+id/tvDay"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="01"
            android:textSize="18sp"
            android:textStyle="bold"
            android:textColor="@color/text_main"
            android:includeFontPadding="false"/>
            
        <TextView
            android:id="@+id/tvMonth"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="JAN"
            android:textSize="10sp"
            android:textStyle="bold"
            android:textAllCaps="true"
            android:textColor="@color/text_secondary"
            android:includeFontPadding="false"/>
    </LinearLayout>

    <!-- INFO CENTRO (Apps e Detalhes) -->
    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">
        
        <TextView
            android:id="@+id/tvApps"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Uber • 99"
            android:textSize="14sp"
            android:textStyle="bold"
            android:textColor="@color/text_main"/>
            
        <TextView
            android:id="@+id/tvDetails"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="0km • 0h"
            android:textSize="11sp"
            android:textColor="@color/text_secondary"
            android:layout_marginTop="2dp"/>
    </LinearLayout>

    <!-- VALORES (Direita) -->
    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:gravity="end">
        
        <TextView
            android:id="@+id/tvValue"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="+ R$ 0,00"
            android:textSize="14sp"
            android:textStyle="bold"
            android:textColor="@color/accent"/>
            
        <TextView
            android:id="@+id/tvExpense"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="- R$ 0,00"
            android:textSize="10sp"
            android:textColor="@color/danger"
            android:layout_marginTop="2dp"/>
    </LinearLayout>

</LinearLayout>
"""
    write_file(f"{base_res}/item_history.xml", item_xml)

    # ==========================================================================
    # 2. TELA PRINCIPAL (activity_history.xml)
    # Com filtros de Dia, Semana, Mês iguais ao site
    # ==========================================================================
    history_layout = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="@color/bg_body">

    <!-- HEADER -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp"
        android:background="@color/white"
        android:elevation="4dp">
        
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical">
            
            <ImageView
                android:id="@+id/btnBack"
                android:layout_width="35dp"
                android:layout_height="35dp"
                android:src="@android:drawable/ic_menu_revert"
                android:background="@drawable/bg_input_field"
                android:padding="8dp"
                android:tint="@color/text_main"
                android:layout_marginEnd="15dp"
                android:clickable="true"
                android:focusable="true"/>

            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:orientation="vertical">
                
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Histórico"
                    android:textSize="20sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_main"/>
                    
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Livro Caixa Digital"
                    android:textSize="12sp"
                    android:textColor="@color/text_secondary"/>
            </LinearLayout>
        </LinearLayout>
        
        <!-- FILTROS (Visual - Lógica será implementada depois) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:layout_marginTop="20dp"
            android:weightSum="3"
            android:background="@drawable/bg_input_field"
            android:padding="4dp">
            
            <TextView
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="DIA"
                android:gravity="center"
                android:padding="10dp"
                android:textSize="12sp"
                android:textStyle="bold"
                android:textColor="@color/text_secondary"/>
                
            <TextView
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="SEMANA"
                android:gravity="center"
                android:padding="10dp"
                android:textSize="12sp"
                android:textStyle="bold"
                android:background="@drawable/bg_glass_card"
                android:textColor="@color/primary"/>
                
            <TextView
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:text="MÊS"
                android:gravity="center"
                android:padding="10dp"
                android:textSize="12sp"
                android:textStyle="bold"
                android:textColor="@color/text_secondary"/>
        </LinearLayout>
    </LinearLayout>

    <!-- LISTA (RecyclerView) -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:padding="15dp"
        android:clipToPadding="false"/>

</LinearLayout>
"""
    write_file(f"{base_res}/activity_history.xml", history_layout)

    # ==========================================================================
    # 3. ADAPTER (Lógica da Lista) - HistoryAdapter.kt
    # ==========================================================================
    adapter_kt = """package com.motoristapro.android

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.motoristapro.android.data.DailyEntry
import java.text.NumberFormat
import java.util.Locale

class HistoryAdapter(private val list: List<DailyEntry>) : RecyclerView.Adapter<HistoryAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvDay: TextView = view.findViewById(R.id.tvDay)
        val tvMonth: TextView = view.findViewById(R.id.tvMonth)
        val tvApps: TextView = view.findViewById(R.id.tvApps)
        val tvDetails: TextView = view.findViewById(R.id.tvDetails)
        val tvValue: TextView = view.findViewById(R.id.tvValue)
        val tvExpense: TextView = view.findViewById(R.id.tvExpense)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_history, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = list[position]
        val ptBr = Locale("pt", "BR")

        // Data (Ex: 25/12/2025)
        try {
            val parts = item.dateString.split("/")
            holder.tvDay.text = parts[0]
            val meses = listOf("","JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ")
            val mesIdx = parts[1].toInt()
            holder.tvMonth.text = if (mesIdx <= 12) meses[mesIdx] else parts[1]
        } catch(e: Exception) {
            holder.tvDay.text = "--"
            holder.tvMonth.text = ""
        }

        // Valores
        val format = NumberFormat.getCurrencyInstance(ptBr)
        holder.tvValue.text = "+ " + format.format(item.totalAmount)
        
        // Despesa (Se tiver)
        if (item.expenses > 0) {
            holder.tvExpense.text = "- " + format.format(item.expenses)
            holder.tvExpense.visibility = View.VISIBLE
        } else {
            holder.tvExpense.visibility = View.GONE
        }

        // Apps
        val apps = ArrayList<String>()
        if (item.uber > 0) apps.add("Uber")
        if (item.pop > 0) apps.add("99")
        if (item.part > 0) apps.add("Part")
        if (item.others > 0) apps.add("Out")
        if (apps.isEmpty()) apps.add("Geral")
        
        // Limita a 3 apps para não quebrar layout
        val appsText = if (apps.size > 3) apps.take(3).joinToString(" • ") + "..." else apps.joinToString(" • ")
        holder.tvApps.text = appsText

        // Detalhes
        holder.tvDetails.text = String.format(Locale.US, "%.0f km • %.1f h", item.km, item.hours)
    }

    override fun getItemCount() = list.size
}
"""
    write_file(f"{base_java}/HistoryAdapter.kt", adapter_kt)

    # ==========================================================================
    # 4. ACTIVITY (Lógica da Tela) - HistoryActivity.kt
    # ==========================================================================
    activity_kt = """package com.motoristapro.android

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.motoristapro.android.data.DailyRepository

class HistoryActivity : AppCompatActivity() {

    private var recyclerView: RecyclerView? = null
    private var btnBack: View? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_history)

            recyclerView = findViewById(R.id.recyclerView)
            btnBack = findViewById(R.id.btnBack)
            
            recyclerView?.layoutManager = LinearLayoutManager(this)
            
            btnBack?.setOnClickListener { finish() }

            loadData()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun loadData() {
        try {
            val repo = DailyRepository(this)
            val list = repo.getAll()
            
            if (list.isEmpty()) {
                Toast.makeText(this, "Nenhum registo encontrado.", Toast.LENGTH_SHORT).show()
            }
            
            val adapter = HistoryAdapter(list)
            recyclerView?.adapter = adapter
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro ao carregar: " + e.message, Toast.LENGTH_SHORT).show()
        }
    }
}
"""
    write_file(f"{base_java}/HistoryActivity.kt", activity_kt)

    # ==========================================================================
    # 5. ATUALIZAR MANIFESTO
    # ==========================================================================
    manifest_path = "app/src/main/AndroidManifest.xml"
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = f.read()
        
        if ".HistoryActivity" not in manifest:
            idx = manifest.rfind("</application>")
            # Adiciona activity
            new_entry = '        <activity android:name=".HistoryActivity" android:exported="false"/>\n    '
            manifest = manifest[:idx] + new_entry + manifest[idx:]
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest)
            print("✅ Manifesto atualizado.")

    # ==========================================================================
    # 6. LIGAR BOTÃO NA HOME
    # ==========================================================================
    main_kt_path = f"{base_java}/MainActivity.kt"
    if os.path.exists(main_kt_path):
        with open(main_kt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar listener no tvEmptyHistory (Card Inferior)
        if "HistoryActivity::class.java" not in content:
            # Procura um lugar seguro (dentro do onCreate)
            # Vamos procurar o listener do btnRobo e colocar depois
            anchor = "checkPermissionsAndStart()"
            new_code = """
            }
            
            // Botão Histórico (Card Inferior)
            findViewById<View>(R.id.tvEmptyHistory)?.setOnClickListener {
                startActivity(Intent(this, HistoryActivity::class.java))
            """
            # Substitui o fechamento do bloco anterior
            content = content.replace("checkPermissionsAndStart()\n            }", "checkPermissionsAndStart()" + new_code)
            
            with open(main_kt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Home ligada ao Histórico.")

    # Versionamento
    os.system("python3 auto_version.py")
    print("🎉 Módulo 3 Prontos! Compile agora.")

if __name__ == "__main__":
    main()


