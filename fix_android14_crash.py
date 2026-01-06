import os
import shutil
import subprocess
import re
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
PROJETO = "MotoristaPro-Android"
DIRETORIO_BACKUP = "backup_automatico"
ARQUIVO_GRADLE = "app/build.gradle.kts"
ARQUIVO_OCR = "app/src/main/java/com/motoristapro/android/OcrService.kt"
ARQUIVO_MAIN = "app/src/main/java/com/motoristapro/android/MainActivity.kt"

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def log(msg, cor="36"): # 36 = Cyan
    print(f"\033[{cor}m[{PROJETO}] {msg}\033[0m")

def criar_backup(arquivos):
    if not os.path.exists(DIRETORIO_BACKUP):
        os.makedirs(DIRETORIO_BACKUP)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            nome_orig = os.path.basename(arquivo)
            destino = os.path.join(DIRETORIO_BACKUP, f"{nome_orig}_{timestamp}.bak")
            shutil.copy2(arquivo, destino)
            log(f"Backup salvo: {destino}")

def atualizar_versao():
    """Incrementa versionCode para gerar novo APK"""
    if not os.path.exists(ARQUIVO_GRADLE): return

    with open(ARQUIVO_GRADLE, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    match_code = re.search(r'(versionCode\s*=\s*)(\d+)', conteudo)
    if match_code:
        novo_code = int(match_code.group(2)) + 1
        conteudo = re.sub(r'(versionCode\s*=\s*)(\d+)', fr'\g<1>{novo_code}', conteudo)
        
        # Atualiza versionName
        match_name = re.search(r'(versionName\s*=\s*")([^"]+)(")', conteudo)
        if match_name:
            nome_atual = match_name.group(2)
            try:
                pts = nome_atual.split('.')
                pts[-1] = str(int(pts[-1]) + 1)
                novo_nome = ".".join(pts)
            except:
                novo_nome = nome_atual + ".1"
            conteudo = re.sub(r'(versionName\s*=\s*")([^"]+)(")', fr'\g<1>{novo_nome}\g<3>', conteudo)

        with open(ARQUIVO_GRADLE, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        log(f"Versão atualizada para {novo_code} ({novo_nome})", "32")
        return f"Fix Android 14 Crash - v{novo_code}"
    return "Fix Android 14 Crash"

def git_push(msg):
    try:
        log("Executando Git Push...", "33")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Git Push Concluído.", "32")
    except:
        log("Erro no Git Push.", "31")

# ==============================================================================
# LÓGICA DE CORREÇÃO (ANDROID 14 RECEIVER)
# ==============================================================================

def corrigir_receivers():
    # 1. Lista de arquivos para backup e correção
    arquivos_alvo = [ARQUIVO_OCR, ARQUIVO_MAIN]
    criar_backup(arquivos_alvo)

    for arquivo in arquivos_alvo:
        if not os.path.exists(arquivo): continue
        
        log(f"Processando {arquivo}...", "34")
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        modificado = False
        
        # A. Se já tiver a verificação de SDK, não faz nada (para evitar duplicação)
        if "RECEIVER_NOT_EXPORTED" in conteudo and "Build.VERSION.SDK_INT" in conteudo:
            log(f"  -> Já parece corrigido.", "33")
            continue

        # B. Substituição Inteligente
        # Regex captura: (registerReceiver)\(([^,]+),\s*([^)]+)\)
        
        regex_receiver = r'registerReceiver\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)'
        
        def replacer(match):
            receiver = match.group(1).strip()
            filter_obj = match.group(2).strip()
            
            # Se já tiver Context.RECEIVER..., ignora
            if "Context.RECEIVER" in filter_obj:
                return match.group(0)
            
            # Gera o bloco de código compatível
            return f"""if (Build.VERSION.SDK_INT >= 33) {{
            registerReceiver({receiver}, {filter_obj}, Context.RECEIVER_EXPORTED)
        }} else {{
            registerReceiver({receiver}, {filter_obj})
        }}"""

        novo_conteudo = re.sub(regex_receiver, replacer, conteudo)
        
        if novo_conteudo != conteudo:
            # Garante que Context e Build estão importados
            if "import android.content.Context" not in novo_conteudo:
                novo_conteudo = novo_conteudo.replace("package com.motoristapro.android", "package com.motoristapro.android\n\nimport android.content.Context")
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(novo_conteudo)
            log(f"  -> Correção aplicada com sucesso!", "32")
            modificado = True
        else:
            log(f"  -> Nenhuma ocorrência de registerReceiver simples encontrada.", "33")

    return True

# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    print("-" * 50)
    log("Iniciando correção de Crash (Android 14)...", "36")
    
    corrigir_receivers()
    msg_git = atualizar_versao()
    
    if msg_git:
        git_push(msg_git)
    
    # Auto-destruição
    try:
        os.remove(__file__)
        log("Script removido.", "32")
    except:
        pass
        
    print("-" * 50)



