import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Criado/Atualizado: {path}")

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def main():
    print("🚀 Iniciando Módulo 2: Tela de Lançamento Nativa...")

    base_res = "app/src/main/res/layout"
    base_java = "app/src/main/java/com/motoristapro/android"

    # ==========================================================================
    # 1. LAYOUT XML (activity_add_daily.xml)
    # ==========================================================================
    layout_xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#F8FAFC"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- CABEÇALHO -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Novo Lançamento"
            android:textSize="24sp"
            android:textStyle="bold"
            android:textColor="#0F172A"
            android:layout_marginBottom="20dp"/>

        <!-- DATA -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#FFFFFF"
            android:padding="15dp"
            android:elevation="2dp"
            android:layout_marginBottom="15dp">
            
            <TextView
                android:text="DATA DO TRABALHO"
                android:textSize="11sp"
                android:textStyle="bold"
                android:textColor="#64748B"/>
                
            <TextView
                android:id="@+id/tvDate"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Selecionar Data"
                android:textSize="18sp"
                android:textStyle="bold"
                android:textColor="#2563EB"
                android:paddingTop="10dp"
                android:drawableEnd="@android:drawable/ic_menu_today"/>
        </LinearLayout>

        <!-- GANHOS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#FFFFFF"
            android:padding="15dp"
            android:elevation="2dp"
            android:layout_marginBottom="15dp">
            
            <TextView
                android:text="FATURAMENTO TOTAL"
                android:textSize="11sp"
                android:textStyle="bold"
                android:textColor="#64748B"/>
                
            <EditText
                android:id="@+id/etTotal"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="R$ 0.00"
                android:textSize="24sp"
                android:textStyle="bold"
                android:textColor="#10B981"
                android:inputType="numberDecimal"
                android:backgroundTint="#10B981"/>

            <TextView
                android:text="Detalhar (Opcional)"
                android:textSize="10sp"
                android:layout_marginTop="10dp"
                android:textColor="#94A3B8"/>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2">
                <EditText android:id="@+id/etUber" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:hint="Uber" android:inputType="numberDecimal" android:textSize="14sp"/>
                <EditText android:id="@+id/et99" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:hint="99 Pop" android:inputType="numberDecimal" android:textSize="14sp"/>
            </LinearLayout>
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2">
                <EditText android:id="@+id/etPart" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:hint="Particular" android:inputType="numberDecimal" android:textSize="14sp"/>
                <EditText android:id="@+id/etOutros" android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:hint="Outros" android:inputType="numberDecimal" android:textSize="14sp"/>
            </LinearLayout>
        </LinearLayout>

        <!-- DESPESAS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="#FFFFFF"
            android:padding="15dp"
            android:elevation="2dp"
            android:layout_marginBottom="15dp">
            
            <TextView android:text="DESPESAS DO DIA" android:textSize="11sp" android:textStyle="bold" android:textColor="#EF4444"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="3" android:layout_marginTop="10dp">
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1">
                    <TextView android:text="Combustível" android:textSize="10sp"/>
                    <EditText android:id="@+id/etComb" android:layout_width="match_parent" android:layout_height="wrap_content" android:inputType="numberDecimal" android:hint="0.00"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1">
                    <TextView android:text="Alimentação" android:textSize="10sp"/>
                    <EditText android:id="@+id/etAlim" android:layout_width="match_parent" android:layout_height="wrap_content" android:inputType="numberDecimal" android:hint="0.00"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1">
                    <TextView android:text="Manutenção" android:textSize="10sp"/>
                    <EditText android:id="@+id/etManu" android:layout_width="match_parent" android:layout_height="wrap_content" android:inputType="numberDecimal" android:hint="0.00"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- OPERACIONAL -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:background="#FFFFFF"
            android:padding="15dp"
            android:elevation="2dp"
            android:layout_marginBottom="30dp"
            android:weightSum="2">
            
            <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingEnd="10dp">
                <TextView android:text="KM TOTAL" android:textSize="11sp" android:textStyle="bold" android:textColor="#64748B"/>
                <EditText android:id="@+id/etKm" android:layout_width="match_parent" android:layout_height="wrap_content" android:inputType="numberDecimal" android:hint="0.0"/>
            </LinearLayout>
            
            <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingStart="10dp">
                <TextView android:text="HORAS" android:textSize="11sp" android:textStyle="bold" android:textColor="#64748B"/>
                <EditText android:id="@+id/etHoras" android:layout_width="match_parent" android:layout_height="wrap_content" android:inputType="numberDecimal" android:hint="0.0"/>
            </LinearLayout>
        </LinearLayout>

        <Button
            android:id="@+id/btnSave"
            android:layout_width="match_parent"
            android:layout_height="60dp"
            android:text="SALVAR NO CELULAR"
            android:backgroundTint="#2563EB"
            android:textSize="16sp"
            android:textStyle="bold"/>

    </LinearLayout>
</ScrollView>
"""
    write_file(f"{base_res}/activity_add_daily.xml", layout_xml)

    # ==========================================================================
    # 2. ACTIVITY KOTLIN (AddDailyActivity.kt)
    # ==========================================================================
    activity_kt = """package com.motoristapro.android

import android.app.DatePickerDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.motoristapro.android.data.AppDatabase
import com.motoristapro.android.data.entities.DiarioEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class AddDailyActivity : AppCompatActivity() {

    private val calendar = Calendar.getInstance()
    private lateinit var tvDate: TextView
    private lateinit var etTotal: EditText
    
    // Inputs
    private lateinit var etUber: EditText
    private lateinit var et99: EditText
    private lateinit var etPart: EditText
    private lateinit var etOutros: EditText
    private lateinit var etComb: EditText
    private lateinit var etAlim: EditText
    private lateinit var etManu: EditText
    private lateinit var etKm: EditText
    private lateinit var etHoras: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_add_daily)

        initViews()
        setupDatePicker()
        setupAutoSum()
        
        findViewById<Button>(R.id.btnSave).setOnClickListener { saveEntry() }
    }

    private fun initViews() {
        tvDate = findViewById(R.id.tvDate)
        etTotal = findViewById(R.id.etTotal)
        etUber = findViewById(R.id.etUber)
        et99 = findViewById(R.id.et99)
        etPart = findViewById(R.id.etPart)
        etOutros = findViewById(R.id.etOutros)
        etComb = findViewById(R.id.etComb)
        etAlim = findViewById(R.id.etAlim)
        etManu = findViewById(R.id.etManu)
        etKm = findViewById(R.id.etKm)
        etHoras = findViewById(R.id.etHoras)
        
        updateDateLabel()
    }

    private fun setupDatePicker() {
        tvDate.setOnClickListener {
            DatePickerDialog(this, { _, year, month, day ->
                calendar.set(year, month, day)
                updateDateLabel()
            }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show()
        }
    }

    private fun updateDateLabel() {
        val fmt = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
        tvDate.text = fmt.format(calendar.time)
    }

    private fun setupAutoSum() {
        val watcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { calculateTotal() }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        }
        etUber.addTextChangedListener(watcher)
        et99.addTextChangedListener(watcher)
        etPart.addTextChangedListener(watcher)
        etOutros.addTextChangedListener(watcher)
    }

    private fun calculateTotal() {
        val u = etUber.text.toString().toDoubleOrNull() ?: 0.0
        val n = et99.text.toString().toDoubleOrNull() ?: 0.0
        val p = etPart.text.toString().toDoubleOrNull() ?: 0.0
        val o = etOutros.text.toString().toDoubleOrNull() ?: 0.0
        val sum = u + n + p + o
        if (sum > 0) etTotal.setText(String.format("%.2f", sum).replace(",", "."))
    }

    private fun saveEntry() {
        val total = etTotal.text.toString().toDoubleOrNull()
        if (total == null || total <= 0) {
            Toast.makeText(this, "Informe o Faturamento Total", Toast.LENGTH_SHORT).show()
            return
        }

        val diario = DiarioEntity(
            data = calendar.timeInMillis,
            ganhoBruto = total,
            ganhoUber = etUber.text.toString().toDoubleOrNull() ?: 0.0,
            ganho99 = et99.text.toString().toDoubleOrNull() ?: 0.0,
            ganhoPart = etPart.text.toString().toDoubleOrNull() ?: 0.0,
            ganhoOutros = etOutros.text.toString().toDoubleOrNull() ?: 0.0,
            despCombustivel = etComb.text.toString().toDoubleOrNull() ?: 0.0,
            despAlimentacao = etAlim.text.toString().toDoubleOrNull() ?: 0.0,
            despManutencao = etManu.text.toString().toDoubleOrNull() ?: 0.0,
            kmPercorrido = etKm.text.toString().toDoubleOrNull() ?: 0.0,
            horasTrabalhadas = etHoras.text.toString().toDoubleOrNull() ?: 0.0,
            isSynced = false
        )

        // Salvar no Banco (Background)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val db = AppDatabase.getDatabase(applicationContext)
                db.diarioDao().insert(diario)
                
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@AddDailyActivity, "✅ Guardado no telemóvel!", Toast.LENGTH_LONG).show()
                    finish() // Fecha e volta pra home
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@AddDailyActivity, "Erro ao guardar: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
"""
    write_file(f"{base_java}/AddDailyActivity.kt", activity_kt)

    # ==========================================================================
    # 3. ATUALIZAR MANIFESTO (Registar Activity)
    # ==========================================================================
    manifest_path = "app/src/main/AndroidManifest.xml"
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = f.read()
        
        if ".AddDailyActivity" not in manifest:
            # Adiciona antes de fechar application
            idx = manifest.rfind("</application>")
            new_entry = '        <activity android:name=".AddDailyActivity" android:exported="false" android:windowSoftInputMode="adjustResize"/>\n    '
            manifest = manifest[:idx] + new_entry + manifest[idx:]
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(manifest)
            print("✅ Manifesto atualizado.")

    # ==========================================================================
    # 4. ATUALIZAR HOME (Botão para abrir Lançamento)
    # ==========================================================================
    # Assumindo que a Home é HomeActivity.kt e o layout é activity_home.xml
    
    # 4.1 Adicionar botão no XML da Home
    home_xml = "app/src/main/res/layout/activity_home.xml"
    if os.path.exists(home_xml):
        with open(home_xml, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Inserimos um botão novo se não existir
        if "btnAddDaily" not in content:
            new_btn = """
    <Button
        android:id="@+id/btnAddDaily"
        android:layout_width="match_parent"
        android:layout_height="60dp"
        android:text="LANÇAR GANHOS (OFFLINE)"
        android:backgroundTint="#F59E0B"
        android:textStyle="bold"
        android:layout_marginTop="20dp"/>
            """
            # Insere antes do fechamento do LinearLayout
            idx = content.rfind("</LinearLayout>")
            content = content[:idx] + new_btn + content[idx:]
            
            with open(home_xml, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Botão adicionado na Home XML.")

    # 4.2 Lógica do botão no Kotlin
    home_kt = f"{base_java}/HomeActivity.kt"
    if os.path.exists(home_kt):
        with open(home_kt, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "btnAddDaily" not in content:
            # Insere listener
            listener = """
        findViewById<Button>(R.id.btnAddDaily)?.setOnClickListener {
            startActivity(Intent(this, AddDailyActivity::class.java))
        }
            """
            # Procura onCreate e insere no fim dele (antes da chave de fecho)
            # Simplificação: Procurar o último setOnClickListener e adicionar depois
            idx = content.rfind("}")
            idx = content.rfind("}", 0, idx) # Penúltima chave (fim do onCreate)
            
            content = content[:idx] + listener + content[idx:]
            
            with open(home_kt, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Lógica do botão adicionada na Home Kotlin.")

    print("🎉 Módulo 2 Completo! Rode './gradlew assembleDebug' para testar.")

if __name__ == "__main__":
    main()


