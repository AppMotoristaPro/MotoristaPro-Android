import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Layout Corrigido: {path}")

def main():
    print("🚑 Corrigindo 'layout_height' ausente em activity_add_daily.xml...")
    
    path = "app/src/main/res/layout/activity_add_daily.xml"
    
    # XML Completo e Corrigido
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_body"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp">

        <!-- HEADER -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="25dp">
            
            <ImageView
                android:id="@+id/btnBack"
                android:layout_width="40dp"
                android:layout_height="40dp"
                android:src="@android:drawable/ic_menu_revert"
                android:padding="8dp"
                android:background="@drawable/bg_glass_card"
                android:elevation="2dp"
                android:clickable="true"
                android:focusable="true"
                android:tint="@color/text_main"/>
                
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:gravity="center">
                
                <TextView
                    android:text="Novo Lançamento"
                    android:textSize="18sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_main"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
                
                <TextView
                    android:text="Fechamento do Dia"
                    android:textSize="12sp"
                    android:textColor="@color/text_secondary"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
            </LinearLayout>
        </LinearLayout>

        <!-- 1. DADOS GERAIS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="15dp">
            
            <TextView android:text="RESUMO" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="15dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <TextView android:text="DATA DO TRABALHO" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            <TextView android:id="@+id/tvDate" android:layout_width="match_parent" android:layout_height="50dp" android:text="Hoje" android:textSize="16sp" android:textStyle="bold" android:textColor="@color/text_main" android:background="@drawable/bg_input_field" android:gravity="center_vertical" android:paddingStart="15dp" android:layout_marginBottom="15dp"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2">
                <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginEnd="5dp">
                    <TextView android:text="KM TOTAL" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etKm" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:hint="0.0"/>
                </LinearLayout>
                <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginStart="5dp">
                    <TextView android:text="HORAS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etHoras" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:hint="0.0"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- 2. FATURAMENTO -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="15dp">
            
            <LinearLayout android:orientation="horizontal" android:layout_width="match_parent" android:layout_height="wrap_content" android:gravity="center_vertical">
                <TextView android:text="FATURAMENTO" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/accent" android:layout_weight="1" android:layout_width="0dp" android:layout_height="wrap_content"/>
                <TextView android:id="@+id/badgeTotal" android:text="R$ 0,00" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/white" android:background="@drawable/bg_gradient_primary" android:padding="6dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            </LinearLayout>

            <EditText
                android:id="@+id/etTotal"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="R$ 0,00"
                android:textSize="32sp"
                android:textStyle="bold"
                android:textColor="@color/accent"
                android:background="@null"
                android:inputType="numberDecimal"
                android:paddingTop="15dp"
                android:paddingBottom="15dp"/>
            
            <View android:layout_width="match_parent" android:layout_height="1dp" android:background="#E2E8F0" android:layout_marginBottom="15dp"/>

            <!-- ADDER -->
            <TextView android:text="DETALHAR GANHOS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="10dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical">
                <EditText 
                    android:id="@+id/etNewEarnValue" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:layout_height="50dp" 
                    android:hint="R$ 0,00" 
                    android:inputType="numberDecimal" 
                    android:textColor="@color/accent"
                    android:textStyle="bold"
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp"
                    android:layout_marginEnd="10dp"/>
                
                <Spinner
                    android:id="@+id/spNewEarnType"
                    android:layout_width="110dp"
                    android:layout_height="50dp"
                    android:background="@drawable/bg_input_field"
                    android:padding="5dp"
                    android:layout_marginEnd="10dp"/>
                    
                <ImageView
                    android:id="@+id/btnAddEarn"
                    android:layout_width="50dp"
                    android:layout_height="50dp"
                    android:src="@android:drawable/ic_input_add"
                    android:background="@drawable/bg_gradient_primary"
                    android:padding="12dp"
                    android:clickable="true"
                    android:focusable="true"
                    android:tint="@color/white"/>
            </LinearLayout>

            <LinearLayout
                android:id="@+id/containerEarnings"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="10dp"/>
        </LinearLayout>

        <!-- 3. CORRIDAS (AQUI ESTAVA O ERRO DE ALTURA) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="15dp">
            
            <TextView android:text="QUANTIDADE DE VIAGENS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="10dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="4">
                <!-- Adicionado layout_height="wrap_content" em todos os LinearLayouts internos -->
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:gravity="center">
                    <TextView android:text="UBER" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtdUber" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
                
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:gravity="center" android:layout_marginStart="5dp">
                    <TextView android:text="99" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtd99" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
                
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:gravity="center" android:layout_marginStart="5dp">
                    <TextView android:text="PART" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtdPart" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
                
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:gravity="center" android:layout_marginStart="5dp">
                    <TextView android:text="OUT" android:textSize="9sp" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/qtdOutros" android:layout_width="match_parent" android:layout_height="40dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- 4. DESPESAS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="25dp">
            
            <TextView android:text="DESPESAS DO DIA" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/danger" android:layout_marginBottom="10dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical">
                <EditText 
                    android:id="@+id/etNewExpValue" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:layout_height="50dp" 
                    android:hint="R$ 0,00" 
                    android:inputType="numberDecimal" 
                    android:textColor="@color/danger"
                    android:textStyle="bold"
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp"
                    android:layout_marginEnd="10dp"/>
                
                <Spinner
                    android:id="@+id/spNewExpType"
                    android:layout_width="110dp"
                    android:layout_height="50dp"
                    android:background="@drawable/bg_input_field"
                    android:padding="5dp"
                    android:layout_marginEnd="10dp"/>
                    
                <ImageView
                    android:id="@+id/btnAddExp"
                    android:layout_width="50dp"
                    android:layout_height="50dp"
                    android:src="@android:drawable/ic_input_add"
                    android:background="@drawable/bg_gradient_primary"
                    android:padding="12dp"
                    android:clickable="true"
                    android:focusable="true"
                    android:tint="@color/white"/>
            </LinearLayout>

            <LinearLayout
                android:id="@+id/containerExpenses"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="10dp"/>
        </LinearLayout>

        <!-- Usei androidx.appcompat.widget.AppCompatButton para garantir suporte a background custom -->
        <androidx.appcompat.widget.AppCompatButton
            android:id="@+id/btnSave"
            android:layout_width="match_parent"
            android:layout_height="60dp"
            android:text="CONFIRMAR LANÇAMENTO"
            android:background="@drawable/bg_gradient_primary"
            android:textColor="#FFFFFF"
            android:textSize="16sp"
            android:textStyle="bold"
            android:elevation="5dp"/>

    </LinearLayout>
</ScrollView>
"""
    write_file(path, xml_content)
    
    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("🚀 XML Corrigido. Altura definida em todos os elementos.")

if __name__ == "__main__":
    main()
