package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "agendamentos")
data class AgendamentoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    
    val cliente: String,
    val dataHora: Long,
    val origem: String,
    val destino: String,
    val valor: Double,
    val observacao: String? = null,
    val status: String = "pendente", // pendente, concluido
    
    val isSynced: Boolean = false
)
