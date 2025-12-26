import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo criado: {path}")

def main():
    print("🎨 Simplificando Layout para corrigir Crash...")

    res_draw = "app/src/main/res/drawable"
    res_layout = "app/src/main/res/layout"

    # 1. CRIAR FUNDOS ARREDONDADOS (Substitui o CardView)
    
    # Fundo Azul (Para o Card de Faturamento)
    bg_card_blue = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#2563EB"/>
    <corners android:radius="20dp"/>
</shape>
"""
    write_file(f"{res_draw}/bg_card_blue.xml", bg_card_blue)

    # Fundo Branco com Borda (Para os Botões)
    bg_card_white = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#FFFFFF"/>
    <corners android:radius="15dp"/>
    <stroke android:width="1dp" android:color="#E2E8F0"/>
</shape>
"""
    write_file(f"{res_draw}/bg_card_white.xml", bg_card_white)

    # 2. REESCREVER ACTIVITY_MAIN.XML (Sem CardView)
    # Trocamos <androidx.cardview.widget.CardView> por <LinearLayout> com background
    
    new_layout = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true"
    android:background="#F1F5F9">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- CABEÇALHO -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="25dp">
            
            <ImageView
                android:layout_width="50dp"
                android:layout_height="50dp"
                android:src="@mipmap/ic_launcher_round"/>
                
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginStart="15dp">
                
                <TextView
                    android:text="Olá, Motorista"
                    android:textSize="18sp"
                    android:textStyle="bold"
                    android:textColor="#0F172A"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
                
                <TextView
                    android:text="Visão Geral (Offline)"
                    android:textSize="12sp"
                    android:textColor="#64748B"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
            </LinearLayout>
        </LinearLayout>

        <!-- CARD DE RESUMO FINANCEIRO (LinearLayout com fundo azul) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_card_blue"
            android:padding="25dp"
            android:layout_marginBottom="25dp"
            android:elevation="4dp">

            <TextView
                android:text="FATURAMENTO TOTAL"
                android:textSize="12sp"
                android:textColor="#93C5FD"
                android:textStyle="bold"
                android:letterSpacing="0.1"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>

            <TextView
                android:id="@+id/tvTotalGanho"
                android:text="R$ 0,00"
                android:textSize="36sp"
                android:textStyle="bold"
                android:textColor="#FFFFFF"
                android:layout_marginTop="5dp"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>
            
            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#40FFFFFF"
                android:layout_marginTop="15dp"
                android:layout_marginBottom="15dp"/>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">
                
                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"
                    android:orientation="vertical">
                    <TextView android:text="CORRIDAS" android:textSize="10sp" android:textColor="#93C5FD" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <TextView android:id="@+id/tvTotalCorridas" android:text="0" android:textSize="16sp" android:textColor="#FFFFFF" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                </LinearLayout>
                
                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"
                    android:orientation="vertical">
                    <TextView android:text="KM TOTAL" android:textSize="10sp" android:textColor="#93C5FD" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <TextView android:id="@+id/tvTotalKm" android:text="0 km" android:textSize="16sp" android:textColor="#FFFFFF" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- AÇÕES RÁPIDAS -->
        <TextView
            android:text="AÇÕES RÁPIDAS"
            android:textSize="12sp"
            android:textStyle="bold"
            android:textColor="#64748B"
            android:layout_marginBottom="10dp"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"/>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2"
            android:layout_marginBottom="15dp">

            <!-- BOTÃO LANÇAR -->
            <LinearLayout
                android:id="@+id/btnLancar"
                android:layout_width="0dp"
                android:layout_height="100dp"
                android:layout_weight="1"
                android:layout_marginEnd="8dp"
                android:background="@drawable/bg_card_white"
                android:elevation="2dp"
                android:gravity="center"
                android:orientation="vertical"
                android:clickable="true"
                android:focusable="true">
                
                <ImageView android:src="@android:drawable/ic_input_add" android:layout_width="30dp" android:layout_height="30dp" android:tint="#10B981"/>
                <TextView android:text="Novo\nLançamento" android:textSize="14sp" android:textStyle="bold" android:textColor="#0F172A" android:textAlignment="center" android:layout_marginTop="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            </LinearLayout>

            <!-- BOTÃO ROBÔ -->
            <LinearLayout
                android:id="@+id/btnRobo"
                android:layout_width="0dp"
                android:layout_height="100dp"
                android:layout_weight="1"
                android:layout_marginStart="8dp"
                android:background="@drawable/bg_card_white"
                android:elevation="2dp"
                android:gravity="center"
                android:orientation="vertical"
                android:clickable="true"
                android:focusable="true">
                
                <ImageView android:src="@android:drawable/ic_media_play" android:layout_width="30dp" android:layout_height="30dp" android:tint="#F59E0B"/>
                <TextView android:text="Ativar\nRobô" android:textSize="14sp" android:textStyle="bold" android:textColor="#0F172A" android:textAlignment="center" android:layout_marginTop="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            </LinearLayout>
        </LinearLayout>
        
        <TextView
            android:text="Histórico Recente"
            android:textSize="12sp"
            android:textStyle="bold"
            android:textColor="#64748B"
            android:layout_marginBottom="10dp"
            android:layout_marginTop="10dp"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"/>
            
        <TextView
            android:id="@+id/tvEmptyHistory"
            android:text="Nenhum lançamento encontrado.\nToque em 'Novo Lançamento' para começar."
            android:gravity="center"
            android:padding="30dp"
            android:background="#FFFFFF"
            android:textColor="#94A3B8"
            android:textSize="12sp"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"/>

    </LinearLayout>
</ScrollView>
"""
    write_file(f"{res_layout}/activity_main.xml", new_layout)
    
    # 3. ATUALIZAR MAINACTIVITY.KT (Remover referências a CardView)
    main_path = "app/src/main/java/com/motoristapro/android/MainActivity.kt"
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove import do CardView
        content = content.replace("import androidx.cardview.widget.CardView", "")
        # Troca casting de CardView por LinearLayout ou View genérica
        content = content.replace("findViewById<CardView>", "findViewById<LinearLayout>")
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ MainActivity.kt atualizado (CardView removido).")

    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("🚀 Layout simplificado! Rode './gradlew assembleDebug'")

if __name__ == "__main__":
    main()


