package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "diarios")
data class DiarioEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null, // Nulo se ainda não subiu pra nuvem
    val data: Long, // Data do trabalho
    
    // Ganhos
    val ganhoBruto: Double = 0.0,
    val ganhoUber: Double = 0.0,
    val ganho99: Double = 0.0,
    val ganhoPart: Double = 0.0,
    val ganhoOutros: Double = 0.0,
    
    // Despesas Variáveis
    val despCombustivel: Double = 0.0,
    val despAlimentacao: Double = 0.0,
    val despManutencao: Double = 0.0,
    
    // Operacional
    val kmPercorrido: Double = 0.0,
    val horasTrabalhadas: Double = 0.0,
    val qtdCorridas: Int = 0,
    
    // Controle de Sincronia
    val isSynced: Boolean = false,
    val isDeleted: Boolean = false
)
