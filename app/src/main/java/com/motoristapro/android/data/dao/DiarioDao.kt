package com.motoristapro.android.data.dao

import androidx.room.*
import com.motoristapro.android.data.entities.DiarioEntity

@Dao
interface DiarioDao {
    @Query("SELECT * FROM diarios WHERE isDeleted = 0 ORDER BY data DESC")
    suspend fun getAllList(): List<DiarioEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(diario: DiarioEntity): Long
}
