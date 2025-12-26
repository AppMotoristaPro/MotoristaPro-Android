import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Criado: {path}")

def main():
    print("💾 Criando Sistema de Arquivos JSON...")
    
    base_pkg = "app/src/main/java/com/motoristapro/android/data"
    
    # 1. MODELO DE DADOS
    model_kt = """package com.motoristapro.android.data

data class DailyEntry(
    val id: String, 
    val timestamp: Long,
    val dateString: String, 
    val totalAmount: Double,
    val uber: Double,
    val pop: Double,
    val part: Double,
    val others: Double,
    val km: Double,
    val hours: Double,
    val expenses: Double,
    val runs: Int
)

data class DashboardSummary(
    val totalEarnings: Double,
    val totalKm: Double,
    val totalRuns: Int,
    val lastEntry: DailyEntry?
)
"""
    write_file(f"{base_pkg}/Models.kt", model_kt)

    # 2. REPOSITÓRIO (Gerenciador do Arquivo)
    repo_kt = """package com.motoristapro.android.data

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
"""
    write_file(f"{base_pkg}/DailyRepository.kt", repo_kt)

    print("🎉 Sistema de Dados JSON criado!")

if __name__ == "__main__":
    main()


