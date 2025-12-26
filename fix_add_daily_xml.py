import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Layout Corrigido: {path}")

def main():
    print("🚑 Corrigindo activity_add_daily.xml (layout_width missing)...")
    
    path = "app/src/main/res/layout/activity_add_daily.xml"
    
    # XML Blindado (Todas as tags com width/height explícitos)
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
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="DATA DO TRABALHO"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="@color/text_secondary"/>
                
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
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="FATURAMENTO TOTAL"
                android:textSize="10sp"
                android:textStyle="bold"
                android:textColor="@color/text_secondary"/>
                
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
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Detalhar (Opcional)"
                android:textSize="11sp"
                android:layout_marginBottom="10dp"
                android:textColor="@color/text_secondary"/>

            <LinearLayout 
                android:layout_width="match_parent" 
                android:layout_height="wrap_content" 
                android:orientation="horizontal" 
                android:weightSum="2" 
                android:layout_marginBottom="10dp">
                
                <EditText 
                    android:id="@+id/etUber" 
                    android:layout_width="0dp" 
                    android:layout_height="50dp" 
                    android:layout_weight="1" 
                    android:hint="Uber" 
                    android:inputType="numberDecimal" 
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp" 
                    android:layout_marginEnd="8dp"/>
                    
                <EditText 
                    android:id="@+id/et99" 
                    android:layout_width="0dp" 
                    android:layout_height="50dp" 
                    android:layout_weight="1" 
                    android:hint="99 Pop" 
                    android:inputType="numberDecimal" 
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp" 
                    android:layout_marginStart="8dp"/>
            </LinearLayout>
            
            <LinearLayout 
                android:layout_width="match_parent" 
                android:layout_height="wrap_content" 
                android:orientation="horizontal" 
                android:weightSum="2">
                
                <EditText 
                    android:id="@+id/etPart" 
                    android:layout_width="0dp" 
                    android:layout_height="50dp" 
                    android:layout_weight="1" 
                    android:hint="Particular" 
                    android:inputType="numberDecimal" 
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp" 
                    android:layout_marginEnd="8dp"/>
                    
                <EditText 
                    android:id="@+id/etOutros" 
                    android:layout_width="0dp" 
                    android:layout_height="50dp" 
                    android:layout_weight="1" 
                    android:hint="Outros" 
                    android:inputType="numberDecimal" 
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp" 
                    android:layout_marginStart="8dp"/>
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
            
            <TextView 
                android:layout_width="wrap_content" 
                android:layout_height="wrap_content" 
                android:text="DESPESAS DO DIA" 
                android:textSize="10sp" 
                android:textStyle="bold" 
                android:textColor="@color/danger"/>
            
            <LinearLayout 
                android:layout_width="match_parent" 
                android:layout_height="wrap_content" 
                android:orientation="horizontal" 
                android:weightSum="3" 
                android:layout_marginTop="15dp">
                
                <LinearLayout 
                    android:orientation="vertical" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:paddingEnd="5dp"
                    android:layout_height="wrap_content">
                    <TextView 
                        android:layout_width="wrap_content" 
                        android:layout_height="wrap_content" 
                        android:text="Combustível" 
                        android:textSize="10sp" 
                        android:layout_marginBottom="5dp"/>
                    <EditText 
                        android:id="@+id/etComb" 
                        android:layout_width="match_parent" 
                        android:layout_height="45dp" 
                        android:inputType="numberDecimal" 
                        android:background="@drawable/bg_input_field" 
                        android:padding="10dp" 
                        android:textSize="13sp"/>
                </LinearLayout>
                
                <LinearLayout 
                    android:orientation="vertical" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:paddingStart="2dp" 
                    android:paddingEnd="2dp"
                    android:layout_height="wrap_content">
                    <TextView 
                        android:layout_width="wrap_content" 
                        android:layout_height="wrap_content" 
                        android:text="Alimentação" 
                        android:textSize="10sp" 
                        android:layout_marginBottom="5dp"/>
                    <EditText 
                        android:id="@+id/etAlim" 
                        android:layout_width="match_parent" 
                        android:layout_height="45dp" 
                        android:inputType="numberDecimal" 
                        android:background="@drawable/bg_input_field" 
                        android:padding="10dp" 
                        android:textSize="13sp"/>
                </LinearLayout>
                
                <LinearLayout 
                    android:orientation="vertical" 
                    android:layout_width="0dp" 
                    android:layout_weight="1" 
                    android:paddingStart="5dp"
                    android:layout_height="wrap_content">
                    <TextView 
                        android:layout_width="wrap_content" 
                        android:layout_height="wrap_content" 
                        android:text="Manutenção" 
                        android:textSize="10sp" 
                        android:layout_marginBottom="5dp"/>
                    <EditText 
                        android:id="@+id/etManu" 
                        android:layout_width="match_parent" 
                        android:layout_height="45dp" 
                        android:inputType="numberDecimal" 
                        android:background="@drawable/bg_input_field" 
                        android:padding="10dp" 
                        android:textSize="13sp"/>
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
            
            <LinearLayout 
                android:orientation="vertical" 
                android:layout_width="0dp" 
                android:layout_weight="1" 
                android:paddingEnd="10dp"
                android:layout_height="wrap_content">
                <TextView 
                    android:layout_width="wrap_content" 
                    android:layout_height="wrap_content" 
                    android:text="KM TOTAL" 
                    android:textSize="10sp" 
                    android:textStyle="bold" 
                    android:textColor="@color/text_secondary" 
                    android:layout_marginBottom="5dp"/>
                <EditText 
                    android:id="@+id/etKm" 
                    android:layout_width="match_parent" 
                    android:layout_height="50dp" 
                    android:inputType="numberDecimal" 
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp"/>
            </LinearLayout>
            
            <LinearLayout 
                android:orientation="vertical" 
                android:layout_width="0dp" 
                android:layout_weight="1" 
                android:paddingStart="10dp"
                android:layout_height="wrap_content">
                <TextView 
                    android:layout_width="wrap_content" 
                    android:layout_height="wrap_content" 
                    android:text="HORAS" 
                    android:textSize="10sp" 
                    android:textStyle="bold" 
                    android:textColor="@color/text_secondary" 
                    android:layout_marginBottom="5dp"/>
                <EditText 
                    android:id="@+id/etHoras" 
                    android:layout_width="match_parent" 
                    android:layout_height="50dp" 
                    android:inputType="numberDecimal" 
                    android:background="@drawable/bg_input_field" 
                    android:padding="12dp"/>
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
    with open(path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    # Incrementa versão
    os.system("python3 auto_version.py")
    
    print("✅ XML Corrigido! Tente compilar.")

if __name__ == "__main__":
    main()


