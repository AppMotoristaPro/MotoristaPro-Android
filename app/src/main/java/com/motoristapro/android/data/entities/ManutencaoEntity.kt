package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "manutencoes")
data class ManutencaoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    
    val item: String,      // Ex: Óleo
    val kmProxima: Double, // KM do odômetro alvo
    
    val isSynced: Boolean = false
)
