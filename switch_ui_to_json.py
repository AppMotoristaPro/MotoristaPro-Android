import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ UI Atualizada: {path}")

def main():
    print("🔄 Conectando Telas ao JSON...")

    base_java = "app/src/main/java/com/motoristapro/android"

    # 1. ADD ACTIVITY (Salvar no JSON)
    add_kt = """package com.motoristapro.android

import android.app.DatePickerDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.motoristapro.android.data.DailyEntry
import com.motoristapro.android.data.DailyRepository
import java.text.SimpleDateFormat
import java.util.*
import java.util.UUID

class AddDailyActivity : AppCompatActivity() {

    private val calendar = Calendar.getInstance()
    private lateinit var tvDate: TextView
    private lateinit var etTotal: EditText
    
    // Inputs
    private lateinit var etUber: EditText
    private lateinit var et99: EditText
    private lateinit var etPart: EditText
    private lateinit var etOutros: EditText
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
            Toast.makeText(this, "Informe o Faturamento", Toast.LENGTH_SHORT).show()
            return
        }

        val sdf = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
        
        val entry = DailyEntry(
            id = UUID.randomUUID().toString(),
            timestamp = calendar.timeInMillis,
            dateString = sdf.format(calendar.time),
            totalAmount = total,
            uber = etUber.text.toString().toDoubleOrNull() ?: 0.0,
            pop = et99.text.toString().toDoubleOrNull() ?: 0.0,
            part = etPart.text.toString().toDoubleOrNull() ?: 0.0,
            others = etOutros.text.toString().toDoubleOrNull() ?: 0.0,
            km = etKm.text.toString().toDoubleOrNull() ?: 0.0,
            hours = etHoras.text.toString().toDoubleOrNull() ?: 0.0,
            expenses = 0.0, // Simplificado por enquanto
            runs = 0 // Simplificado
        )

        try {
            val repo = DailyRepository(this)
            repo.save(entry)
            Toast.makeText(this, "✅ Salvo com sucesso!", Toast.LENGTH_LONG).show()
            finish()
        } catch (e: Exception) {
            Toast.makeText(this, "Erro: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
}
"""
    write_file(f"{base_java}/AddDailyActivity.kt", add_kt)

    # 2. MAIN ACTIVITY (Ler do JSON)
    main_kt = """package com.motoristapro.android

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.media.projection.MediaProjectionManager
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import com.motoristapro.android.data.DailyRepository
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
            setContentView(R.layout.activity_main)

            tvTotalGanho = findViewById(R.id.tvTotalGanho)
            tvTotalCorridas = findViewById(R.id.tvTotalCorridas)
            tvTotalKm = findViewById(R.id.tvTotalKm)
            tvEmptyHistory = findViewById(R.id.tvEmptyHistory)

            findViewById<CardView>(R.id.btnLancar)?.setOnClickListener {
                startActivity(Intent(this, AddDailyActivity::class.java))
            }

            findViewById<CardView>(R.id.btnRobo)?.setOnClickListener {
                checkPermissionsAndStart()
            }

        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    override fun onResume() {
        super.onResume()
        refreshDashboard()
    }

    private fun refreshDashboard() {
        try {
            val repo = DailyRepository(this)
            val summary = repo.getMonthSummary()

            val ptBr = Locale("pt", "BR")
            tvTotalGanho.text = NumberFormat.getCurrencyInstance(ptBr).format(summary.totalEarnings)
            tvTotalKm.text = String.format("%.0f km", summary.totalKm)
            tvTotalCorridas.text = summary.totalRuns.toString()
            
            if (summary.lastEntry != null) {
                tvEmptyHistory.text = "Último: R$ ${summary.lastEntry.totalAmount} em ${summary.lastEntry.dateString}"
            } else {
                tvEmptyHistory.text = "Nenhum lançamento."
            }

        } catch (e: Exception) {
            tvEmptyHistory.text = "Erro ao carregar dados."
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
                moveTaskToBack(true) // Minimiza o app
            }
        }
    }
}
"""
    write_file(f"{base_java}/MainActivity.kt", main_kt)
    
    # Atualiza versão
    os.system("python3 auto_version.py")
    
    print("🚀 Plano B (JSON) Integrado!")

if __name__ == "__main__":
    main()


