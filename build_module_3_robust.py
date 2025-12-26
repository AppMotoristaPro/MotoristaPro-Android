import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Criado: {path}")

def main():
    print("🛡️ Iniciando Módulo 3 (Histórico) com Verificação de Erros...")

    base_res = "app/src/main/res/layout"
    base_java = "app/src/main/java/com/motoristapro/android"
    gradle_path = "app/build.gradle.kts"

    # ==========================================================================
    # 0. PRÉ-REQUISITO: RECYCLERVIEW NO GRADLE
    # ==========================================================================
    # Sem isso, o app crasha ao tentar carregar a lista
    if os.path.exists(gradle_path):
        with open(gradle_path, 'r', encoding='utf-8') as f:
            gradle_content = f.read()
        
        if "recyclerview" not in gradle_content:
            print("📦 Adicionando dependência RecyclerView...")
            dep = '    implementation("androidx.recyclerview:recyclerview:1.3.2")'
            if "dependencies {" in gradle_content:
                gradle_content = gradle_content.replace("dependencies {", "dependencies {\n" + dep)
                write_file(gradle_path, gradle_content)
                # Força limpeza para garantir download
                os.system("./gradlew clean")

    # ==========================================================================
    # 1. ITEM DA LISTA (item_history.xml)
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
        android:minWidth="55dp">
        
        <TextView
            android:id="@+id/tvDay"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="01"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="@color/text_main"
            android:includeFontPadding="false"/>
            
        <TextView
            android:id="@+id/tvMonth"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="JAN"
            android:textSize="11sp"
            android:textStyle="bold"
            android:textAllCaps="true"
            android:textColor="@color/text_secondary"
            android:includeFontPadding="false"/>
    </LinearLayout>

    <!-- INFO CENTRO -->
    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical">
        
        <TextView
            android:id="@+id/tvApps"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Carregando..."
            android:textSize="14sp"
            android:textStyle="bold"
            android:ellipsize="end"
            android:maxLines="1"
            android:textColor="@color/text_main"/>
            
        <TextView
            android:id="@+id/tvDetails"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="-- km • -- h"
            android:textSize="12sp"
            android:textColor="@color/text_secondary"
            android:layout_marginTop="3dp"/>
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
            android:text="R$ 0,00"
            android:textSize="15sp"
            android:textStyle="bold"
            android:textColor="@color/accent"/>
            
        <TextView
            android:id="@+id/tvExpense"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="- R$ 0,00"
            android:textSize="11sp"
            android:textColor="@color/danger"
            android:layout_marginTop="3dp"
            android:visibility="gone"/>
    </LinearLayout>

</LinearLayout>
"""
    write_file(f"{base_res}/item_history.xml", item_xml)

    # ==========================================================================
    # 2. LAYOUT TELA (activity_history.xml)
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
        android:padding="24dp"
        android:background="@color/white"
        android:elevation="4dp">
        
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical">
            
            <ImageView
                android:id="@+id/btnBack"
                android:layout_width="40dp"
                android:layout_height="40dp"
                android:src="@android:drawable/ic_menu_revert"
                android:padding="10dp"
                android:background="@drawable/bg_input_field"
                android:elevation="0dp"
                android:layout_marginEnd="15dp"
                android:clickable="true"
                android:focusable="true"
                android:tint="@color/text_main"/>

            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:orientation="vertical">
                
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Histórico"
                    android:textSize="22sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_main"/>
                    
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Livro Caixa Digital"
                    android:textSize="13sp"
                    android:textColor="@color/text_secondary"/>
            </LinearLayout>
        </LinearLayout>
        
        <!-- FILTROS DE DATA (ESTÁTICOS POR ENQUANTO) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:layout_marginTop="25dp"
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
        android:padding="20dp"
        android:clipToPadding="false"
        android:scrollbars="vertical"/>

</LinearLayout>
"""
    write_file(f"{base_res}/activity_history.xml", history_layout)

    # ==========================================================================
    # 3. ADAPTER (HistoryAdapter.kt) - Com Tratamento de Nulos
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
        try {
            val item = list[position]
            val context = holder.itemView.context
            val ptBr = Locale("pt", "BR")

            // Formatação de Data Segura
            try {
                if (item.dateString.contains("/")) {
                    val parts = item.dateString.split("/")
                    if (parts.size >= 2) {
                        holder.tvDay.text = parts[0]
                        val meses = listOf("","JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ")
                        val mesIdx = parts[1].toIntOrNull() ?: 0
                        holder.tvMonth.text = if (mesIdx in 1..12) meses[mesIdx] else parts[1]
                    }
                } else {
                    holder.tvDay.text = "?"
                }
            } catch(e: Exception) {
                holder.tvDay.text = "--"
            }

            // Valores Monetários
            val format = NumberFormat.getCurrencyInstance(ptBr)
            holder.tvValue.text = "+ " + format.format(item.totalAmount)
            holder.tvValue.setTextColor(android.graphics.Color.parseColor("#10B981")) // Verde (Hardcoded para segurança)

            if (item.expenses > 0) {
                holder.tvExpense.text = "- " + format.format(item.expenses)
                holder.tvExpense.visibility = View.VISIBLE
                holder.tvExpense.setTextColor(android.graphics.Color.parseColor("#EF4444")) // Vermelho
            } else {
                holder.tvExpense.visibility = View.GONE
            }

            // Lista de Apps
            val apps = ArrayList<String>()
            if (item.uber > 0) apps.add("Uber")
            if (item.pop > 0) apps.add("99")
            if (item.part > 0) apps.add("Part")
            if (item.others > 0) apps.add("Out")
            if (apps.isEmpty()) apps.add("Geral")
            
            holder.tvApps.text = apps.joinToString(" • ")

            // Detalhes (KM e Horas)
            holder.tvDetails.text = String.format(Locale.US, "%.0f km • %.1f h", item.km, item.hours)
            
        } catch (e: Exception) {
            // Evita crash se der erro no bind
            holder.tvApps.text = "Erro ao exibir item"
        }
    }

    override fun getItemCount() = list.size
}
"""
    write_file(f"{base_java}/HistoryAdapter.kt", adapter_kt)

    # ==========================================================================
    # 4. ACTIVITY (HistoryActivity.kt) - Inicialização Segura
    # ==========================================================================
    activity_kt = """package com.motoristapro.android

import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.motoristapro.android.data.DailyRepository

class HistoryActivity : AppCompatActivity() {

    // Variáveis com ? (Nullable) para segurança
    private var recyclerView: RecyclerView? = null
    private var btnBack: ImageView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_history)

            // Inicialização com IDs explícitos
            recyclerView = findViewById(R.id.recyclerView)
            btnBack = findViewById(R.id.btnBack)
            
            // Configura RecyclerView
            if (recyclerView != null) {
                recyclerView!!.layoutManager = LinearLayoutManager(this)
            }
            
            // Configura Botão Voltar
            btnBack?.setOnClickListener { finish() }

            loadData()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI Histórico: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun loadData() {
        try {
            val repo = DailyRepository(this)
            val list = repo.getAll()
            
            if (list.isEmpty()) {
                Toast.makeText(this, "Nenhum registo encontrado.", Toast.LENGTH_SHORT).show()
            }
            
            if (recyclerView != null) {
                val adapter = HistoryAdapter(list)
                recyclerView!!.adapter = adapter
            }
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro ao carregar lista: " + e.message, Toast.LENGTH_SHORT).show()
        }
    }
}
"""
    write_file(f"{base_java}/HistoryActivity.kt", activity_kt)

    # ==========================================================================
    # 5. REGISTRO NO MANIFEST
    # ==========================================================================
    manifest_path = "app/src/main/AndroidManifest.xml"
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = f.read()
        
        # Só adiciona se não existir
        if ".HistoryActivity" not in manifest:
            idx = manifest.rfind("</application>")
            new_entry = '        <activity android:name=".HistoryActivity" android:exported="false"/>\n    '
            manifest = manifest[:idx] + new_entry + manifest[idx:]
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest)
            print("✅ Manifesto atualizado.")

    # ==========================================================================
    # 6. ATUALIZAÇÃO DA HOME (Linkar Botão)
    # ==========================================================================
    # Vamos garantir que o clique no card de histórico abra a nova activity
    main_kt_path = f"{base_java}/MainActivity.kt"
    if os.path.exists(main_kt_path):
        with open(main_kt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Adiciona listener se não tiver
        if "HistoryActivity::class.java" not in content:
            # Procura um ponto seguro (final do onCreate)
            # A estratégia segura é substituir a função inteira ou inserir num ponto conhecido
            # Vamos procurar onde definimos o btnRobo e adicionar logo abaixo
            
            search_str = "checkPermissionsAndStart()\n            }"
            add_code = """
            }
            
            // Link Histórico
            findViewById<View>(R.id.tvEmptyHistory)?.setOnClickListener {
                try { startActivity(Intent(this, HistoryActivity::class.java)) } catch(e: Exception){}
            }
            """
            
            if search_str in content:
                content = content.replace(search_str, search_str + add_code.replace("}", "", 1)) # Hack simples
                # Na verdade, é melhor apenas adicionar no final do onCreate se for muito complexo achar
                # Mas vamos tentar:
                
                new_content = content.replace(search_str, "checkPermissionsAndStart()\n            }\n\n            findViewById<View>(R.id.tvEmptyHistory)?.setOnClickListener {\n                startActivity(Intent(this, HistoryActivity::class.java))\n            }")
                
                with open(main_kt_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ Home linkada ao Histórico.")
            else:
                print("⚠️ Não encontrei o ponto de inserção na Home. Adicione o clique manualmente depois.")

    # Versionamento
    os.system("python3 auto_version.py")
    
    print("🚀 Módulo 3 Concluído e Blindado. Compile agora!")

if __name__ == "__main__":
    main()


