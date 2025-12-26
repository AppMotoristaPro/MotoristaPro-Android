package com.motoristapro.android.data

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
