package com.motoristapro.android.data.dao
import androidx.room.*
import com.motoristapro.android.data.entities.ManutencaoEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ManutencaoDao {
    @Query("SELECT * FROM manutencoes ORDER BY kmProxima ASC")
    fun getAll(): Flow<List<ManutencaoEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ManutencaoEntity)

    @Delete
    suspend fun delete(item: ManutencaoEntity)
}
