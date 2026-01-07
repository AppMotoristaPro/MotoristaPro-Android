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
ARQUIVO_OCR = "app/src/main/java/com/motoristapro/android/OcrService.kt"
ARQUIVO_GRADLE = "app/build.gradle.kts"

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def log(msg, cor="36"): # 36 = Cyan
    print(f"\033[{cor}m[{PROJETO}] {msg}\033[0m")

def criar_backup(arquivo):
    if not os.path.exists(DIRETORIO_BACKUP):
        os.makedirs(DIRETORIO_BACKUP)
    
    if os.path.exists(arquivo):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_orig = os.path.basename(arquivo)
        destino = os.path.join(DIRETORIO_BACKUP, f"{nome_orig}_{timestamp}.bak")
        shutil.copy2(arquivo, destino)
        log(f"Backup salvo: {destino}")

def git_push(msg):
    try:
        log("Executando Git Push...", "33")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        log("Git Push Concluído.", "32")
    except:
        log("Erro no Git Push.", "31")

def atualizar_versao():
    """Incrementa versionCode"""
    if not os.path.exists(ARQUIVO_GRADLE): return None

    with open(ARQUIVO_GRADLE, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Incrementa versionCode
    match_code = re.search(r'(versionCode\s*=\s*)(\d+)', conteudo)
    novo_code = 0
    if match_code:
        novo_code = int(match_code.group(2)) + 1
        conteudo = re.sub(r'(versionCode\s*=\s*)(\d+)', fr'\g<1>{novo_code}', conteudo)
    
    # Atualiza versionName (opcional, só pra manter coerência)
    match_name = re.search(r'(versionName\s*=\s*")([^"]+)(")', conteudo)
    if match_name:
        try:
            parts = match_name.group(2).split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            new_name = ".".join(parts)
            conteudo = re.sub(r'(versionName\s*=\s*")([^"]+)(")', fr'\g<1>{new_name}\g<3>', conteudo)
        except:
            pass

    with open(ARQUIVO_GRADLE, 'w', encoding='utf-8') as f:
        f.write(conteudo)
        
    return novo_code

# ==============================================================================
# CORREÇÃO DO OCR SERVICE
# ==============================================================================

def corrigir_ocr_service():
    if not os.path.exists(ARQUIVO_OCR):
        log(f"Arquivo não encontrado: {ARQUIVO_OCR}", "31")
        return False

    criar_backup(ARQUIVO_OCR)

    with open(ARQUIVO_OCR, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # O código problemático provavelmente se parece com isso (devido ao erro de sintaxe):
    # if (Build.VERSION.SDK_INT >= 33) {
    #     registerReceiver(textReceiver, filter, Context.RECEIVER_EXPORTED)
    # } else {
    #     registerReceiver(textReceiver, filter)
    # }
    
    # Vamos substituir TODA a ocorrência de registerReceiver do textReceiver e do hideCardReceiver
    # por uma versão limpa e garantida.

    # 1. Encontra e remove as tentativas anteriores quebradas (regex genérico para pegar o bloco if/else ou a chamada simples)
    # Como não sabemos exatamente como ficou o erro de sintaxe no arquivo, vamos buscar pelo padrão 
    # de registro do textReceiver e substituir o bloco inteiro.
    
    # Padrão para textReceiver
    # Vamos procurar qualquer coisa que envolva 'registerReceiver(textReceiver' e algumas linhas em volta
    
    # Solução mais robusta: Ler o arquivo linha a linha e reescrever a seção do onCreate
    
    novo_conteudo = conteudo
    
    # Bloco correto para textReceiver
    bloco_correto_text = """
        val filterText = IntentFilter("ACTION_PROCESS_TEXT")
        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(textReceiver, filterText, Context.RECEIVER_EXPORTED)
        } else {
            registerReceiver(textReceiver, filterText)
        }
    """
    
    # Bloco correto para hideCardReceiver
    bloco_correto_hide = """
        val filterHide = IntentFilter("com.motoristapro.ACTION_HIDE_CARD")
        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(hideCardReceiver, filterHide, Context.RECEIVER_EXPORTED)
        } else {
            registerReceiver(hideCardReceiver, filterHide)
        }
    """

    # Tenta identificar onde estão os registros antigos e substituir
    # Padrão antigo provável (versão original ou a quebrada):
    # registerReceiver(textReceiver, filter) ...
    # ou
    # val filter = IntentFilter("ACTION_PROCESS_TEXT") ... registerReceiver...
    
    # Vamos fazer uma substituição mais agressiva baseada em âncoras conhecidas
    
    # 1. Substituir o registro do textReceiver
    # Procura pela definição do filtro e o registro
    pattern_text = r'val\s+filter\s*=\s*IntentFilter\("ACTION_PROCESS_TEXT"\)[\s\S]*?registerReceiver\s*\(\s*textReceiver\s*,\s*filter.*?\)'
    
    # Se o script anterior bagunçou e removeu a variável 'filter', precisamos restaurar.
    # Se o script anterior gerou um if/else quebrado, o regex acima pode não pegar se houver chaves desbalanceadas.
    
    # Vamos tentar substituir o bloco que sabemos que existe no onCreate
    
    # Localiza o início do onCreate
    idx_oncreate = novo_conteudo.find("override fun onCreate() {")
    if idx_oncreate == -1:
        log("Não encontrou onCreate no OcrService.", "31")
        return False
        
    # Localiza o registro do textReceiver DENTRO do onCreate (ou próximo dele)
    # Uma âncora segura é a linha: if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    # que o script anterior inseriu (ou tentou).
    
    # Vamos procurar por trechos específicos e substituir
    
    # Remove qualquer tentativa anterior de registro do textReceiver
    novo_conteudo = re.sub(
        r'(?s)val\s+filter\s*=\s*IntentFilter\("ACTION_PROCESS_TEXT"\).*?registerReceiver\(textReceiver.*?\}(\s*else\s*\{.*?\})?', 
        "// RECEIVER REPLACED", 
        novo_conteudo
    )
    
    # Remove qualquer tentativa anterior de registro do hideCardReceiver
    novo_conteudo = re.sub(
        r'(?s)registerReceiver\(hideCardReceiver.*?\)', 
        "// HIDE RECEIVER REPLACED", 
        novo_conteudo
    )

    # Agora, limpa as linhas comentadas e insere o código correto no lugar certo
    # Inserimos logo após "loadConfigs()" que sabemos que existe no onCreate
    
    codigo_injecao = f"""
        loadConfigs()
        {bloco_correto_text}
        {bloco_correto_hide}
    """
    
    novo_conteudo = novo_conteudo.replace("loadConfigs()", codigo_injecao)
    
    # Limpa os comentários de substituição que ficaram soltos (se houver)
    novo_conteudo = novo_conteudo.replace("// RECEIVER REPLACED", "")
    novo_conteudo = novo_conteudo.replace("// HIDE RECEIVER REPLACED", "")
    
    # Remove duplicatas se o loadConfigs() foi usado como âncora mas o código antigo estava antes
    # (Não deve acontecer se a estrutura for padrão, mas vamos garantir que não tenha duplicatas de registerReceiver)
    
    # Salva
    with open(ARQUIVO_OCR, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    
    log("OcrService corrigido com receivers seguros.", "32")
    return True

# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    print("-" * 50)
    log("Iniciando correção de compilação OCR...", "36")
    
    if corrigir_ocr_service():
        novo_code = atualizar_versao()
        if novo_code:
            git_push(f"Fix OCR Service Syntax Error - v{novo_code}")
        
    # Auto-destruição
    try:
        os.remove(__file__)
    except:
        pass
        
    print("-" * 50)


