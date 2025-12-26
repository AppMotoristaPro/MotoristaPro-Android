package com.motoristapro.android

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
                    finish()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@AddDailyActivity, "Erro ao guardar: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
