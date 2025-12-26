import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Design Aplicado: {path}")

def main():
    print("🎨 Aplicando Identidade Visual do Site no App...")

    res_values = "app/src/main/res/values"
    res_draw = "app/src/main/res/drawable"
    res_layout = "app/src/main/res/layout"

    # ==========================================================================
    # 1. CORES (Extraídas do style.css do Site)
    # ==========================================================================
    colors_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary">#2563EB</color>
    <color name="primary_dark">#1D4ED8</color>
    <color name="accent">#10B981</color>
    <color name="warning">#D97706</color>
    <color name="danger">#EF4444</color>
    
    <color name="bg_body">#F0F4F8</color>
    <color name="text_main">#0F172A</color>
    <color name="text_secondary">#64748B</color>
    
    <color name="glass_white">#FFFFFF</color>
    <color name="glass_border">#E2E8F0</color>
    
    <color name="white">#FFFFFF</color>
    <color name="black">#000000</color>
    <color name="transparent">#00000000</color>
</resources>
"""
    write_file(f"{res_values}/colors.xml", colors_xml)

    # ==========================================================================
    # 2. DRAWABLES (Estilos dos Botões e Cards)
    # ==========================================================================

    # Fundo Gradiente (Botões Principais)
    bg_gradient = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient 
        android:startColor="#2563EB" 
        android:endColor="#1D4ED8" 
        android:angle="135"/>
    <corners android:radius="18dp"/>
</shape>
"""
    write_file(f"{res_draw}/bg_gradient_primary.xml", bg_gradient)

    # Card "Glass" (Fundo Branco Arredondado com Borda Sutil)
    bg_glass = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@color/glass_white"/>
    <corners android:radius="22dp"/>
    <stroke android:width="1dp" android:color="#E2E8F0"/>
</shape>
"""
    write_file(f"{res_draw}/bg_glass_card.xml", bg_glass)

    # Input Field (Campos de Texto)
    bg_input = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#FFFFFF"/>
    <corners android:radius="15dp"/>
    <stroke android:width="1dp" android:color="#CBD5E1"/>
</shape>
"""
    write_file(f"{res_draw}/bg_input_field.xml", bg_input)
    
    # Card de Destaque Azul (Header do Dashboard)
    bg_card_blue = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient 
        android:startColor="#3B82F6" 
        android:endColor="#2563EB" 
        android:angle="180"/>
    <corners android:radius="22dp"/>
</shape>
"""
    write_file(f"{res_draw}/bg_card_blue.xml", bg_card_blue)
    
    # Botão Secundário (Branco com Sombra)
    bg_btn_sec = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#FFFFFF"/>
    <corners android:radius="18dp"/>
    <stroke android:width="1dp" android:color="#E2E8F0"/>
</shape>
"""
    write_file(f"{res_draw}/bg_btn_secondary.xml", bg_btn_sec)


    # ==========================================================================
    # 3. LAYOUTS (Aplicando o visual)
    # ==========================================================================

    # DASHBOARD (activity_main.xml)
    dashboard_xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fillViewport="true"
    android:background="@color/bg_body">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="24dp">

        <!-- CABEÇALHO -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="30dp">
            
            <ImageView
                android:layout_width="50dp"
                android:layout_height="50dp"
                android:src="@mipmap/ic_launcher_round"
                android:elevation="5dp"/>
                
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginStart="15dp">
                
                <TextView
                    android:text="Painel de Controle"
                    android:textSize="18sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_main"
                    android:fontFamily="sans-serif-medium"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
                
                <TextView
                    android:text="Visão Geral"
                    android:textSize="13sp"
                    android:textColor="@color/text_secondary"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
            </LinearLayout>
        </LinearLayout>

        <!-- CARD FINANCEIRO (Estilo Hero do Site) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_card_blue"
            android:padding="30dp"
            android:layout_marginBottom="30dp"
            android:elevation="8dp">

            <TextView
                android:text="FATURAMENTO TOTAL"
                android:textSize="11sp"
                android:textColor="#BFDBFE"
                android:textStyle="bold"
                android:letterSpacing="0.1"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>

            <TextView
                android:id="@+id/tvTotalGanho"
                android:text="R$ 0,00"
                android:textSize="38sp"
                android:textStyle="bold"
                android:textColor="#FFFFFF"
                android:layout_marginTop="5dp"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>
            
            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#30FFFFFF"
                android:layout_marginTop="20dp"
                android:layout_marginBottom="20dp"/>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">
                
                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"
                    android:orientation="vertical">
                    <TextView android:text="CORRIDAS" android:textSize="11sp" android:textColor="#BFDBFE" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <TextView android:id="@+id/tvTotalCorridas" android:text="0" android:textSize="16sp" android:textColor="#FFFFFF" android:textStyle="bold" android:layout_marginTop="2dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                </LinearLayout>
                
                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"
                    android:orientation="vertical">
                    <TextView android:text="KM TOTAL" android:textSize="11sp" android:textColor="#BFDBFE" android:textStyle="bold" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <TextView android:id="@+id/tvTotalKm" android:text="0 km" android:textSize="16sp" android:textColor="#FFFFFF" android:textStyle="bold" android:layout_marginTop="2dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- AÇÕES RÁPIDAS -->
        <TextView
            android:text="AÇÕES RÁPIDAS"
            android:textSize="11sp"
            android:textStyle="bold"
            android:textColor="@color/text_secondary"
            android:layout_marginBottom="15dp"
            android:letterSpacing="0.05"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"/>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:weightSum="2"
            android:layout_marginBottom="20dp">

            <!-- BOTÃO LANÇAR -->
            <LinearLayout
                android:id="@+id/btnLancar"
                android:layout_width="0dp"
                android:layout_height="110dp"
                android:layout_weight="1"
                android:layout_marginEnd="10dp"
                android:background="@drawable/bg_glass_card"
                android:elevation="2dp"
                android:gravity="center"
                android:orientation="vertical"
                android:clickable="true"
                android:focusable="true">
                
                <ImageView android:src="@android:drawable/ic_input_add" android:layout_width="32dp" android:layout_height="32dp" android:tint="@color/accent"/>
                <TextView android:text="Novo\nLançamento" android:textSize="13sp" android:textStyle="bold" android:textColor="@color/text_main" android:textAlignment="center" android:layout_marginTop="8dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            </LinearLayout>

            <!-- BOTÃO ROBÔ -->
            <LinearLayout
                android:id="@+id/btnRobo"
                android:layout_width="0dp"
                android:layout_height="110dp"
                android:layout_weight="1"
                android:layout_marginStart="10dp"
                android:background="@drawable/bg_glass_card"
                android:elevation="2dp"
                android:gravity="center"
                android:orientation="vertical"
                android:clickable="true"
                android:focusable="true">
                
                <ImageView android:src="@android:drawable/ic_media_play" android:layout_width="32dp" android:layout_height="32dp" android:tint="@color/warning"/>
                <TextView android:text="Ativar\nRobô" android:textSize="13sp" android:textStyle="bold" android:textColor="@color/text_main" android:textAlignment="center" android:layout_marginTop="8dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            </LinearLayout>
        </LinearLayout>
        
        <!-- CARD HISTÓRICO RECENTE -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:elevation="2dp">
            
            <TextView
                android:text="Última Atividade"
                android:textSize="14sp"
                android:textStyle="bold"
                android:textColor="@color/text_main"
                android:layout_marginBottom="5dp"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>
                
            <TextView
                android:id="@+id/tvEmptyHistory"
                android:text="Carregando..."
                android:textSize="13sp"
                android:textColor="@color/text_secondary"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"/>
        </LinearLayout>

    </LinearLayout>
</ScrollView>
"""
    write_file(f"{res_layout}/activity_main.xml", dashboard_xml)

    # ADD ACTIVITY (activity_add_daily.xml)
    add_xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_body"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="24dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Novo Lançamento"
            android:textSize="22sp"
            android:textStyle="bold"
            android:textColor="@color/text_main"
            android:layout_marginBottom="25dp"/>

        <!-- SEÇÃO DATA -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="20dp">
            
            <TextView
                android:text="DATA DO TRABALHO"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="@color/text_secondary"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>
                
            <TextView
                android:id="@+id/tvDate"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Hoje"
                android:textSize="18sp"
                android:textStyle="bold"
                android:textColor="@color/primary"
                android:paddingTop="10dp"/>
        </LinearLayout>

        <!-- SEÇÃO GANHOS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="20dp">
            
            <TextView
                android:text="FATURAMENTO TOTAL"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="@color/text_secondary"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>
                
            <EditText
                android:id="@+id/etTotal"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="R$ 0.00"
                android:textSize="28sp"
                android:textStyle="bold"
                android:textColor="@color/accent"
                android:background="@null"
                android:inputType="numberDecimal"
                android:paddingTop="10dp"
                android:paddingBottom="10dp"/>

            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#E2E8F0"
                android:layout_marginBottom="15dp"/>

            <TextView
                android:text="Detalhar (Opcional)"
                android:textSize="11sp"
                android:layout_marginBottom="10dp"
                android:textColor="@color/text_secondary"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2" android:layout_marginBottom="10dp">
                <EditText android:id="@+id/etUber" android:layout_width="0dp" android:layout_height="50dp" android:layout_weight="1" android:hint="Uber" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:layout_marginEnd="8dp"/>
                <EditText android:id="@+id/et99" android:layout_width="0dp" android:layout_height="50dp" android:layout_weight="1" android:hint="99 Pop" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:layout_marginStart="8dp"/>
            </LinearLayout>
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2">
                <EditText android:id="@+id/etPart" android:layout_width="0dp" android:layout_height="50dp" android:layout_weight="1" android:hint="Particular" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:layout_marginEnd="8dp"/>
                <EditText android:id="@+id/etOutros" android:layout_width="0dp" android:layout_height="50dp" android:layout_weight="1" android:hint="Outros" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:layout_marginStart="8dp"/>
            </LinearLayout>
        </LinearLayout>

        <!-- SEÇÃO DESPESAS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="20dp">
            
            <TextView android:text="DESPESAS DO DIA" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/danger" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="3" android:layout_marginTop="15dp">
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingEnd="5dp">
                    <TextView android:text="Combustível" android:textSize="10sp" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etComb" android:layout_width="match_parent" android:layout_height="45dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="10dp" android:textSize="13sp"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingStart="2dp" android:paddingEnd="2dp">
                    <TextView android:text="Alimentação" android:textSize="10sp" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etAlim" android:layout_width="match_parent" android:layout_height="45dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="10dp" android:textSize="13sp"/>
                </LinearLayout>
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingStart="5dp">
                    <TextView android:text="Manutenção" android:textSize="10sp" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                    <EditText android:id="@+id/etManu" android:layout_width="match_parent" android:layout_height="45dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="10dp" android:textSize="13sp"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- SEÇÃO KM -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:background="@drawable/bg_glass_card"
            android:padding="20dp"
            android:layout_marginBottom="30dp"
            android:weightSum="2">
            
            <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingEnd="10dp">
                <TextView android:text="KM TOTAL" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                <EditText android:id="@+id/etKm" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp"/>
            </LinearLayout>
            
            <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:paddingStart="10dp">
                <TextView android:text="HORAS" android:textSize="10sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp" android:layout_width="wrap_content" android:layout_height="wrap_content"/>
                <EditText android:id="@+id/etHoras" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp"/>
            </LinearLayout>
        </LinearLayout>

        <Button
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
    write_file(f"{res_layout}/activity_add_daily.xml", add_xml)

    # Incrementa versão para garantir refresh
    os.system("python3 auto_version.py")
    
    print("✅ Identidade Visual Aplicada! Rode './gradlew assembleDebug'")

if __name__ == "__main__":
    main()


