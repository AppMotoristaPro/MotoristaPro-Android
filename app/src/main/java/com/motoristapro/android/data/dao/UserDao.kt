package com.motoristapro.android.data.dao

import androidx.room.*
import com.motoristapro.android.data.entities.UserEntity

@Dao
interface UserDao {
    @Query("SELECT * FROM users LIMIT 1")
    suspend fun getUser(): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Query("DELETE FROM users")
    suspend fun clear()
}
