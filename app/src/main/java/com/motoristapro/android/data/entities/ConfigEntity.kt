package com.motoristapro.android.data.entities
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "configs")
data class ConfigEntity(
    @PrimaryKey val chave: String,
    val valor: String,
    val isSynced: Boolean = false
)
