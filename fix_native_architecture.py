import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Reconstruído: {path}")

def main():
    print("🚑 Corrigindo Dependências do Room e Estrutura de Pacotes...")

    # ==============================================================================
    # 1. CORRIGIR BUILD.GRADLE (Garantir Room e Kapt)
    # ==============================================================================
    gradle_path = "app/build.gradle.kts"
    gradle_content = """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt") // Essencial para o Room
}

android {
    namespace = "com.motoristapro.android"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.motoristapro.android"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // ML Kit (OCR)
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    implementation("androidx.lifecycle:lifecycle-service:2.6.1")
    
    // ROOM DATABASE (Versão Estável)
    val room_version = "2.6.1"
    implementation("androidx.room:room-runtime:$room_version")
    implementation("androidx.room:room-ktx:$room_version")
    kapt("androidx.room:room-compiler:$room_version")
    
    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.6.1")
}
"""
    write_file(gradle_path, gradle_content)

    # ==============================================================================
    # 2. RECONSTRUIR BANCO DE DADOS (Pacotes Corrigidos)
    # ==============================================================================
    base_pkg = "app/src/main/java/com/motoristapro/android/data"
    
    # Converters
    write_file(f"{base_pkg}/Converters.kt", """package com.motoristapro.android.data

import androidx.room.TypeConverter
import java.util.Date

class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }
    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time
}
""")

    # --- ENTIDADES (Pacote: .data.entities) ---
    ent_pkg = "package com.motoristapro.android.data.entities"

    write_file(f"{base_pkg}/entities/UserEntity.kt", f"""{ent_pkg}
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int,
    val nome: String,
    val email: String,
    val planType: String,
    val validade: Long?,
    val token: String?,
    val lastSync: Long = 0
)
""")

    write_file(f"{base_pkg}/entities/DiarioEntity.kt", f"""{ent_pkg}
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
""")

    write_file(f"{base_pkg}/entities/ConfigEntity.kt", f"""{ent_pkg}
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "configs")
data class ConfigEntity(
    @PrimaryKey val chave: String,
    val valor: String,
    val isSynced: Boolean = false
)
""")

    write_file(f"{base_pkg}/entities/AgendamentoEntity.kt", f"""{ent_pkg}
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
    val status: String = "pendente",
    val isSynced: Boolean = false
)
""")

    write_file(f"{base_pkg}/entities/ManutencaoEntity.kt", f"""{ent_pkg}
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "manutencoes")
data class ManutencaoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    val item: String,
    val kmProxima: Double,
    val isSynced: Boolean = false
)
""")

    write_file(f"{base_pkg}/entities/CustoFixoEntity.kt", f"""{ent_pkg}
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "custos_fixos")
data class CustoFixoEntity(
    @PrimaryKey(autoGenerate = true) val localId: Long = 0,
    val serverId: Int? = null,
    val nome: String,
    val valor: Double,
    val tipo: String = "mensal",
    val isSynced: Boolean = false
)
""")

    # --- DAOs (Pacote: .data.dao) ---
    dao_pkg = "package com.motoristapro.android.data.dao"
    
    write_file(f"{base_pkg}/dao/DiarioDao.kt", f"""{dao_pkg}
import androidx.room.*
import com.motoristapro.android.data.entities.DiarioEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DiarioDao {{
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
}}
""")

    write_file(f"{base_pkg}/dao/ConfigDao.kt", f"""{dao_pkg}
import androidx.room.*
import com.motoristapro.android.data.entities.ConfigEntity

@Dao
interface ConfigDao {{
    @Query("SELECT valor FROM configs WHERE chave = :key LIMIT 1")
    suspend fun getValue(key: String): String?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(config: ConfigEntity)
    
    @Query("SELECT * FROM configs")
    suspend fun getAll(): List<ConfigEntity>
}}
""")

    write_file(f"{base_pkg}/dao/UserDao.kt", f"""{dao_pkg}
import androidx.room.*
import com.motoristapro.android.data.entities.UserEntity

@Dao
interface UserDao {{
    @Query("SELECT * FROM users LIMIT 1")
    suspend fun getUser(): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Query("DELETE FROM users")
    suspend fun clear()
}}
""")

    write_file(f"{base_pkg}/dao/ManutencaoDao.kt", f"""{dao_pkg}
import androidx.room.*
import com.motoristapro.android.data.entities.ManutencaoEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ManutencaoDao {{
    @Query("SELECT * FROM manutencoes ORDER BY kmProxima ASC")
    fun getAll(): Flow<List<ManutencaoEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ManutencaoEntity)

    @Delete
    suspend fun delete(item: ManutencaoEntity)
}}
""")

    # --- DATABASE PRINCIPAL (Pacote: .data) ---
    write_file(f"{base_pkg}/AppDatabase.kt", """package com.motoristapro.android.data

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
""")

    # ==============================================================================
    # 3. CORRIGIR ADD ACTIVITY (Imports)
    # ==============================================================================
    add_activity_path = "app/src/main/java/com/motoristapro/android/AddDailyActivity.kt"
    add_activity_code = """package com.motoristapro.android

import android.app.DatePickerDialog
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.motoristapro.android.data.AppDatabase
import com.motoristapro.android.data.entities.DiarioEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class AddDailyActivity : AppCompatActivity() {

    private val calendar = Calendar.getInstance()
    private lateinit var tvDate: TextView
    private lateinit var etTotal: EditText
    
    // Inputs
    private lateinit var etUber: EditText
    private lateinit var et99: EditText
    private lateinit var etPart: EditText
    private lateinit var etOutros: EditText
    private lateinit var etComb: EditText
    private lateinit var etAlim: EditText
    private lateinit var etManu: EditText
    private lateinit var etKm: EditText
    private lateinit var etHoras: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_add_daily)

        initViews()
        setupDatePicker()
        setupAutoSum()
        
        findViewById<Button>(R.id.btnSave).setOnClickListener { saveEntry() }
    }

    private fun initViews() {
        tvDate = findViewById(R.id.tvDate)
        etTotal = findViewById(R.id.etTotal)
        etUber = findViewById(R.id.etUber)
        et99 = findViewById(R.id.et99)
        etPart = findViewById(R.id.etPart)
        etOutros = findViewById(R.id.etOutros)
        etComb = findViewById(R.id.etComb)
        etAlim = findViewById(R.id.etAlim)
        etManu = findViewById(R.id.etManu)
        etKm = findViewById(R.id.etKm)
        etHoras = findViewById(R.id.etHoras)
        
        updateDateLabel()
    }

    private fun setupDatePicker() {
        tvDate.setOnClickListener {
            DatePickerDialog(this, { _, year, month, day ->
                calendar.set(year, month, day)
                updateDateLabel()
            }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show()
        }
    }

    private fun updateDateLabel() {
        val fmt = SimpleDateFormat("dd/MM/yyyy", Locale("pt", "BR"))
        tvDate.text = fmt.format(calendar.time)
    }

    private fun setupAutoSum() {
        val watcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { calculateTotal() }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        }
        etUber.addTextChangedListener(watcher)
        et99.addTextChangedListener(watcher)
        etPart.addTextChangedListener(watcher)
        etOutros.addTextChangedListener(watcher)
    }

    private fun calculateTotal() {
        val u = etUber.text.toString().toDoubleOrNull() ?: 0.0
        val n = et99.text.toString().toDoubleOrNull() ?: 0.0
        val p = etPart.text.toString().toDoubleOrNull() ?: 0.0
        val o = etOutros.text.toString().toDoubleOrNull() ?: 0.0
        val sum = u + n + p + o
        if (sum > 0) etTotal.setText(String.format("%.2f", sum).replace(",", "."))
    }

    private fun saveEntry() {
        val total = etTotal.text.toString().toDoubleOrNull()
        if (total == null || total <= 0) {
            Toast.makeText(this, "Informe o Faturamento Total", Toast.LENGTH_SHORT).show()
            return
        }

        val diario = DiarioEntity(
            data = calendar.timeInMillis,
            ganhoBruto = total,
            ganhoUber = etUber.text.toString().toDoubleOrNull() ?: 0.0,
            ganho99 = et99.text.toString().toDoubleOrNull() ?: 0.0,
            ganhoPart = etPart.text.toString().toDoubleOrNull() ?: 0.0,
            ganhoOutros = etOutros.text.toString().toDoubleOrNull() ?: 0.0,
            despCombustivel = etComb.text.toString().toDoubleOrNull() ?: 0.0,
            despAlimentacao = etAlim.text.toString().toDoubleOrNull() ?: 0.0,
            despManutencao = etManu.text.toString().toDoubleOrNull() ?: 0.0,
            kmPercorrido = etKm.text.toString().toDoubleOrNull() ?: 0.0,
            horasTrabalhadas = etHoras.text.toString().toDoubleOrNull() ?: 0.0,
            isSynced = false
        )

        // Salvar no Banco (Background)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val db = AppDatabase.getDatabase(applicationContext)
                db.diarioDao().insert(diario)
                
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@AddDailyActivity, "✅ Guardado no telemóvel!", Toast.LENGTH_LONG).show()
                    finish()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@AddDailyActivity, "Erro ao guardar: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
"""
    write_file(add_activity_path, add_activity_code)

    print("🎉 Correção Geral Aplicada! A estrutura de pacotes agora está coerente.")
    print("👉 Rode './gradlew assembleDebug' para verificar.")

if __name__ == "__main__":
    main()


