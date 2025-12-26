import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo Blindado: {path}")

def main():
    print("🚑 Blindando AddDailyActivity para mostrar o erro na tela...")
    
    path = "app/src/main/java/com/motoristapro/android/AddDailyActivity.kt"
    
    # Código Seguro com Tratamento de Erros
    code = """package com.motoristapro.android

import android.app.DatePickerDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.motoristapro.android.data.DailyEntry
import com.motoristapro.android.data.DailyRepository
import java.text.SimpleDateFormat
import java.util.*

class AddDailyActivity : AppCompatActivity() {

    private val calendar = Calendar.getInstance()
    
    // Variáveis Nullable para evitar Crash de inicialização
    private var tvDate: TextView? = null
    private var etTotal: EditText? = null
    
    private var etUber: EditText? = null
    private var et99: EditText? = null
    private var etPart: EditText? = null
    private var etOutros: EditText? = null
    private var etComb: EditText? = null
    private var etAlim: EditText? = null
    private var etManu: EditText? = null
    private var etKm: EditText? = null
    private var etHoras: EditText? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            setContentView(R.layout.activity_add_daily)

            initViews()
            setupDatePicker()
            setupAutoSum()
            
            // Botão Salvar Seguro
            findViewById<View>(R.id.btnSave)?.setOnClickListener { 
                try {
                    saveEntry()
                } catch(e: Exception) {
                    showError("Erro ao salvar: " + e.message)
                }
            }
            
        } catch (e: Exception) {
            // MOSTRA O ERRO NA TELA (EM VEZ DE FECHAR)
            showErrorFatal(e)
        }
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
        tvDate?.setOnClickListener {
            try {
                DatePickerDialog(this, { _, year, month, day ->
                    calendar.set(year, month, day)
                    updateDateLabel()
                }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show()
            } catch(e: Exception) { showError("Erro DatePicker: " + e.message) }
        }
    }

    private fun updateDateLabel() {
        try {
            val fmt = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
            tvDate?.text = fmt.format(calendar.time)
        } catch(e: Exception) {}
    }

    private fun setupAutoSum() {
        val watcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { calculateTotal() }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        }
        
        // Adiciona listener apenas se o campo existir
        etUber?.addTextChangedListener(watcher)
        et99?.addTextChangedListener(watcher)
        etPart?.addTextChangedListener(watcher)
        etOutros?.addTextChangedListener(watcher)
    }

    private fun calculateTotal() {
        try {
            val u = etUber?.text.toString().toDoubleOrNull() ?: 0.0
            val n = et99?.text.toString().toDoubleOrNull() ?: 0.0
            val p = etPart?.text.toString().toDoubleOrNull() ?: 0.0
            val o = etOutros?.text.toString().toDoubleOrNull() ?: 0.0
            val sum = u + n + p + o
            if (sum > 0) etTotal?.setText(String.format(Locale.US, "%.2f", sum))
        } catch(e: Exception) {}
    }

    private fun saveEntry() {
        val total = etTotal?.text.toString().toDoubleOrNull()
        if (total == null || total <= 0) {
            Toast.makeText(this, "Informe o Faturamento", Toast.LENGTH_SHORT).show()
            return
        }

        val sdf = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
        val comb = etComb?.text.toString().toDoubleOrNull() ?: 0.0
        val alim = etAlim?.text.toString().toDoubleOrNull() ?: 0.0
        val manu = etManu?.text.toString().toDoubleOrNull() ?: 0.0
        
        val entry = DailyEntry(
            id = UUID.randomUUID().toString(),
            timestamp = calendar.timeInMillis,
            dateString = sdf.format(calendar.time),
            totalAmount = total,
            uber = etUber?.text.toString().toDoubleOrNull() ?: 0.0,
            pop = et99?.text.toString().toDoubleOrNull() ?: 0.0,
            part = etPart?.text.toString().toDoubleOrNull() ?: 0.0,
            others = etOutros?.text.toString().toDoubleOrNull() ?: 0.0,
            km = etKm?.text.toString().toDoubleOrNull() ?: 0.0,
            hours = etHoras?.text.toString().toDoubleOrNull() ?: 0.0,
            expenses = comb + alim + manu,
            runs = 0 
        )

        val repo = DailyRepository(this)
        repo.save(entry)
        Toast.makeText(this, "✅ Salvo com sucesso!", Toast.LENGTH_LONG).show()
        finish()
    }
    
    private fun showError(msg: String) {
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show()
    }
    
    private fun showErrorFatal(e: Exception) {
        val scroll = ScrollView(this)
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.setPadding(40, 40, 40, 40)
        layout.setBackgroundColor(android.graphics.Color.WHITE)
        
        val title = TextView(this)
        title.text = "ERRO FATAL (NOVO LANÇAMENTO)"
        title.textSize = 18f
        title.setTextColor(android.graphics.Color.RED)
        title.setPadding(0, 0, 0, 20)
        
        val msg = TextView(this)
        msg.text = e.toString() + "\\n\\n" + e.stackTraceToString()
        msg.setTextColor(android.graphics.Color.BLACK)
        
        layout.addView(title)
        layout.addView(msg)
        scroll.addView(layout)
        setContentView(scroll)
    }
}
"""
    write_file(path, code)
    
    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("🚀 Activity de Lançamento Protegida. Compile agora.")

if __name__ == "__main__":
    main()


