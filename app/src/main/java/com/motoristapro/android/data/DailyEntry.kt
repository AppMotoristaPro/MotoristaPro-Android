package com.motoristapro.android.data

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
