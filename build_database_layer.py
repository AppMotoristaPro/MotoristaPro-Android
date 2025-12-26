import os

def write_file(path, content):
    # Garante que a pasta existe
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Criado: {path}")

def main():
    print("🏗️ Construindo Camada de Dados Nativa (Room Database)...")
    
    base_pkg = "app/src/main/java/com/motoristapro/android/data"
    
    # ==============================================================================
    # 1. TYPE CONVERTERS (Para lidar com Datas)
    # ==============================================================================
    converters_kt = """package com.motoristapro.android.data

import androidx.room.TypeConverter
import java.util.Date

class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }
}
"""
    write_file(f"{base_pkg}/Converters.kt", converters_kt)

    # ==============================================================================
    # 2. ENTIDADES (Tabelas do Banco)
    # ==============================================================================
    
    # 2.1 USUÁRIO (Perfil Local)
    user_kt = """package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int, // ID vindo do Servidor (Postgres)
    val nome: String,
    val email: String,
    val planType: String, // 'basic' ou 'premium'
    val validade: Long?,  // Timestamp da expiração
    val token: String?,   // Token de Sessão (JWT)
    val lastSync: Long = 0 // Última sincronização
)
"""
    write_file(f"{base_pkg}/entities/UserEntity.kt", user_kt)

    # 2.2 DIÁRIO (Ganhos e Despesas)
    diario_kt = """package com.motoristapro.android.data

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
"""
    write_file(f"{base_pkg}/entities/DiarioEntity.kt", diario_kt)

    # 2.3 CONFIG (Preferências e Carro)
    config_kt = """package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "configs")
data class ConfigEntity(
    @PrimaryKey val chave: String, // Ex: 'preco_combustivel', 'meta_semanal'
    val valor: String,
    val isSynced: Boolean = false
)
"""
    write_file(f"{base_pkg}/entities/ConfigEntity.kt", config_kt)

    # 2.4 AGENDAMENTOS (Agenda)
    agenda_kt = """package com.motoristapro.android.data

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
"""
    write_file(f"{base_pkg}/entities/AgendamentoEntity.kt", agenda_kt)

    # 2.5 MANUTENÇÃO (Alertas)
    manu_kt = """package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "manutencoes")
data class ManutencaoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    
    val item: String,      // Ex: Óleo
    val kmProxima: Double, // KM do odômetro alvo
    
    val isSynced: Boolean = false
)
"""
    write_file(f"{base_pkg}/entities/ManutencaoEntity.kt", manu_kt)

    # 2.6 CUSTOS FIXOS (IPVA, Seguro)
    custos_kt = """package com.motoristapro.android.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "custos_fixos")
data class CustoFixoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    
    val nome: String,
    val valor: Double,
    val tipo: String = "mensal", // mensal, anual, semanal
    
    val isSynced: Boolean = false
)
"""
    write_file(f"{base_pkg}/entities/CustoFixoEntity.kt", custos_kt)


    # ==============================================================================
    # 3. DAOs (Data Access Objects - As Queries SQL)
    # ==============================================================================
    
    # 3.1 Diario DAO
    diario_dao = """package com.motoristapro.android.data.dao

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
"""
    write_file(f"{base_pkg}/dao/DiarioDao.kt", diario_dao)

    # 3.2 Config DAO
    config_dao = """package com.motoristapro.android.data.dao

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
"""
    write_file(f"{base_pkg}/dao/ConfigDao.kt", config_dao)
    
    # 3.3 User DAO
    user_dao = """package com.motoristapro.android.data.dao

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
"""
    write_file(f"{base_pkg}/dao/UserDao.kt", user_dao)
    
    # 3.4 Manutenção DAO
    manu_dao = """package com.motoristapro.android.data.dao

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
"""
    write_file(f"{base_pkg}/dao/ManutencaoDao.kt", manu_dao)


    # ==============================================================================
    # 4. DATABASE INSTANCE (Singleton)
    # ==============================================================================
    db_class = """package com.motoristapro.android.data

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
                // Permite migração destrutiva durante desenvolvimento (apaga dados se mudar esquema)
                .fallbackToDestructiveMigration() 
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
"""
    write_file(f"{base_pkg}/AppDatabase.kt", db_class)

    print("🎉 Estrutura de Banco de Dados Completa Criada!")
    print("👉 Agora rode './gradlew assembleDebug' para verificar se compila.")

if __name__ == "__main__":
    main()


