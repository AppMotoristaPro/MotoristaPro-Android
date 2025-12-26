package com.motoristapro.android

import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.motoristapro.android.data.DailyRepository

class HistoryActivity : AppCompatActivity() {

    // Variáveis com ? (Nullable) para segurança
    private var recyclerView: RecyclerView? = null
    private var btnBack: ImageView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_history)

            // Inicialização com IDs explícitos
            recyclerView = findViewById(R.id.recyclerView)
            btnBack = findViewById(R.id.btnBack)
            
            // Configura RecyclerView
            if (recyclerView != null) {
                recyclerView!!.layoutManager = LinearLayoutManager(this)
            }
            
            // Configura Botão Voltar
            btnBack?.setOnClickListener { finish() }

            loadData()
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro UI Histórico: " + e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun loadData() {
        try {
            val repo = DailyRepository(this)
            val list = repo.getAll()
            
            if (list.isEmpty()) {
                Toast.makeText(this, "Nenhum registo encontrado.", Toast.LENGTH_SHORT).show()
            }
            
            if (recyclerView != null) {
                val adapter = HistoryAdapter(list)
                recyclerView!!.adapter = adapter
            }
            
        } catch (e: Exception) {
            Toast.makeText(this, "Erro ao carregar lista: " + e.message, Toast.LENGTH_SHORT).show()
        }
    }
}
