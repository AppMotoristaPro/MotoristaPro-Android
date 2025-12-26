package com.motoristapro.android

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
    
    // UI - Views
    private var tvDate: TextView? = null
    private var etTotal: EditText? = null
    private var badgeTotal: TextView? = null
    
    private var etNewEarnValue: EditText? = null
    private var spNewEarnType: Spinner? = null
    private var containerEarnings: LinearLayout? = null
    
    private var etNewExpValue: EditText? = null
    private var spNewExpType: Spinner? = null
    private var containerExpenses: LinearLayout? = null
    
    // Contadores
    private var qtdUber: EditText? = null
    private var qtd99: EditText? = null
    private var qtdPart: EditText? = null
    private var qtdOutros: EditText? = null
    private var etKm: EditText? = null
    private var etHoras: EditText? = null

    // Dados em Memória
    private val earningItems = ArrayList<HistoryItem>()
    private val expenseItems = ArrayList<HistoryItem>()

    data class HistoryItem(val type: String, val name: String, val value: Double)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_add_daily)
            initViews()
            setupSpinners()
            setupFormatters()
            updateDateLabel()
            
            findViewById<View>(R.id.btnBack)?.setOnClickListener { finish() }
            
            findViewById<View>(R.id.tvDate)?.setOnClickListener {
                DatePickerDialog(this, { _, y, m, d ->
                    calendar.set(y, m, d)
                    updateDateLabel()
                }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show()
            }
            
            findViewById<View>(R.id.btnAddEarn)?.setOnClickListener { addEarning() }
            findViewById<View>(R.id.btnAddExp)?.setOnClickListener { addExpense() }
            
            findViewById<Button>(R.id.btnSave)?.setOnClickListener { saveEntry() }
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun initViews() {
        tvDate = findViewById(R.id.tvDate)
        etTotal = findViewById(R.id.etTotal)
        badgeTotal = findViewById(R.id.badgeTotal)
        
        etNewEarnValue = findViewById(R.id.etNewEarnValue)
        spNewEarnType = findViewById(R.id.spNewEarnType)
        containerEarnings = findViewById(R.id.containerEarnings)
        
        etNewExpValue = findViewById(R.id.etNewExpValue)
        spNewExpType = findViewById(R.id.spNewExpType)
        containerExpenses = findViewById(R.id.containerExpenses)
        
        qtdUber = findViewById(R.id.qtdUber)
        qtd99 = findViewById(R.id.qtd99)
        qtdPart = findViewById(R.id.qtdPart)
        qtdOutros = findViewById(R.id.qtdOutros)
        etKm = findViewById(R.id.etKm)
        etHoras = findViewById(R.id.etHoras)
    }

    private fun setupSpinners() {
        val earnTypes = listOf("Uber", "99", "Part", "Outros")
        spNewEarnType?.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, earnTypes)
        
        val expTypes = listOf("Combustível", "Alimentação", "Manutenção")
        spNewExpType?.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, expTypes)
    }

    private fun setupFormatters() {
        // Aplica mascara R$ para inputs
        etTotal?.addTextChangedListener(CurrencyTextWatcher(etTotal!!))
        etNewEarnValue?.addTextChangedListener(CurrencyTextWatcher(etNewEarnValue!!))
        etNewExpValue?.addTextChangedListener(CurrencyTextWatcher(etNewExpValue!!))
        
        // Atualiza badge quando total muda
        etTotal?.addTextChangedListener(object: TextWatcher {
            override fun afterTextChanged(s: Editable?) { 
                badgeTotal?.text = s.toString() 
            }
            override fun beforeTextChanged(s: CharSequence?, st: Int, c: Int, a: Int) {}
            override fun onTextChanged(s: CharSequence?, st: Int, b: Int, c: Int) {}
        })
    }

    private fun updateDateLabel() {
        val fmt = SimpleDateFormat("dd/MM/yyyy", localeBR)
        tvDate?.text = fmt.format(calendar.time)
    }

    // --- LÓGICA DE LISTAS DINÂMICAS ---
    
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
        if (sum > 0) {
            etTotal?.setText(formatMoney(sum)) // A máscara vai limpar o "R$" depois
        }
    }

    // --- SALVAR ---
    private fun saveEntry() {
        try {
            val total = parseMoney(etTotal?.text.toString())
            if (total <= 0) {
                Toast.makeText(this, "Informe o Faturamento Total", Toast.LENGTH_SHORT).show()
                return
            }
            
            // Agrupar ganhos por tipo
            var u = 0.0; var n = 0.0; var p = 0.0; var o = 0.0
            earningItems.forEach { 
                when(it.type) {
                    "Uber" -> u += it.value
                    "99" -> n += it.value
                    "Part" -> p += it.value
                    else -> o += it.value
                }
            }
            
            // Agrupar despesas (simplificado: soma tudo)
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

    // --- UTILITÁRIOS ---
    private fun parseMoney(text: String): Double {
        return try {
            // Remove R$, espaços e converte vírgula para ponto
            val clean = text.replace("[^0-9]".toRegex(), "")
            clean.toDouble() / 100.0
        } catch(e: Exception) { 0.0 }
    }
    
    private fun formatMoney(valD: Double): String {
        return NumberFormat.getCurrencyInstance(localeBR).format(valD)
    }

    // MÁSCARA DINHEIRO
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
