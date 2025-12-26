package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "custos_fixos")
data class CustoFixoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    
    val nome: String,
    val valor: Double,
    val tipo: String = "mensal", // mensal, anual, semanal
    
    val isSynced: Boolean = false
)
