package com.motoristapro.android.data

import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.File
import java.util.UUID

class DailyRepository(private val context: Context) {
    
    private val fileName = "motorista_diary.json"
    private val gson = Gson()

    // Salvar novo registro
    fun save(entry: DailyEntry) {
        val list = getAll().toMutableList()
        list.add(entry)
        saveList(list)
    }

    // Pegar todos (Ordenado por data decrescente)
    fun getAll(): List<DailyEntry> {
        val file = File(context.filesDir, fileName)
        if (!file.exists()) return emptyList()
        
        return try {
            val json = file.readText()
            val type = object : TypeToken<List<DailyEntry>>() {}.type
            val list: List<DailyEntry> = gson.fromJson(json, type)
            list.sortedByDescending { it.timestamp }
        } catch (e: Exception) {
            emptyList()
        }
    }

    // Salvar a lista completa no arquivo
    private fun saveList(list: List<DailyEntry>) {
        val json = gson.toJson(list)
        val file = File(context.filesDir, fileName)
        file.writeText(json)
    }
    
    // Calcular Resumo do Mês Atual
    fun getMonthSummary(): DashboardSummary {
        val all = getAll()
        var total = 0.0
        var km = 0.0
        var runs = 0
        
        // Aqui poderíamos filtrar por mês, mas vamos somar tudo por enquanto para testar
        for (item in all) {
            total += item.totalAmount
            km += item.km
            runs += item.runs
        }
        
        return DashboardSummary(total, km, runs, if (all.isNotEmpty()) all[0] else null)
    }
}

data class DashboardSummary(
    val totalEarnings: Double,
    val totalKm: Double,
    val totalRuns: Int,
    val lastEntry: DailyEntry?
)
