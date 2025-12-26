package com.motoristapro.android.data.entities
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "diarios")
data class DiarioEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    val data: Long,
    val ganhoBruto: Double = 0.0,
    val ganhoUber: Double = 0.0,
    val ganho99: Double = 0.0,
    val ganhoPart: Double = 0.0,
    val ganhoOutros: Double = 0.0,
    val despCombustivel: Double = 0.0,
    val despAlimentacao: Double = 0.0,
    val despManutencao: Double = 0.0,
    val kmPercorrido: Double = 0.0,
    val horasTrabalhadas: Double = 0.0,
    val qtdCorridas: Int = 0,
    val isSynced: Boolean = false,
    val isDeleted: Boolean = false
)
