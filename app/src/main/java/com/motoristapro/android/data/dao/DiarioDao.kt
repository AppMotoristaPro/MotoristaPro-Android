package com.motoristapro.android.data.dao
import androidx.room.*
import com.motoristapro.android.data.entities.DiarioEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DiarioDao {
    @Query("SELECT * FROM diarios WHERE isDeleted = 0 ORDER BY data DESC")
    fun getAllHistorico(): Flow<List<DiarioEntity>>

    @Query("SELECT * FROM diarios WHERE isDeleted = 0 AND data BETWEEN :inicio AND :fim")
    suspend fun getPeriodo(inicio: Long, fim: Long): List<DiarioEntity>

    @Query("SELECT SUM(kmPercorrido) FROM diarios WHERE isDeleted = 0")
    suspend fun getTotalKmRodado(): Double?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(diario: DiarioEntity): Long

    @Update
    suspend fun update(diario: DiarioEntity)

    @Query("UPDATE diarios SET isDeleted = 1, isSynced = 0 WHERE localId = :id")
    suspend fun softDelete(id: Long)
    
    @Query("SELECT * FROM diarios WHERE isSynced = 0")
    suspend fun getUnsynced(): List<DiarioEntity>
}
