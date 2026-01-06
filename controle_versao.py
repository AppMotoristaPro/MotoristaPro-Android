import os
import shutil
import subprocess
import re
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
PROJETO = "MotoristaPro-Android"
ARQUIVO_ALVO = "app/build.gradle.kts"
# Este arquivo oculto servirá de "memória" para o script saber se já rodou antes
ARQUIVO_RASTREADOR = ".version_tracker" 
PASTA_BACKUP = "backup_automatico"

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def log(msg, cor="36"): # 36 = Cyan
    print(f"\033[{cor}m[{PROJETO}] {msg}\033[0m")

def criar_backup(arquivo):
    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_orig = os.path.basename(arquivo)
    destino = os.path.join(PASTA_BACKUP, f"{nome_orig}_{timestamp}.bak")
    
    if os.path.exists(arquivo):
        shutil.copy2(arquivo, destino)
        log(f"Backup salvo em: {destino}")

def git_automacao(mensagem):
    try:
        log("Executando Git Push...", "33") # Amarelo
        # Adiciona tudo, inclusive o .version_tracker para persistir o estado
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", mensagem], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Git Push realizado com sucesso!", "32") # Verde
    except Exception as e:
        log(f"Erro no Git: {e}", "31") # Vermelho

# ==============================================================================
# LÓGICA PRINCIPAL
# ==============================================================================

def atualizar_versao():
    if not os.path.exists(ARQUIVO_ALVO):
        log(f"Arquivo não encontrado: {ARQUIVO_ALVO}", "31")
        return

    # 1. Realizar Backup antes de mexer
    criar_backup(ARQUIVO_ALVO)

    # 2. Ler o arquivo gradle
    with open(ARQUIVO_ALVO, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Regex para encontrar os valores
    padrao_code = r'(versionCode\s*=\s*)(\d+)'
    padrao_name = r'(versionName\s*=\s*")([^"]+)(")'

    # 3. Verificar se é a PRIMEIRA VEZ
    primeira_vez = not os.path.exists(ARQUIVO_RASTREADOR)
    
    novo_code = 0
    novo_name = ""
    msg_commit = ""

    if primeira_vez:
        log("--- PRIMEIRA EXECUÇÃO DETECTADA ---", "35") # Magenta
        log("Reiniciando versão para 1.0")
        
        novo_code = 1
        novo_name = "1.0"
        msg_commit = "Reset de Versao (Play Protect Fix) - v1.0"
        
        # Cria o arquivo rastreador para a próxima vez saber que não é a primeira
        with open(ARQUIVO_RASTREADOR, 'w') as f:
            f.write(f"Iniciado em: {datetime.now()}\n")
            f.write("NÃO APAGUE ESTE ARQUIVO SE QUISER MANTER A CONTAGEM SEQUENCIAL.")
            
    else:
        log("--- EXECUÇÃO RECORRENTE ---", "35")
        
        # Pega o código atual no arquivo
        match_code = re.search(padrao_code, conteudo)
        if match_code:
            code_atual = int(match_code.group(2))
            novo_code = code_atual + 1
        else:
            log("Não foi possível ler o versionCode atual. Forçando 1.", "31")
            novo_code = 1

        # Lógica para o nome da versão (ex: 1.0 -> 1.1)
        match_name = re.search(padrao_name, conteudo)
        if match_name:
            name_atual = match_name.group(2)
            try:
                # Tenta incrementar o último número após o ponto
                partes = name_atual.split('.')
                ultimo = int(partes[-1])
                partes[-1] = str(ultimo + 1)
                novo_name = ".".join(partes)
            except:
                novo_name = f"{name_atual}.1"
        else:
            novo_name = "1.0"
            
        log(f"Subindo versão: {novo_code} ({novo_name})")
        msg_commit = f"Bump version code: {novo_code}"

    # 4. Aplicar alterações no texto
    novo_conteudo = re.sub(padrao_code, fr'\g<1>{novo_code}', conteudo)
    novo_conteudo = re.sub(padrao_name, fr'\g<1>{novo_name}\g<3>', novo_conteudo)

    # 5. Salvar arquivo
    with open(ARQUIVO_ALVO, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
        
    return msg_commit

if __name__ == "__main__":
    msg = atualizar_versao()
    if msg:
        git_automacao(msg)
    
    log("Processo finalizado. O script foi mantido.", "32")


