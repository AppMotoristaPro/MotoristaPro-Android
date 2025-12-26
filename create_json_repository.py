import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Criado: {path}")

def main():
    print("💾 Criando Sistema de Arquivos JSON...")
    
    base_pkg = "app/src/main/java/com/motoristapro/android/data"
    
    # 1. MODELO DE DADOS (Simples Data Class)
    model_kt = """package com.motoristapro.android.data

data class DailyEntry(
    val id: String, // UUID único
    val timestamp: Long,
    val dateString: String, // "dd/MM/yyyy" para facilitar
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
"""
    write_file(f"{base_pkg}/DailyEntry.kt", model_kt)

    # 2. REPOSITÓRIO (Gerenciador do Arquivo)
    repo_kt = """package com.motoristapro.android.data

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
"""
    write_file(f"{base_pkg}/DailyRepository.kt", repo_kt)

    print("🎉 Sistema de Dados JSON criado!")

if __name__ == "__main__":
    main()


