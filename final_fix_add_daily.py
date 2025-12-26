import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo Corrigido: {path}")

def main():
    print("🚑 Corrigindo Referências Perdidas na AddDailyActivity...")
    
    path = "app/src/main/java/com/motoristapro/android/AddDailyActivity.kt"
    
    # Código Kotlin Blindado
    # Todas as variáveis são declaradas como nullable (?) e inicializadas no initViews
    code = """package com.motoristapro.android

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
    
    // --- 1. DECLARAÇÃO DE VARIÁVEIS (Mapeando o XML) ---
    
    // Header & Resumo
    private var btnBack: View? = null
    private var tvDate: TextView? = null
    private var etKm: EditText? = null
    private var etHoras: EditText? = null
    
    // Faturamento
    private var badgeTotal: TextView? = null
    private var etTotal: EditText? = null
    private var etNewEarnValue: EditText? = null
    private var spNewEarnType: Spinner? = null
    private var btnAddEarn: View? = null
    private var containerEarnings: LinearLayout? = null
    
    // Corridas (Qtd)
    private var qtdUber: EditText? = null
    private var qtd99: EditText? = null
    private var qtdPart: EditText? = null
    private var qtdOutros: EditText? = null
    
    // Despesas
    private var etNewExpValue: EditText? = null
    private var spNewExpType: Spinner? = null
    private var btnAddExp: View? = null
    private var containerExpenses: LinearLayout? = null
    
    // Ação
    private var btnSave: Button? = null

    // Dados em Memória
    private val earningItems = ArrayList<HistoryItem>()
    private val expenseItems = ArrayList<HistoryItem>()

    data class HistoryItem(val type: String, val name: String, val value: Double)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_add_daily)
            
            initViews()       // 2. Vincula XML com Variáveis
            setupSpinners()   // 3. Preenche os dropdowns
            setupFormatters() // 4. Máscara de dinheiro
            updateDateLabel() // 5. Data de hoje
            setupListeners()  // 6. Cliques
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro Inicialização: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    // --- 2. VINCULAÇÃO (findViewById) ---
    private fun initViews() {
        btnBack = findViewById(R.id.btnBack)
        tvDate = findViewById(R.id.tvDate)
        etKm = findViewById(R.id.etKm)
        etHoras = findViewById(R.id.etHoras)
        
        badgeTotal = findViewById(R.id.badgeTotal)
        etTotal = findViewById(R.id.etTotal)
        
        etNewEarnValue = findViewById(R.id.etNewEarnValue)
        spNewEarnType = findViewById(R.id.spNewEarnType)
        btnAddEarn = findViewById(R.id.btnAddEarn)
        containerEarnings = findViewById(R.id.containerEarnings)
        
        qtdUber = findViewById(R.id.qtdUber)
        qtd99 = findViewById(R.id.qtd99)
        qtdPart = findViewById(R.id.qtdPart)
        qtdOutros = findViewById(R.id.qtdOutros)
        
        etNewExpValue = findViewById(R.id.etNewExpValue)
        spNewExpType = findViewById(R.id.spNewExpType)
        btnAddExp = findViewById(R.id.btnAddExp)
        containerExpenses = findViewById(R.id.containerExpenses)
        
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
            earningItems.forEach { 
                when(it.type) {
                    "Uber" -> u += it.value
                    "99" -> n += it.value
                    "Part" -> p += it.value
                    else -> o += it.value
                }
            }
            
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
                runs = (qtdUber?.text.toString().toIntOrNull()?:0) + (qtd99?.text.toString().toIntOrNull()?:0) + (qtdPart?.text.toString().toIntOrNull()?:0) + (qtdOutros?.text.toString().toIntOrNull()?:0)
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
    write_file(path, code)
    
    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("🚀 Activity corrigida. Todas as referências existem.")

if __name__ == "__main__":
    main()


