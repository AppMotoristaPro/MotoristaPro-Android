package com.motoristapro.android.data.entities
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int,
    val nome: String,
    val email: String,
    val planType: String,
    val validade: Long?,
    val token: String?,
    val lastSync: Long = 0
)
