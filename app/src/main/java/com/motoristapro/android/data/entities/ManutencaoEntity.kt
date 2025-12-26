package com.motoristapro.android.data.entities
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "manutencoes")
data class ManutencaoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    val item: String,
    val kmProxima: Double,
    val isSynced: Boolean = false
)
