package com.motoristapro.android

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
