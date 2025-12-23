import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Atualizado: {path}")

# --- 1. DEFINIR CORES (Azul Marca) ---
colors_xml = """
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#2563EB</color> <!-- Azul Primary -->
    <color name="ic_launcher_foreground">#FFFFFF</color> <!-- Branco -->
</resources>
"""

# --- 2. FUNDO DO ÍCONE (Background) ---
background_xml = """
<?xml version="1.0" encoding="utf-8"?>
<drawable xmlns:android="http://schemas.android.com/apk/res/android">
    <color android:color="@color/ic_launcher_background"/>
</drawable>
"""

# --- 3. FRENTE DO ÍCONE (Foreground - Volante Vetorial) ---
# Este é um desenho vetorial de um volante estilizado
foreground_xml = """
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    
    <!-- Centraliza o ícone (escala 0.6 para caber na zona segura) -->
    <group 
        android:scaleX="0.65"
        android:scaleY="0.65"
        android:translateX="4.2"
        android:translateY="4.2">
        
        <path
            android:fillColor="@color/ic_launcher_foreground"
            android:pathData="M12,2C6.48,2 2,6.48 2,12C2,17.52 6.48,22 12,22C17.52,22 22,17.52 22,12C22,6.48 17.52,2 12,2ZM12,4C15.81,4 19.09,6.66 20.08,10.21L15.35,11.85C14.77,10.74 13.51,10 12,10C10.49,10 9.23,10.74 8.65,11.85L3.92,10.21C4.91,6.66 8.19,4 12,4ZM12,20C8.19,20 4.91,17.34 3.92,13.79L8.65,12.15C8.89,12.63 9.24,13.05 9.66,13.36L8.03,17.88C9.2,18.59 10.56,19 12,19C13.44,19 14.8,18.59 15.97,17.88L14.34,13.36C14.76,13.05 15.11,12.63 15.35,12.15L20.08,13.79C19.09,17.34 15.81,20 12,20Z"/>
    </group>
</vector>
"""

# --- 4. ÍCONE ADAPTATIVO (Container) ---
# Isto combina o fundo com a frente e permite que o Android corte em círculo/quadrado
adaptive_icon_xml = """
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""

# --- 5. ATUALIZAR MANIFESTO ---
# Aponta para o novo mipmap/ic_launcher
manifest_content = """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="Motorista Pro"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service 
            android:name=".OcrService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="mediaProjection" />

    </application>

</manifest>
"""

print("--- Criando Ícone Profissional (Vector) ---")

# 1. Criar Definição de Cores
create_file("app/src/main/res/values/ic_colors.xml", colors_xml)

# 2. Criar Drawables (Fundo e Frente)
create_file("app/src/main/res/drawable/ic_launcher_background.xml", background_xml)
create_file("app/src/main/res/drawable/ic_launcher_foreground.xml", foreground_xml)

# 3. Criar Mipmaps (Definição Adaptativa)
# Criamos para 'anydpi-v26' que é o padrão para Android 8+
create_file("app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml", adaptive_icon_xml)
create_file("app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml", adaptive_icon_xml)

# 4. Atualizar Manifesto
create_file("app/src/main/AndroidManifest.xml", manifest_content)

print("\nÍcone atualizado para Volante Branco com Fundo Azul.")
print("Execute:")
print("1. git add .")
print("2. git commit -m 'UI: New App Icon'")
print("3. git push")


