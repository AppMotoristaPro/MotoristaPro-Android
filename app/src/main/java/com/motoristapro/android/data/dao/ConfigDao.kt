package com.motoristapro.android.data.dao
import androidx.room.*
import com.motoristapro.android.data.entities.ConfigEntity

@Dao
interface ConfigDao {
    @Query("SELECT valor FROM configs WHERE chave = :key LIMIT 1")
    suspend fun getValue(key: String): String?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(config: ConfigEntity)
    
    @Query("SELECT * FROM configs")
    suspend fun getAll(): List<ConfigEntity>
}
