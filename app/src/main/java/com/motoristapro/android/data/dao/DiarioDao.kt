package com.motoristapro.android.data.dao

import androidx.room.*
import com.motoristapro.android.data.entities.DiarioEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DiarioDao {
    // Listar histórico (decrescente por data)
    @Query("SELECT * FROM diarios WHERE isDeleted = 0 ORDER BY data DESC")
    fun getAllHistorico(): Flow<List<DiarioEntity>>

    // Filtrar por período (Dashboard)
    @Query("SELECT * FROM diarios WHERE isDeleted = 0 AND data BETWEEN :inicio AND :fim")
    suspend fun getPeriodo(inicio: Long, fim: Long): List<DiarioEntity>

    // Somar KM Total (Para Manutenção)
    @Query("SELECT SUM(kmPercorrido) FROM diarios WHERE isDeleted = 0")
    suspend fun getTotalKmRodado(): Double?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(diario: DiarioEntity): Long

    @Update
    suspend fun update(diario: DiarioEntity)

    // Soft Delete (Marca como deletado para sincronizar depois)
    @Query("UPDATE diarios SET isDeleted = 1, isSynced = 0 WHERE localId = :id")
    suspend fun softDelete(id: Long)
    
    // Buscar não sincronizados
    @Query("SELECT * FROM diarios WHERE isSynced = 0")
    suspend fun getUnsynced(): List<DiarioEntity>
}
