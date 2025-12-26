package com.motoristapro.android

import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.media.projection.MediaProjectionManager
import android.view.View
import android.widget.TextView
import android.widget.Button
import android.widget.ProgressBar
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.motoristapro.android.data.DailyRepository
import com.motoristapro.android.data.DailyEntry
import java.text.NumberFormat
import java.util.Locale
import java.util.Calendar
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.charts.PieChart
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.github.mikephil.charting.data.PieData
import com.github.mikephil.charting.data.PieDataSet
import com.github.mikephil.charting.data.PieEntry

class MainActivity : AppCompatActivity() {

    // Views
    private var tvTotalGanho: TextView? = null
    private var tvTotalCorridas: TextView? = null
    private var tvTotalKm: TextView? = null
    private var tvTotalDespesas: TextView? = null
    private var tvLucroLiq: TextView? = null
    private var tvLabelTotal: TextView? = null
    private var tvGreeting: TextView? = null
    
    private var filterDay: TextView? = null
    private var filterWeek: TextView? = null
    private var filterMonth: TextView? = null
    
    private var chartLine: LineChart? = null
    private var chartPie: PieChart? = null
    private var progressMeta: ProgressBar? = null
    private var tvMetaPct: TextView? = null
    
    private var currentFilter = "MONTH" // DAY, WEEK, MONTH
    
    private val REQUEST_OVERLAY = 101
    private val REQUEST_MEDIA_PROJECTION = 102

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_main)
            initViews()
            setupButtons()
            setupFilters()
            setupChartsConfig()
            
            updateGreeting()
            loadData()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI: " + e.message, Toast.LENGTH_LONG).show()
        }
    }
    
    override fun onResume() {
        super.onResume()
        loadData()
    }

    private fun initViews() {
        tvTotalGanho = findViewById(R.id.tvTotalGanho)
        tvTotalCorridas = findViewById(R.id.tvTotalCorridas)
        tvTotalKm = findViewById(R.id.tvTotalKm)
        tvTotalDespesas = findViewById(R.id.tvTotalDespesas)
        tvLucroLiq = findViewById(R.id.tvLucroLiq)
        tvLabelTotal = findViewById(R.id.tvLabelTotal)
        tvGreeting = findViewById(R.id.tvGreeting)
        
        filterDay = findViewById(R.id.filterDay)
        filterWeek = findViewById(R.id.filterWeek)
        filterMonth = findViewById(R.id.filterMonth)
        
        chartLine = findViewById(R.id.chartLine)
        chartPie = findViewById(R.id.chartPie)
        progressMeta = findViewById(R.id.progressMeta)
        tvMetaPct = findViewById(R.id.tvMetaPct)
    }

    private fun setupButtons() {
        findViewById<View>(R.id.btnLancar)?.setOnClickListener {
            startActivity(Intent(this, AddDailyActivity::class.java))
        }
        findViewById<View>(R.id.btnRobo)?.setOnClickListener {
            checkPermissionsAndStart()
        }
        findViewById<View>(R.id.btnHistorico)?.setOnClickListener {
            startActivity(Intent(this, HistoryActivity::class.java))
        }
    }
    
    private fun setupFilters() {
        filterDay?.setOnClickListener { setFilter("DAY") }
        filterWeek?.setOnClickListener { setFilter("WEEK") }
        filterMonth?.setOnClickListener { setFilter("MONTH") }
    }
    
    private fun setFilter(type: String) {
        currentFilter = type
        // Reset Visual
        val activeBg = ContextCompat.getDrawable(this, R.drawable.bg_glass_card)
        val inactiveBg = null
        val activeColor = ContextCompat.getColor(this, R.color.primary)
        val inactiveColor = ContextCompat.getColor(this, R.color.text_secondary)
        
        filterDay?.background = if(type=="DAY") activeBg else inactiveBg
        filterDay?.setTextColor(if(type=="DAY") activeColor else inactiveColor)
        
        filterWeek?.background = if(type=="WEEK") activeBg else inactiveBg
        filterWeek?.setTextColor(if(type=="WEEK") activeColor else inactiveColor)
        
        filterMonth?.background = if(type=="MONTH") activeBg else inactiveBg
        filterMonth?.setTextColor(if(type=="MONTH") activeColor else inactiveColor)
        
        // Labels
        tvLabelTotal?.text = when(type) {
            "DAY" -> "FATURAMENTO HOJE"
            "WEEK" -> "FATURAMENTO SEMANAL"
            else -> "FATURAMENTO MENSAL"
        }
        
        loadData()
    }
    
    private fun updateGreeting() {
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        val msg = when (hour) {
            in 5..11 -> "Bom dia"
            in 12..18 -> "Boa tarde"
            else -> "Boa noite"
        }
        tvGreeting?.text = "$msg, Motorista"
    }
    
    private fun setupChartsConfig() {
        // Line Chart (Faturamento)
        chartLine?.apply {
            description.isEnabled = false
            setDrawGridBackground(false)
            xAxis.setDrawGridLines(false)
            xAxis.setDrawLabels(false)
            axisLeft.setDrawGridLines(false)
            axisLeft.textColor = Color.WHITE
            axisRight.isEnabled = false
            legend.isEnabled = false
            setTouchEnabled(false)
        }
        
        // Pie Chart (Despesas)
        chartPie?.apply {
            description.isEnabled = false
            legend.isEnabled = false
            setHoleColor(Color.TRANSPARENT)
            setUsePercentValues(false)
            setTouchEnabled(false)
        }
    }

    private fun loadData() {
        try {
            val repo = DailyRepository(this)
            val allData = repo.getAll() // Já vem ordenado por data desc
            
            // Filtra os dados
            val filteredData = filterData(allData)
            
            // Soma Totais
            var totalGanho = 0.0
            var totalKm = 0.0
            var totalCorridas = 0
            var totalDespesas = 0.0
            
            // Dados para o Gráfico de Linha
            val lineEntries = ArrayList<Entry>()
            
            // Itera reverso para o gráfico ficar cronológico (Esq -> Dir)
            filteredData.reversed().forEachIndexed { index, item ->
                totalGanho += item.totalAmount
                totalKm += item.km
                totalCorridas += item.runs
                totalDespesas += item.expenses
                
                lineEntries.add(Entry(index.toFloat(), item.totalAmount.toFloat()))
            }
            
            // Atualiza Textos
            val ptBr = Locale("pt", "BR")
            tvTotalGanho?.text = NumberFormat.getCurrencyInstance(ptBr).format(totalGanho)
            tvTotalKm?.text = String.format(Locale.US, "%.0f km", totalKm)
            tvTotalCorridas?.text = totalCorridas.toString()
            tvTotalDespesas?.text = NumberFormat.getCurrencyInstance(ptBr).format(totalDespesas)
            
            val lucroLiq = totalGanho - totalDespesas
            tvLucroLiq?.text = NumberFormat.getCurrencyInstance(ptBr).format(lucroLiq)

            // Atualiza Gráfico de Linha
            if (lineEntries.isNotEmpty()) {
                val dataSet = LineDataSet(lineEntries, "Ganhos")
                dataSet.color = Color.WHITE
                dataSet.lineWidth = 2f
                dataSet.setDrawCircles(false)
                dataSet.setDrawValues(false)
                dataSet.mode = LineDataSet.Mode.CUBIC_BEZIER
                chartLine?.data = LineData(dataSet)
                chartLine?.invalidate()
            } else {
                chartLine?.clear()
            }
            
            // Atualiza Gráfico de Pizza (Combustível vs Outros)
            // Simplificado: Despesa vs Lucro para dar visual
            val pieEntries = ArrayList<PieEntry>()
            if (totalGanho > 0) {
                pieEntries.add(PieEntry(totalDespesas.toFloat(), ""))
                pieEntries.add(PieEntry(lucroLiq.toFloat(), ""))
                
                val pieDataSet = PieDataSet(pieEntries, "")
                pieDataSet.colors = listOf(Color.parseColor("#EF4444"), Color.parseColor("#10B981")) // Vermelho Desp, Verde Lucro
                pieDataSet.setDrawValues(false)
                chartPie?.data = PieData(pieDataSet)
                chartPie?.invalidate()
            } else {
                chartPie?.clear()
            }
            
            // Meta (Simulada R$ 1000 por enquanto, depois virá da config)
            val meta = 1000.0
            val pct = ((totalGanho / meta) * 100).toInt()
            progressMeta?.progress = pct.coerceIn(0, 100)
            tvMetaPct?.text = "$pct% da Meta Semanal"

        } catch (e: Exception) {
            tvTotalGanho?.text = "R$ 0,00"
        }
    }
    
    private fun filterData(all: List<DailyEntry>): List<DailyEntry> {
        val cal = Calendar.getInstance()
        val today = cal.get(Calendar.DAY_OF_YEAR)
        val month = cal.get(Calendar.MONTH)
        
        return when(currentFilter) {
            "DAY" -> all.filter { 
                // Conversão simples de timestamp pra dia do ano
                cal.timeInMillis = it.timestamp
                cal.get(Calendar.DAY_OF_YEAR) == today
            }
            "WEEK" -> all.take(7) // Simplificação: Últimos 7 lançamentos
            else -> all.filter {
                cal.timeInMillis = it.timestamp
                cal.get(Calendar.MONTH) == month
            }
        }
    }

    // Permissões e OCR (Mantido igual)
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
                moveTaskToBack(true)
            }
        }
    }
}
