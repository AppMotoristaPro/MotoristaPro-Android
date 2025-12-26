import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Design Aplicado: {path}")

def main():
    print("🎨 Iniciando Reforma Visual Completa (Web -> Nativo)...")

    res_values = "app/src/main/res/values"
    res_drawable = "app/src/main/res/drawable"
    res_layout = "app/src/main/res/layout"

    # ==========================================================================
    # 1. PALETA DE CORES (Baseada no TailwindCSS do Site)
    # ==========================================================================
    colors_xml = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Brand Colors -->
    <color name="primary">#2563EB</color>       <!-- Blue 600 -->
    <color name="primary_dark">#1D4ED8</color>  <!-- Blue 700 -->
    <color name="secondary">#64748B</color>     <!-- Slate 500 -->
    <color name="accent">#10B981</color>        <!-- Emerald 500 -->
    <color name="warning">#F59E0B</color>       <!-- Amber 500 -->
    <color name="danger">#EF4444</color>        <!-- Red 500 -->
    
    <!-- Backgrounds -->
    <color name="bg_body">#F8FAFC</color>       <!-- Slate 50 -->
    <color name="bg_card">#FFFFFF</color>       <!-- White -->
    <color name="bg_input">#F1F5F9</color>      <!-- Slate 100 -->
    
    <!-- Text -->
    <color name="text_main">#0F172A</color>     <!-- Slate 900 -->
    <color name="text_dim">#94A3B8</color>      <!-- Slate 400 -->
    
    <!-- UI Elements -->
    <color name="border_light">#E2E8F0</color>  <!-- Slate 200 -->
    <color name="white">#FFFFFF</color>
    
    <!-- Status -->
    <color name="uber_black">#000000</color>
    <color name="pop_yellow">#F7C948</color>
</resources>
"""
    write_file(f"{res_values}/colors.xml", colors_xml)

    # ==========================================================================
    # 2. ESTILOS CSS TRADUZIDOS PARA ANDROID (Drawables)
    # ==========================================================================

    # Card Glass (Fundo Branco, Borda Fina, Arredondado)
    # Equivalente a: background: white; border: 1px solid #e2e8f0; border-radius: 20px;
    bg_glass_card = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@color/bg_card"/>
    <corners android:radius="20dp"/>
    <stroke android:width="1dp" android:color="@color/border_light"/>
</shape>
"""
    write_file(f"{res_drawable}/bg_glass_card.xml", bg_glass_card)

    # Input Field (Fundo cinza claro, arredondado)
    # Equivalente a: background: #f1f5f9; border-radius: 12px;
    bg_input = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@color/bg_input"/>
    <corners android:radius="12dp"/>
    <stroke android:width="0dp" android:color="@color/transparent"/>
</shape>
"""
    write_file(f"{res_drawable}/bg_input_field.xml", bg_input)

    # Botão Gradiente (Azul Vibrante)
    # Equivalente a: background: linear-gradient(135deg, #2563EB, #1D4ED8);
    bg_gradient = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient 
        android:startColor="@color/primary" 
        android:endColor="@color/primary_dark" 
        android:angle="135"/>
    <corners android:radius="16dp"/>
</shape>
"""
    write_file(f"{res_drawable}/bg_btn_gradient.xml", bg_gradient)

    # Botão ícone (Círculo colorido)
    bg_circle_btn = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="@color/primary"/>
</shape>
"""
    write_file(f"{res_drawable}/bg_circle_btn.xml", bg_circle_btn)

    # ==========================================================================
    # 3. ÍCONES VETORIAIS (Para substituir os feios padrão)
    # ==========================================================================
    
    # Ícone Calendário
    ic_calendar = """<vector android:height="24dp" android:tint="#2563EB"
    android:viewportHeight="24" android:viewportWidth="24"
    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">
    <path android:fillColor="@android:color/white" android:pathData="M19,4h-1V2h-2v2H8V2H6v2H5C3.89,4 3.01,4.9 3.01,6L3,20c0,1.1 0.89,2 2,2h14c1.1,0 2,-0.9 2,-2V6c0,-1.1 -0.9,-2 -2,-2zM19,20H5V10h14v10zM19,8H5V6h14v2zM9,14H7v-2h2v2zM13,14h-2v-2h2v2zM17,14h-2v-2h2v2zM9,18H7v-2h2v2zM13,18h-2v-2h2v2zM17,18h-2v-2h2v2z"/>
</vector>"""
    write_file(f"{res_drawable}/ic_custom_calendar.xml", ic_calendar)

    # Ícone Voltar
    ic_back = """<vector android:height="24dp" android:tint="#0F172A"
    android:viewportHeight="24" android:viewportWidth="24"
    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">
    <path android:fillColor="@android:color/white" android:pathData="M20,11H7.83l5.59,-5.59L12,4l-8,8 8,8 1.41,-1.41L7.83,13H20v-2z"/>
</vector>"""
    write_file(f"{res_drawable}/ic_custom_back.xml", ic_back)

    # Ícone Adicionar (Plus)
    ic_add = """<vector android:height="24dp" android:tint="#FFFFFF"
    android:viewportHeight="24" android:viewportWidth="24"
    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">
    <path android:fillColor="@android:color/white" android:pathData="M19,13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
</vector>"""
    write_file(f"{res_drawable}/ic_custom_add.xml", ic_add)


    # ==========================================================================
    # 4. RECONSTRUÇÃO DA TELA (activity_add_daily.xml)
    # ==========================================================================
    # Foco: Espaçamento (Padding), Hierarquia Visual e Cores do Site
    
    layout_xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_body"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingStart="24dp"
        android:paddingEnd="24dp"
        android:paddingTop="32dp"
        android:paddingBottom="40dp">

        <!-- HEADER (Botão Voltar + Título) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginBottom="32dp">
            
            <ImageView
                android:id="@+id/btnBack"
                android:layout_width="48dp"
                android:layout_height="48dp"
                android:src="@drawable/ic_custom_back"
                android:padding="12dp"
                android:background="@drawable/bg_glass_card"
                android:elevation="2dp"
                android:clickable="true"
                android:focusable="true"/>
                
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginStart="16dp">
                
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Novo Lançamento"
                    android:textSize="20sp"
                    android:textStyle="bold"
                    android:textColor="@color/text_main"
                    android:fontFamily="sans-serif-medium"/>
                
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="Registre seu dia"
                    android:textSize="13sp"
                    android:textColor="@color/text_secondary"/>
            </LinearLayout>
        </LinearLayout>

        <!-- CARD 1: DATA E RESUMO (Operacional) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="24dp"
            android:layout_marginBottom="24dp"
            android:elevation="4dp">
            
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical"
                android:layout_marginBottom="20dp">
                
                <ImageView
                    android:layout_width="24dp"
                    android:layout_height="24dp"
                    android:src="@drawable/ic_custom_calendar"
                    android:layout_marginEnd="10dp"/>
                    
                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"
                    android:orientation="vertical">
                    
                    <TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="DATA DE HOJE"
                        android:textSize="11sp"
                        android:textStyle="bold"
                        android:letterSpacing="0.05"
                        android:textColor="@color/text_secondary"/>
                        
                    <TextView
                        android:id="@+id/tvDate"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:text="--/--/----"
                        android:textSize="18sp"
                        android:textStyle="bold"
                        android:textColor="@color/primary"/>
                </LinearLayout>
            </LinearLayout>
            
            <View android:layout_width="match_parent" android:layout_height="1dp" android:background="@color/border_light" android:layout_marginBottom="20dp"/>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="2" android:baselineAligned="false">
                <!-- KM Input -->
                <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginEnd="8dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="KM RODADO" android:textSize="11sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="8dp"/>
                    <EditText android:id="@+id/etKm" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:hint="0.0" android:textSize="16sp" android:textColor="@color/text_main"/>
                </LinearLayout>
                
                <!-- Horas Input -->
                <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginStart="8dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="HORAS" android:textSize="11sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="8dp"/>
                    <EditText android:id="@+id/etHoras" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="numberDecimal" android:background="@drawable/bg_input_field" android:padding="12dp" android:hint="0.0" android:textSize="16sp" android:textColor="@color/text_main"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- CARD 2: FATURAMENTO (O Principal) -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="24dp"
            android:layout_marginBottom="24dp"
            android:elevation="4dp">
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical" android:layout_marginBottom="10dp">
                <TextView android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content" android:text="FATURAMENTO TOTAL" android:textSize="12sp" android:textStyle="bold" android:letterSpacing="0.05" android:textColor="@color/accent"/>
                <TextView android:id="@+id/badgeTotal" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="R$ 0,00" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/white" android:background="@drawable/bg_btn_gradient" android:paddingStart="12dp" android:paddingEnd="12dp" android:paddingTop="6dp" android:paddingBottom="6dp"/>
            </LinearLayout>

            <EditText
                android:id="@+id/etTotal"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="R$ 0,00"
                android:textSize="40sp"
                android:textStyle="bold"
                android:textColor="@color/text_main"
                android:background="@null"
                android:inputType="numberDecimal"
                android:paddingTop="10dp"
                android:paddingBottom="20dp"/>
            
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Adicionar Ganho Individual" android:textSize="12sp" android:textColor="@color/text_secondary" android:layout_marginBottom="10dp"/>

            <!-- Inputs Dinâmicos (Adicionar) -->
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical">
                <EditText 
                    android:id="@+id/etNewEarnValue" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:layout_height="56dp" 
                    android:hint="Valor (R$)" 
                    android:inputType="numberDecimal" 
                    android:textColor="@color/text_main"
                    android:textSize="16sp"
                    android:background="@drawable/bg_input_field" 
                    android:paddingStart="16dp"
                    android:paddingEnd="16dp"
                    android:layout_marginEnd="10dp"/>
                
                <Spinner
                    android:id="@+id/spNewEarnType"
                    android:layout_width="100dp"
                    android:layout_height="56dp"
                    android:background="@drawable/bg_input_field"
                    android:padding="5dp"
                    android:layout_marginEnd="10dp"/>
                    
                <LinearLayout
                    android:id="@+id/btnAddEarn"
                    android:layout_width="56dp"
                    android:layout_height="56dp"
                    android:background="@drawable/bg_circle_btn"
                    android:gravity="center"
                    android:clickable="true"
                    android:focusable="true"
                    android:elevation="4dp">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp" android:src="@drawable/ic_custom_add" android:tint="@color/white"/>
                </LinearLayout>
            </LinearLayout>

            <!-- Lista Dinâmica -->
            <LinearLayout
                android:id="@+id/containerEarnings"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="16dp"/>
        </LinearLayout>

        <!-- CARD 3: QUANTIDADE DE VIAGENS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="24dp"
            android:layout_marginBottom="24dp"
            android:elevation="4dp">
            
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="NÚMERO DE CORRIDAS" android:textSize="11sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="16dp"/>
            
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:weightSum="4">
                <!-- UBER -->
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center" android:layout_marginEnd="5dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Uber" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/text_main" android:layout_marginBottom="5dp"/>
                    <EditText android:id="@+id/qtdUber" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center" android:textColor="@color/text_main" android:textStyle="bold"/>
                </LinearLayout>
                
                <!-- 99 -->
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center" android:layout_marginEnd="5dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="99" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/warning" android:layout_marginBottom="5dp"/>
                    <EditText android:id="@+id/qtd99" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center" android:textColor="@color/text_main" android:textStyle="bold"/>
                </LinearLayout>
                
                <!-- PART -->
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center" android:layout_marginEnd="5dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Part" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/primary" android:layout_marginBottom="5dp"/>
                    <EditText android:id="@+id/qtdPart" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center" android:textColor="@color/text_main" android:textStyle="bold"/>
                </LinearLayout>
                
                <!-- OUT -->
                <LinearLayout android:orientation="vertical" android:layout_width="0dp" android:layout_weight="1" android:gravity="center">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Out" android:textSize="12sp" android:textStyle="bold" android:textColor="@color/text_secondary" android:layout_marginBottom="5dp"/>
                    <EditText android:id="@+id/qtdOutros" android:layout_width="match_parent" android:layout_height="50dp" android:inputType="number" android:background="@drawable/bg_input_field" android:gravity="center" android:textColor="@color/text_main" android:textStyle="bold"/>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <!-- CARD 4: DESPESAS -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@drawable/bg_glass_card"
            android:padding="24dp"
            android:layout_marginBottom="30dp"
            android:elevation="4dp">
            
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="DESPESAS E CUSTOS" android:textSize="11sp" android:textStyle="bold" android:textColor="@color/danger" android:layout_marginBottom="16dp"/>

            <!-- Inputs Dinâmicos (Despesas) -->
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical">
                <EditText 
                    android:id="@+id/etNewExpValue" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:layout_height="56dp" 
                    android:hint="Valor (R$)" 
                    android:inputType="numberDecimal" 
                    android:textColor="@color/danger"
                    android:textSize="16sp"
                    android:background="@drawable/bg_input_field" 
                    android:paddingStart="16dp"
                    android:paddingEnd="16dp"
                    android:layout_marginEnd="10dp"/>
                
                <Spinner
                    android:id="@+id/spNewExpType"
                    android:layout_width="100dp"
                    android:layout_height="56dp"
                    android:background="@drawable/bg_input_field"
                    android:padding="5dp"
                    android:layout_marginEnd="10dp"/>
                    
                <LinearLayout
                    android:id="@+id/btnAddExp"
                    android:layout_width="56dp"
                    android:layout_height="56dp"
                    android:background="@drawable/bg_circle_btn"
                    android:gravity="center"
                    android:clickable="true"
                    android:focusable="true"
                    android:elevation="4dp">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp" android:src="@drawable/ic_custom_add" android:tint="@color/white"/>
                </LinearLayout>
            </LinearLayout>

            <LinearLayout
                android:id="@+id/containerExpenses"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:layout_marginTop="16dp"/>
        </LinearLayout>

        <!-- BOTÃO SALVAR (Gigante e Bonito) -->
        <androidx.appcompat.widget.AppCompatButton
            android:id="@+id/btnSave"
            android:layout_width="match_parent"
            android:layout_height="65dp"
            android:text="SALVAR FECHAMENTO"
            android:background="@drawable/bg_btn_gradient"
            android:textColor="#FFFFFF"
            android:textSize="16sp"
            android:textStyle="bold"
            android:elevation="8dp"
            android:stateListAnimator="@null"/>
            
        <Space android:layout_width="match_parent" android:layout_height="50dp"/>

    </LinearLayout>
</ScrollView>
"""
    write_file(f"{res_layout}/activity_add_daily.xml", layout_xml)

    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("🚀 Reforma Visual Concluída! O app agora está 'Glassmorphic'.")
    print("👉 Rode './gradlew assembleDebug' para ver a mágica.")

if __name__ == "__main__":
    main()


