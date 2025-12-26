package com.motoristapro.android.data

import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.File

class DailyRepository(private val context: Context) {
    
    private val fileName = "motorista_diary.json"
    private val gson = Gson()

    fun save(entry: DailyEntry) {
        val list = getAll().toMutableList()
        // Remove se já existir com mesmo ID (edição)
        list.removeAll { it.id == entry.id }
        list.add(entry)
        saveList(list)
    }

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

    private fun saveList(list: List<DailyEntry>) {
        val json = gson.toJson(list)
        val file = File(context.filesDir, fileName)
        file.writeText(json)
    }
    
    fun getMonthSummary(): DashboardSummary {
        val all = getAll()
        var total = 0.0
        var km = 0.0
        var runs = 0
        
        // Soma tudo (futuramente podemos filtrar por mês)
        for (item in all) {
            total += item.totalAmount
            km += item.km
            runs += item.runs
        }
        
        return DashboardSummary(total, km, runs, if (all.isNotEmpty()) all[0] else null)
    }
}
