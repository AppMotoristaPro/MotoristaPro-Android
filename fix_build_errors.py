import os
import shutil
import subprocess
import re

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
PROJETO = "MotoristaPro-Android"
DIR_MAIN = "app/src/main/java/com/motoristapro/android"
FILE_OCR = os.path.join(DIR_MAIN, "OcrService.kt")
FILE_MAIN = os.path.join(DIR_MAIN, "MainActivity.kt")
FILE_GRADLE = "app/build.gradle.kts"

# ==============================================================================
# LOGICA DE CORREÇÃO
# ==============================================================================

def log(msg): print(f"\033[36m[{PROJETO}] {msg}\033[0m")

def fix_ocr_service():
    if not os.path.exists(FILE_OCR): return
    with open(FILE_OCR, 'r', encoding='utf-8') as f: content = f.read()
    
    # 1. Corrigir Escapes Ilegais em Regex
    # O erro é usar "\s" ou "\." em string normal. Precisa ser "\\s" ou "\\."
    
    # Lista de padrões problemáticos identificados nos logs e seus consertos
    replacements = [
        # Preço: (?:r\$|rs)\s*([0-9]+(?:\.[0-9]{2})?)
        (r'(?:r\$|rs)\s*([0-9]+(?:\.[0-9]{2})?)', r'(?:r\\$|rs)\\s*([0-9]+(?:\\.[0-9]{2})?)'),
        
        # Preço 2: ^([0-9]+(?:\.[0-9]{2}))$
        (r'^([0-9]+(?:\.[0-9]{2}))$', r'^([0-9]+(?:\\.[0-9]{2}))$'),
        
        # Distância: \(?([0-9]+(?:\.[0-9]+)?)\s*(km|m)\)?
        (r'\(?([0-9]+(?:\.[0-9]+)?)\s*(km|m)\)?', r'\\(?([0-9]+(?:\\.[0-9]+)?)\\s*(km|m)\\)?'),
        
        # Tempo 1: \d{1,2}:\d{2} (substituição de string, precisa de escape duplo tbm)
        (r'Regex("\\d{1,2}:\\d{2}")', r'Regex("\\\\d{1,2}:\\\\d{2}")'),
        
        # Tempo 2: (\d+)\s*(?:h|hr|hrs|hora|horas)\b
        (r'(\d+)\s*(?:h|hr|hrs|hora|horas)\\b', r'(\\d+)\\s*(?:h|hr|hrs|hora|horas)\\b'),
        
        # Tempo 3: (\d+)\s*(?:min|minutos|m1n|m1ns|mins)
        (r'(\d+)\s*(?:min|minutos|m1n|m1ns|mins)', r'(\\d+)\\s*(?:min|minutos|m1n|m1ns|mins)'),
        
        # Fix genérico para strings que sobraram com \s ou \. inválidos dentro de Pattern.compile
        # Cuidado para não quebrar strings normais. Focamos nas linhas de Pattern.compile
    ]

    new_content = content
    
    # Aplica substituições específicas primeiro (String literals no código)
    # Como estamos manipulando código fonte com strings, é delicado.
    # Vamos substituir as linhas inteiras conhecidas.
    
    # Preço
    new_content = new_content.replace(
        'Pattern.compile("(?:r\$|rs)\s*([0-9]+(?:\.[0-9]{2})?)")', 
        'Pattern.compile("(?:r\\\\$|rs)\\\\s*([0-9]+(?:\\\\.[0-9]{2})?)")'
    )
    new_content = new_content.replace(
        'Pattern.compile("^([0-9]+(?:\.[0-9]{2}))$")', 
        'Pattern.compile("^([0-9]+(?:\\\\.[0-9]{2}))$")'
    )
    
    # Distância
    new_content = new_content.replace(
        'Pattern.compile("\\(?([0-9]+(?:\.[0-9]+)?)\\s*(km|m)\\)?")', 
        'Pattern.compile("\\\\(?([0-9]+(?:\\\\.[0-9]+)?)\\\\s*(km|m)\\\\)?")'
    )
    
    # Tempo (Regex Replace)
    new_content = new_content.replace(
        'cleanText.replace(Regex("\\d{1,2}:\\d{2}"), " ")',
        'cleanText.replace(Regex("\\\\d{1,2}:\\\\d{2}"), " ")'
    )
    
    # Horas
    new_content = new_content.replace(
        'Pattern.compile("(\\d+)\\s*(?:h|hr|hrs|hora|horas)\\b")',
        'Pattern.compile("(\\\\d+)\\\\s*(?:h|hr|hrs|hora|horas)\\\\b")'
    )
    
    # Minutos
    new_content = new_content.replace(
        'Pattern.compile("(\\d+)\\s*(?:min|minutos|m1n|m1ns|mins)(?!in|etro|l|e|a|o)")',
        'Pattern.compile("(\\\\d+)\\\\s*(?:min|minutos|m1n|m1ns|mins)(?!in|etro|l|e|a|o)")'
    )

    if new_content != content:
        with open(FILE_OCR, 'w', encoding='utf-8') as f: f.write(new_content)
        log("OcrService.kt: Escapes de Regex corrigidos.")
    else:
        log("OcrService.kt: Nenhuma alteração de Regex necessária (ou falha no match).")

def fix_main_activity():
    if not os.path.exists(FILE_MAIN): return
    with open(FILE_MAIN, 'r', encoding='utf-8') as f: content = f.read()
    
    # 1. Fix Nullable Intent no onShowFileChooser
    # Erro: Type mismatch: inferred type is Intent? but Intent was expected
    old_block = """val intent = fileChooserParams?.createIntent()
                try {
                    startActivityForResult(intent, FILE_CHOOSER_RESULT_CODE)
                }"""
    
    new_block = """val intent = fileChooserParams?.createIntent()
                if (intent != null) {
                    try {
                        startActivityForResult(intent, FILE_CHOOSER_RESULT_CODE)
                    } catch (e: Exception) {
                        fileUploadCallback = null
                        return false
                    }
                } else {
                    fileUploadCallback = null
                    return false
                }"""
    
    # Normaliza espaços para facilitar o replace
    content_normalized = re.sub(r'\s+', ' ', content)
    old_block_normalized = re.sub(r'\s+', ' ', old_block)
    
    if old_block_normalized in content_normalized:
        # Se achou, tenta substituir no original usando âncoras
        # Como replace exato é difícil com identação, vamos reescrever o método onShowFileChooser
        
        # Regex para capturar o método onShowFileChooser inteiro
        pattern = r'override fun onShowFileChooser.*?return true\s+}'
        
        # Novo método completo
        new_method = """override fun onShowFileChooser(webView: WebView?, filePathCallback: ValueCallback<Array<Uri>>?, fileChooserParams: FileChooserParams?): Boolean {
                if (fileUploadCallback != null) {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = null
                }
                fileUploadCallback = filePathCallback

                val intent = fileChooserParams?.createIntent()
                if (intent != null) {
                    try {
                        startActivityForResult(intent, FILE_CHOOSER_RESULT_CODE)
                    } catch (e: Exception) {
                        fileUploadCallback = null
                        return false
                    }
                } else {
                    fileUploadCallback = null
                    return false
                }
                return true
            }"""
        
        content = re.sub(pattern, new_method, content, flags=re.DOTALL)
        log("MainActivity.kt: Lógica de Upload (Intent Nulo) corrigida.")

    # 2. Fix Imports de Acessibilidade (Unresolved reference)
    # Garante que os imports existam
    imports_needed = [
        "import android.view.accessibility.AccessibilityManager",
        "import android.accessibilityservice.AccessibilityServiceInfo"
    ]
    
    for imp in imports_needed:
        if imp not in content:
            content = content.replace("import android.Manifest", f"{imp}\nimport android.Manifest")
            log(f"MainActivity.kt: Import adicionado: {imp}")

    with open(FILE_MAIN, 'w', encoding='utf-8') as f: f.write(content)

def increment_version():
    if not os.path.exists(FILE_GRADLE): return
    with open(FILE_GRADLE, 'r', encoding='utf-8') as f: content = f.read()
    
    match = re.search(r'(versionCode\s*=\s*)(\d+)', content)
    if match:
        new_ver = int(match.group(2)) + 1
        content = re.sub(r'(versionCode\s*=\s*)(\d+)', fr'\g<1>{new_ver}', content)
        with open(FILE_GRADLE, 'w', encoding='utf-8') as f: f.write(content)
        log(f"Versão do App: {new_ver}")

if __name__ == "__main__":
    fix_ocr_service()
    fix_main_activity()
    increment_version()
    
    os.system("git add .")
    os.system('git commit -m "Fix: Erros de Compilacao (Regex Escapes + Null Intent)"')
    os.system("git push")


