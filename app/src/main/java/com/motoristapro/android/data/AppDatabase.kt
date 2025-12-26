package com.motoristapro.android.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.motoristapro.android.data.entities.*
import com.motoristapro.android.data.dao.*

@Database(
    entities = [
        UserEntity::class, 
        DiarioEntity::class, 
        ConfigEntity::class, 
        AgendamentoEntity::class, 
        ManutencaoEntity::class, 
        CustoFixoEntity::class
    ], 
    version = 1, 
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {

    abstract fun userDao(): UserDao
    abstract fun diarioDao(): DiarioDao
    abstract fun configDao(): ConfigDao
    abstract fun manutencaoDao(): ManutencaoDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "motorista_pro_native_db"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
