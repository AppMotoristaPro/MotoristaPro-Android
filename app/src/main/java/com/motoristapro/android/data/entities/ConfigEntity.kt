package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "configs")
data class ConfigEntity(
    @PrimaryKey val chave: String, // Ex: 'preco_combustivel', 'meta_semanal'
    val valor: String,
    val isSynced: Boolean = false
)
