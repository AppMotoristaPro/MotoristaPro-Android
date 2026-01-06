import os
import shutil
import subprocess
import re
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
PROJETO = "MotoristaPro-Android"
ARQUIVO_OCR = "app/src/main/java/com/motoristapro/android/OcrService.kt"
ARQUIVO_GRADLE = "app/build.gradle.kts"
PASTA_BACKUP = "backup_automatico"
ARQUIVO_RASTREADOR = ".version_tracker" # Mantém o controle da versão

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def log(msg, cor="36"): # 36 = Cyan
    print(f"\033[{cor}m[{PROJETO}] {msg}\033[0m")

def criar_backup(arquivos):
    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            nome_orig = os.path.basename(arquivo)
            destino = os.path.join(PASTA_BACKUP, f"{nome_orig}_{timestamp}.bak")
            shutil.copy2(arquivo, destino)
            log(f"Backup salvo: {destino}")

def git_automacao(mensagem):
    try:
        log("Executando Git Push...", "33")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", mensagem], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Git Push realizado com sucesso!", "32")
    except Exception as e:
        log(f"Erro no Git: {e}", "31")

def atualizar_versao_inteligente():
    """Lógica de versão incremental (v1 -> v2 -> v3...)"""
    if not os.path.exists(ARQUIVO_GRADLE): return None

    with open(ARQUIVO_GRADLE, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    padrao_code = r'(versionCode\s*=\s*)(\d+)'
    padrao_name = r'(versionName\s*=\s*")([^"]+)(")'
    
    # Se não tem o arquivo tracker, é a primeira vez -> Reseta para 1
    primeira_vez = not os.path.exists(ARQUIVO_RASTREADOR)
    
    if primeira_vez:
        novo_code = 1
        novo_name = "1.0"
        with open(ARQUIVO_RASTREADOR, 'w') as f: f.write("Track iniciado")
    else:
        # Incrementa
        match_code = re.search(padrao_code, conteudo)
        code_atual = int(match_code.group(2)) if match_code else 1
        novo_code = code_atual + 1
        
        match_name = re.search(padrao_name, conteudo)
        name_atual = match_name.group(2) if match_name else "1.0"
        try:
            pts = name_atual.split('.')
            pts[-1] = str(int(pts[-1]) + 1)
            novo_name = ".".join(pts)
        except:
            novo_name = name_atual + ".1"

    novo_conteudo = re.sub(padrao_code, fr'\g<1>{novo_code}', conteudo)
    novo_conteudo = re.sub(padrao_name, fr'\g<1>{novo_name}\g<3>', novo_conteudo)
    
    with open(ARQUIVO_GRADLE, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
        
    return novo_code

# ==============================================================================
# CORREÇÃO DO ERRO DE COMPILAÇÃO
# ==============================================================================

def corrigir_erro_kotlin():
    if not os.path.exists(ARQUIVO_OCR):
        log(f"Arquivo não encontrado: {ARQUIVO_OCR}", "31")
        return False

    criar_backup([ARQUIVO_OCR, ARQUIVO_GRADLE])

    with open(ARQUIVO_OCR, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # --- Lista de Correções (RegEx String Escaping) ---
    # O erro é usar "\s" ou "\." direto. Precisa ser "\\s" e "\\."
    
    correcoes = [
        # Caso 1: Preço com \s* e \.
        (r'(?:r\$|rs)\s*([0-9]+(?:\.[0-9]{2})?)', r'(?:r$|rs)\\s*([0-9]+(?:\\.[0-9]{2})?)'),
        
        # Caso 2: Preço isolado com \.
        (r'^([0-9]+(?:\.[0-9]{2}))$', r'^([0-9]+(?:\\.[0-9]{2}))$'),
        
        # Caso 3: Distância com \. e \s*
        (r'\\(?([0-9]+(?:\.[0-9]+)?)\s*(km|m)\\)?', r'\\(?([0-9]+(?:\\.[0-9]+)?)\\s*(km|m)\\)?'),
        
        # Caso 4: Horas com \s*
        (r'(\d+)\s*(?:h|hr|hrs|hora|horas)\b', r'(\d+)\\s*(?:h|hr|hrs|hora|horas)\\b'),
        
        # Caso 5: Minutos com \s*
        (r'(\d+)\s*(?:min|minutos|m1n|m1ns|mins)', r'(\d+)\\s*(?:min|minutos|m1n|m1ns|mins)')
    ]

    novo_conteudo = conteudo
    contador = 0
    
    for errado, correto in correcoes:
        # Usamos replace simples de string (não regex) para ser exato, 
        # mas como definimos as strings acima com raw (r''), temos que cuidar.
        # Vamos fazer replace literal das partes problemáticas.
        
        # Fix \s* -> \\s* (globalmente nos padrões Pattern.compile se possível, ou substituição direta)
        # Como o erro é específico, vamos substituir os trechos conhecidos.
        
        if errado in novo_conteudo:
            novo_conteudo = novo_conteudo.replace(errado, correto)
            contador += 1
            
    # Fallback: Se os replaces exatos falharem por algum caractere diferente, 
    # forçamos a troca de "\s*" por "\\s*" e "\." por "\\." APENAS nas linhas de Pattern.compile
    lines = novo_conteudo.split('\n')
    final_lines = []
    for line in lines:
        if "Pattern.compile" in line:
            # Corrige \s que não esteja escapado
            if r"\s" in line and r"\\s" not in line:
                line = line.replace(r"\s", r"\\s")
                contador += 1
            # Corrige \. que não esteja escapado (cuidado para não quebrar outros escapes)
            if r"(?:\." in line: # Padrão específico do seu código
                line = line.replace(r"(?:\.", r"(?:\\.")
                contador += 1
        final_lines.append(line)
    
    novo_conteudo = "\n".join(final_lines)

    if contador > 0:
        with open(ARQUIVO_OCR, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        log(f"Foram aplicadas correções de sintaxe Kotlin em {contador} locais.", "32")
        return True
    else:
        log("Nenhuma correção necessária ou padrão não encontrado.", "33")
        return False

# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    print("-" * 50)
    log("Iniciando correção de compilação...", "36")
    
    corrigido = corrigir_erro_kotlin()
    
    if corrigido:
        nova_v = atualizar_versao_inteligente()
        if nova_v:
            git_automacao(f"Fix Erro Compilacao Kotlin (Regex Escapes) - v{nova_v}")
        else:
            log("Erro ao atualizar versão.", "31")
    else:
        log("Nada foi alterado.", "33")
    
    print("-" * 50)


