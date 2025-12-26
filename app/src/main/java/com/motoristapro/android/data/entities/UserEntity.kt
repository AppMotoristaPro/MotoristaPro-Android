package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int, // ID vindo do Servidor (Postgres)
    val nome: String,
    val email: String,
    val planType: String, // 'basic' ou 'premium'
    val validade: Long?,  // Timestamp da expiração
    val token: String?,   // Token de Sessão (JWT)
    val lastSync: Long = 0 // Última sincronização
)
