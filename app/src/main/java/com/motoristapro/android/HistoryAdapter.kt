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
