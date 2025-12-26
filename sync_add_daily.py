import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo Sincronizado: {path}")

def main():
    print("🚑 Sincronizando IDs do XML com Variáveis Kotlin...")

    # ==========================================================================
    # 1. XML (activity_add_daily.xml) - IDs Garantidos
    # ==========================================================================
    xml_code = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_body"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- HEADER COM BOTÃO VOLTAR -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="25dp">
            
            <ImageView
                android:id="@+id/btnBack"
                android:layout_width="40dp"
                android:layout_height="40dp"
                android:src="@android:drawable/ic_menu_revert"
                android:padding="8dp"
                android:background="@drawable/bg_glass_card"
                android:elevation="2dp"
                android:clickable="true"
                android:focusable="true"
                android:tint="@color/text_main"/>
                
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:gravity="center">
                
                <TextView
                    android:text="Novo Lançamento"
                    android:textSize="18sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_main"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
                
                <TextView
                    android:text="Fechamento do Dia"
                    android:textSize="12sp"
                    android:textColor="@color/text_secondary"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
            </LinearLayout>
        </LinearLayout>

        <!-- 1. DATA E TOTAIS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="15dp">
            
            <TextView android:text="RESUMO" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="15dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <TextView android:text="DATA DO TRABALHO" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            <TextView android:id="@+id/tvDate" android:layout_width="match_parent" android:layout_height="50dp" android:text="Hoje" android:textSize="16sp" android:textStyle="bold" android:textColor="@color/text_main" android:background="@drawable/bg_input_field" android:gravity="center_vertical" android:paddingStart="15dp" android:layout_marginBottom="15dp"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2">
                <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginEnd="5dp">
                    <TextView android:text="KM TOTAL" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etKm" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:hint="0.0"/>
                </LinearLayout>
                <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginStart="5dp">
                    <TextView android:text="HORAS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etHoras" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:hint="0.0"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- 2. FATURAMENTO -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="15dp">
            
            <LinearLayout android:orientation="horizontal" android:layout_width="match_parent" android:layout_height="wrap_content" android:gravity="center_vertical">
                <TextView android:text="FATURAMENTO" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/accent" android:layout_weight="1" android:layout_width="0dp" android:layout_height="wrap_content"/>
                <TextView android:id="@+id/badgeTotal" android:text="R$ 0,00" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/white" android:background="@drawable/bg_gradient_primary" android:padding="6dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            </LinearLayout>

            <EditText
                android:id="@+id/etTotal"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="R$ 0,00"
                android:textSize="32sp"
                android:textStyle="bold"
                android:textColor="@color/accent"
                android:background="@null"
                android:inputType="numberDecimal"
                android:paddingTop="15dp"
                android:paddingBottom="15dp"/>
            
            <View android:layout_width="match_parent" android:layout_height="1dp" android:background="#E2E8F0" android:layout_marginBottom="15dp"/>

            <!-- ADDER DE GANHOS -->
            <TextView android:text="DETALHAR GANHOS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="10dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical">
                <EditText 
                    android:id="@+id/etNewEarnValue" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:layout_height="50dp" 
                    android:hint="R$ 0,00" 
                    android:inputType="numberDecimal" 
                    android:textColor="@color/accent"
                    android:textStyle="bold"
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp"
                    android:layout_marginEnd="10dp"/>
                
                <Spinner
                    android:id="@+id/spNewEarnType"
                    android:layout_width="110dp"
                    android:layout_height="50dp"
                    android:background="@drawable/bg_input_field"
                    android:padding="5dp"
                    android:layout_marginEnd="10dp"/>
                    
                <ImageView
                    android:id="@+id/btnAddEarn"
                    android:layout_width="50dp"
                    android:layout_height="50dp"
                    android:src="@android:drawable/ic_input_add"
                    android:background="@drawable/bg_gradient_primary"
                    android:padding="12dp"
                    android:clickable="true"
                    android:focusable="true"
                    android:tint="@color/white"/>
            </LinearLayout>

            <!-- LISTA DE GANHOS -->
            <LinearLayout
                android:id="@+id/containerEarnings"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="10dp"/>
        </LinearLayout>

        <!-- 3. CORRIDAS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="15dp">
            
            <TextView android:text="QUANTIDADE DE VIAGENS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="10dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="4">
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center">
                    <TextView android:text="UBER" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtdUber" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center" android:layout_marginStart="5dp">
                    <TextView android:text="99" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtd99" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center" android:layout_marginStart="5dp">
                    <TextView android:text="PART" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtdPart" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center" android:layout_marginStart="5dp">
                    <TextView android:text="OUT" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtdOutros" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- 4. DESPESAS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="25dp">
            
            <TextView android:text="DESPESAS DO DIA" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/danger" android:layout_marginBottom="10dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical">
                <EditText 
                    android:id="@+id/etNewExpValue" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:layout_height="50dp" 
                    android:hint="R$ 0,00" 
                    android:inputType="numberDecimal" 
                    android:textColor="@color/danger"
                    android:textStyle="bold"
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp"
                    android:layout_marginEnd="10dp"/>
                
                <Spinner
                    android:id="@+id/spNewExpType"
                    android:layout_width="110dp"
                    android:layout_height="50dp"
                    android:background="@drawable/bg_input_field"
                    android:padding="5dp"
                    android:layout_marginEnd="10dp"/>
                    
                <ImageView
                    android:id="@+id/btnAddExp"
                    android:layout_width="50dp"
                    android:layout_height="50dp"
                    android:src="@android:drawable/ic_input_add"
                    android:background="@drawable/bg_gradient_primary"
                    android:padding="12dp"
                    android:clickable="true"
                    android:focusable="true"
                    android:tint="@color/white"/>
            </LinearLayout>

            <LinearLayout
                android:id="@+id/containerExpenses"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="10dp"/>
        </LinearLayout>

        <Button
            android:id="@+id/btnSave"
            android:layout_width="match_parent"
            android:layout_height="60dp"
            android:text="CONFIRMAR LANÇAMENTO"
            android:background="@drawable/bg_gradient_primary"
            android:textColor="#FFFFFF"
            android:textSize="16sp"
            android:textStyle="bold"
            android:elevation="5dp"/>

    </LinearLayout>
</ScrollView>
"""
    write_file("app/src/main/res/layout/activity_add_daily.xml", xml_code)


    # ==========================================================================
    # 2. KOTLIN (AddDailyActivity.kt) - Variáveis Declaradas
    # ==========================================================================
    kt_code = """package com.motoristapro.android

import android.app.DatePickerDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.motoristapro.android.data.DailyEntry
import com.motoristapro.android.data.DailyRepository
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.*

class AddDailyActivity : AppCompatActivity() {

    private val calendar = Calendar.getInstance()
    private val localeBR = Locale("pt", "BR")
    
    // UI - Variáveis Nullable (Segurança contra crash)
    private var btnBack: View? = null
    private var tvDate: TextView? = null
    private var etTotal: EditText? = null
    private var badgeTotal: TextView? = null
    
    private var etNewEarnValue: EditText? = null
    private var spNewEarnType: Spinner? = null
    private var btnAddEarn: View? = null
    private var containerEarnings: LinearLayout? = null
    
    private var etNewExpValue: EditText? = null
    private var spNewExpType: Spinner? = null
    private var btnAddExp: View? = null
    private var containerExpenses: LinearLayout? = null
    
    private var qtdUber: EditText? = null
    private var qtd99: EditText? = null
    private var qtdPart: EditText? = null
    private var qtdOutros: EditText? = null
    
    private var etKm: EditText? = null
    private var etHoras: EditText? = null
    private var btnSave: Button? = null

    // Listas em memória
    private val earningItems = ArrayList<HistoryItem>()
    private val expenseItems = ArrayList<HistoryItem>()

    data class HistoryItem(val type: String, val name: String, val value: Double)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_add_daily)
            
            // 1. Inicializa TODAS as views
            initViews()
            
            // 2. Configura Adapters e Listeners
            setupSpinners()
            setupFormatters()
            updateDateLabel()
            setupListeners()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun initViews() {
        btnBack = findViewById(R.id.btnBack)
        tvDate = findViewById(R.id.tvDate)
        etTotal = findViewById(R.id.etTotal)
        badgeTotal = findViewById(R.id.badgeTotal)
        
        etNewEarnValue = findViewById(R.id.etNewEarnValue)
        spNewEarnType = findViewById(R.id.spNewEarnType)
        btnAddEarn = findViewById(R.id.btnAddEarn)
        containerEarnings = findViewById(R.id.containerEarnings)
        
        etNewExpValue = findViewById(R.id.etNewExpValue)
        spNewExpType = findViewById(R.id.spNewExpType)
        btnAddExp = findViewById(R.id.btnAddExp)
        containerExpenses = findViewById(R.id.containerExpenses)
        
        qtdUber = findViewById(R.id.qtdUber)
        qtd99 = findViewById(R.id.qtd99)
        qtdPart = findViewById(R.id.qtdPart)
        qtdOutros = findViewById(R.id.qtdOutros)
        
        etKm = findViewById(R.id.etKm)
        etHoras = findViewById(R.id.etHoras)
        btnSave = findViewById(R.id.btnSave)
    }

    private fun setupListeners() {
        btnBack?.setOnClickListener { finish() }
        
        tvDate?.setOnClickListener {
            DatePickerDialog(this, { _, y, m, d ->
                calendar.set(y, m, d)
                updateDateLabel()
            }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show()
        }
        
        btnAddEarn?.setOnClickListener { addEarning() }
        btnAddExp?.setOnClickListener { addExpense() }
        btnSave?.setOnClickListener { saveEntry() }
    }

    private fun setupSpinners() {
        val earnTypes = listOf("Uber", "99", "Part", "Outros")
        if (spNewEarnType != null) {
            spNewEarnType!!.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, earnTypes)
        }
        
        val expTypes = listOf("Combustível", "Alimentação", "Manutenção")
        if (spNewExpType != null) {
            spNewExpType!!.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, expTypes)
        }
    }

    private fun setupFormatters() {
        if (etTotal != null) etTotal!!.addTextChangedListener(CurrencyTextWatcher(etTotal!!))
        if (etNewEarnValue != null) etNewEarnValue!!.addTextChangedListener(CurrencyTextWatcher(etNewEarnValue!!))
        if (etNewExpValue != null) etNewExpValue!!.addTextChangedListener(CurrencyTextWatcher(etNewExpValue!!))
        
        etTotal?.addTextChangedListener(object: TextWatcher {
            override fun afterTextChanged(s: Editable?) { badgeTotal?.text = s.toString() }
            override fun beforeTextChanged(s: CharSequence?, start: Int, c: Int, a: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, b: Int, c: Int) {}
        })
    }

    private fun updateDateLabel() {
        val fmt = SimpleDateFormat("dd/MM/yyyy", localeBR)
        tvDate?.text = fmt.format(calendar.time)
    }
    
    // --- LÓGICA DE LISTA ---
    private fun addEarning() {
        val rawVal = parseMoney(etNewEarnValue?.text.toString())
        if (rawVal <= 0) return
        val type = spNewEarnType?.selectedItem.toString()
        earningItems.add(HistoryItem(type, type, rawVal))
        etNewEarnValue?.setText("")
        renderEarnings()
        recalcTotal()
    }
    
    private fun addExpense() {
        val rawVal = parseMoney(etNewExpValue?.text.toString())
        if (rawVal <= 0) return
        val type = spNewExpType?.selectedItem.toString()
        expenseItems.add(HistoryItem(type, type, rawVal))
        etNewExpValue?.setText("")
        renderExpenses()
    }
    
    private fun renderEarnings() {
        containerEarnings?.removeAllViews()
        earningItems.forEachIndexed { index, item ->
            val view = LayoutInflater.from(this).inflate(R.layout.item_dynamic_row, containerEarnings, false)
            view.findViewById<TextView>(R.id.tvLabel).text = item.name
            view.findViewById<TextView>(R.id.tvValue).text = formatMoney(item.value)
            view.findViewById<TextView>(R.id.tvValue).setTextColor(android.graphics.Color.parseColor("#10B981"))
            view.findViewById<View>(R.id.btnDelete).setOnClickListener {
                earningItems.removeAt(index)
                renderEarnings()
                recalcTotal()
            }
            containerEarnings?.addView(view)
        }
    }
    
    private fun renderExpenses() {
        containerExpenses?.removeAllViews()
        expenseItems.forEachIndexed { index, item ->
            val view = LayoutInflater.from(this).inflate(R.layout.item_dynamic_row, containerExpenses, false)
            view.findViewById<TextView>(R.id.tvLabel).text = item.name
            view.findViewById<TextView>(R.id.tvValue).text = formatMoney(item.value)
            view.findViewById<TextView>(R.id.tvValue).setTextColor(android.graphics.Color.parseColor("#EF4444"))
            view.findViewById<View>(R.id.btnDelete).setOnClickListener {
                expenseItems.removeAt(index)
                renderExpenses()
            }
            containerExpenses?.addView(view)
        }
    }

    private fun recalcTotal() {
        var sum = 0.0
        earningItems.forEach { sum += it.value }
        if (sum > 0) etTotal?.setText(formatMoney(sum))
    }

    private fun saveEntry() {
        try {
            val total = parseMoney(etTotal?.text.toString())
            if (total <= 0) {
                Toast.makeText(this, "Informe o Faturamento", Toast.LENGTH_SHORT).show()
                return
            }
            var u = 0.0; var n = 0.0; var p = 0.0; var o = 0.0
            earningItems.forEach { when(it.type) { "Uber"->u+=it.value; "99"->n+=it.value; "Part"->p+=it.value; else->o+=it.value } }
            var totalExp = 0.0
            expenseItems.forEach { totalExp += it.value }

            val sdf = SimpleDateFormat("dd/MM/yyyy", localeBR)
            val entry = DailyEntry(
                id = UUID.randomUUID().toString(),
                timestamp = calendar.timeInMillis,
                dateString = sdf.format(calendar.time),
                totalAmount = total,
                uber = u, pop = n, part = p, others = o,
                km = etKm?.text.toString().toDoubleOrNull() ?: 0.0,
                hours = etHoras?.text.toString().toDoubleOrNull() ?: 0.0,
                expenses = totalExp,
                runs = (qtdUber?.text.toString().toIntOrNull()?:0) + (qtd99?.text.toString().toIntOrNull()?:0)
            )

            val repo = DailyRepository(this)
            repo.save(entry)
            Toast.makeText(this, "✅ Salvo!", Toast.LENGTH_LONG).show()
            finish()
        } catch(e: Exception) {
            Toast.makeText(this, "Erro: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun parseMoney(text: String): Double {
        return try {
            val clean = text.replace("[^0-9]".toRegex(), "")
            if (clean.isEmpty()) 0.0 else clean.toDouble() / 100.0
        } catch(e: Exception) { 0.0 }
    }
    
    private fun formatMoney(valD: Double): String {
        return NumberFormat.getCurrencyInstance(localeBR).format(valD)
    }

    inner class CurrencyTextWatcher(private val editText: EditText) : TextWatcher {
        private var current = ""
        override fun onTextChanged(s: CharSequence, start: Int, before: Int, count: Int) {
            if (s.toString() != current) {
                editText.removeTextChangedListener(this)
                val clean = s.toString().replace("[^0-9]".toRegex(), "")
                val parsed = if (clean.isEmpty()) 0.0 else clean.toDouble() / 100
                val formatted = NumberFormat.getCurrencyInstance(localeBR).format(parsed)
                current = formatted
                editText.setText(formatted)
                editText.setSelection(formatted.length)
                editText.addTextChangedListener(this)
            }
        }
        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
        override fun afterTextChanged(s: Editable?) {}
    }
}
"""
    write_file("app/src/main/java/com/motoristapro/android/AddDailyActivity.kt", kt_code)

    # Incrementa versão
    os.system("python3 auto_version.py")
    print("🚀 Sincronização Completa! Pode compilar.")

if __name__ == "__main__":
    main()


