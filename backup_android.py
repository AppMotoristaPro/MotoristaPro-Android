import os
import shutil

# ================= CONFIGURAÇÕES =================
DIRETORIO_RAIZ = "."
PASTA_DESTINO = "Backup_Android"
TAMANHO_MAX = 200 * 1024  # 200 KB

# Extensões focadas em desenvolvimento Android
EXTENSOES_PERMITIDAS = {
    # Código Fonte
    '.kt', '.java',
    # Recursos e Layouts
    '.xml',
    # Configurações e Build
    '.kts', '.gradle', '.properties', '.json',
    # Documentação
    '.md', '.txt'
}

# Pastas para IGNORAR (Builds, Caches, Git)
PASTAS_IGNORADAS = {
    'build', '.gradle', '.idea', '.git', 
    'venv', '__pycache__', 'node_modules',
    'Backup', 'BackupOtimizado', 'BackupFinal', 
    'Backup_Estruturado', 'Backup_Android'
}

# Arquivos Binários ou Desnecessários para IGNORAR
ARQUIVOS_IGNORADOS = {
    'motorista.jks', 'release.keystore', 'debug.keystore',
    'gradlew', 'gradlew.bat', 'local.properties',
    'backup_android.py', 'fazer_backup.py'
}

def limpar_nome_pasta(caminho_pasta):
    """Transforma './app/src/main' em 'app_src_main'."""
    if caminho_pasta == "." or caminho_pasta == "./":
        return "RAIZ_DO_PROJETO"
    
    # Remove ./ e substitui barras por underlines
    limpo = caminho_pasta.replace("./", "").replace(".", "").replace(os.sep, "_")
    
    # Remove duplicidade de underlines e underlines iniciais
    while "__" in limpo:
        limpo = limpo.replace("__", "_")
    if limpo.startswith("_"): 
        limpo = limpo[1:]
        
    return limpo

def deve_processar(nome_arquivo):
    if nome_arquivo in ARQUIVOS_IGNORADOS: return False
    
    # Arquivos sem extensão exatos permitidos (ex: Proguard, mas geralmente tem ext)
    if nome_arquivo in EXTENSOES_PERMITIDAS: return True
    
    _, ext = os.path.splitext(nome_arquivo)
    
    # Ignora imagens (png, jpg, webp) explicitamente se não estiverem na lista permitida
    if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.ico']:
        return False
        
    return ext.lower() in EXTENSOES_PERMITIDAS

def formatar_cabecalho(caminho_arquivo):
    linha = "=" * 80
    return f"\n{linha}\nARQUIVO: {caminho_arquivo}\n{linha}\n"

def realizar_backup():
    # Prepara a pasta de destino
    if os.path.exists(PASTA_DESTINO):
        shutil.rmtree(PASTA_DESTINO)
    os.makedirs(PASTA_DESTINO)
    
    print(f"--- INICIANDO BACKUP ANDROID (Max {TAMANHO_MAX/1024:.0f}KB) ---")
    
    total_arquivos_gerados = 0
    total_arquivos_lidos = 0
    
    for raiz, dirs, arquivos in os.walk(DIRETORIO_RAIZ):
        # Remove pastas ignoradas da árvore de navegação
        dirs[:] = [d for d in dirs if d not in PASTAS_IGNORADAS]
        
        # Filtra arquivos válidos nesta pasta
        arquivos_validos = []
        for arq in arquivos:
            if deve_processar(arq):
                arquivos_validos.append(os.path.join(raiz, arq))
        
        arquivos_validos.sort()
        
        if not arquivos_validos:
            continue

        # Configura o nome do arquivo de backup baseado na pasta
        nome_grupo = limpar_nome_pasta(raiz)
        parte = 1
        tamanho_atual = 0
        
        nome_arquivo_txt = f"android_{nome_grupo}_parte{parte:02d}.txt"
        caminho_txt = os.path.join(PASTA_DESTINO, nome_arquivo_txt)
        f_saida = open(caminho_txt, 'w', encoding='utf-8')
        
        print(f"📱 Pasta: {nome_grupo}...")

        for caminho_origem in arquivos_validos:
            caminho_rel = os.path.relpath(caminho_origem, DIRETORIO_RAIZ)
            
            try:
                with open(caminho_origem, 'r', encoding='utf-8', errors='ignore') as f_origem:
                    conteudo = f_origem.read()
                
                bloco = formatar_cabecalho(caminho_rel) + conteudo + "\n"
                tamanho_bloco = len(bloco.encode('utf-8'))
                
                # Verifica limite de 200KB
                if tamanho_atual + tamanho_bloco > TAMANHO_MAX:
                    f_saida.close()
                    print(f"   -> {nome_arquivo_txt} salvo.")
                    
                    parte += 1
                    tamanho_atual = 0
                    nome_arquivo_txt = f"android_{nome_grupo}_parte{parte:02d}.txt"
                    caminho_txt = os.path.join(PASTA_DESTINO, nome_arquivo_txt)
                    f_saida = open(caminho_txt, 'w', encoding='utf-8')
                
                f_saida.write(bloco)
                tamanho_atual += tamanho_bloco
                total_arquivos_lidos += 1
                
            except Exception as e:
                print(f"   [ERRO] {caminho_rel}: {e}")

        f_saida.close()
        print(f"   -> {nome_arquivo_txt} salvo.")
        total_arquivos_gerados += parte

    print(f"\n--- CONCLUÍDO ---")
    print(f"Pasta de Destino: '{PASTA_DESTINO}'")
    print(f"Arquivos de Código processados: {total_arquivos_lidos}")
    print(f"Arquivos .txt gerados: {total_arquivos_gerados}")

if __name__ == "__main__":
    realizar_backup()


