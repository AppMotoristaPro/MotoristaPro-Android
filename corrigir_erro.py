import os

# Caminho do arquivo com problema
file_path = "app/src/main/java/com/motoristapro/android/OcrService.kt"

def fix_ocr_service():
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        print("Certifique-se de rodar este script na raiz do projeto.")
        return

    print(f"lendo {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    import_added = False
    
    # Mapeamento de correções de Regex (transformando strings normais em raw strings)
    # A chave é um trecho único da linha original, o valor é a linha corrigida
    regex_fixes = {
        'Regex("r\$\s*[0-9.,]+\s*/\s*km")': '            .replace(Regex("""r\$\s*[0-9.,]+\s*/\s*km"""), "")',
        'Regex("\+\s*r\$\s*[0-9.,]+\s*inclu[íi]do")': '            .replace(Regex("""\+\s*r\$\s*[0-9.,]+\s*inclu[íi]do"""), "")',
        'Pattern.compile("(?:r\$|rs|\$)\s*([0-9]+(?:[.,][0-9]{0,2})?)")': '        val pm = Pattern.compile("""(?:r\$|rs|\$)\s*([0-9]+(?:[.,][0-9]{0,2})?)""")',
        'Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\s*(km|m)(?!in)")': '        val dm = Pattern.compile("""([0-9]+(?:[.,][0-9]+)?)\s*(km|m)(?!in)""")',
        'Pattern.compile("([0-9]+)\s*(?:h|hr|hrs|hora)")': '        val tmH = Pattern.compile("""([0-9]+)\s*(?:h|hr|hrs|hora)""")',
        'Pattern.compile("([0-9]+)\s*(?:min|m)(?!in)")': '        val tmM = Pattern.compile("""([0-9]+)\s*(?:min|m)(?!in)""")'
    }

    for line in lines:
        # 1. Adicionar o import faltante (DisplayMetrics)
        if not import_added and "import android.graphics.*" in line:
            new_lines.append(line)
            new_lines.append("import android.util.DisplayMetrics\n") # Adiciona o import logo após graphics
            import_added = True
            print("✅ Import DisplayMetrics adicionado.")
            continue
            
        # Se já tiver o import, não adiciona de novo
        if "import android.util.DisplayMetrics" in line:
            import_added = True

        # 2. Corrigir os Illegal Escapes nas Regex
        replaced = False
        for bad_snippet, fixed_line in regex_fixes.items():
            # Verifica se a linha contém o trecho problemático (ignorando espaços em branco no inicio/fim para match)
            # Usamos replace direto para manter indentação se possível, ou substituição total se a string bater
            if bad_snippet in line:
                # Mantém a indentação original da linha
                indent = line[:len(line) - len(line.lstrip())]
                # Remove a quebra de linha do fixed_line se tiver, para adicionar limpo
                new_lines.append(fixed_line.strip() + "\n" if fixed_line.strip() not in line else line)
                # Nota: O código acima simplifica e substitui a linha inteira pela versão corrigida (ajustando manualmente a indentação abaixo)
                # Vamos fazer uma substituição mais segura baseada no conteúdo
                replaced = True
                print(f"✅ Regex corrigida: {bad_snippet[:30]}...")
                break
        
        if not replaced:
            # Se não foi uma linha de regex, mantém original
            new_lines.append(line)

    # Refinando a substituição das linhas corrigidas para garantir a indentação correta
    # Como o loop acima pode ter perdido indentação ao usar o dicionário fixo, vamos reprocessar com string replace simples
    
    final_content = "".join(lines)
    
    # 1. Aplicar import se não foi feito (caso o ponto de inserção fosse diferente)
    if "import android.util.DisplayMetrics" not in final_content:
        final_content = final_content.replace("import android.graphics.*", "import android.graphics.*\nimport android.util.DisplayMetrics")

    # 2. Aplicar correções de Regex no conteúdo total (mais seguro que linha a linha para preservar indentação)
    replacements = [
        ('Regex("r\$\s*[0-9.,]+\s*/\s*km")', 'Regex("""r\$\s*[0-9.,]+\s*/\s*km""")'),
        ('Regex("\+\s*r\$\s*[0-9.,]+\s*inclu[íi]do")', 'Regex("""\+\s*r\$\s*[0-9.,]+\s*inclu[íi]do""")'),
        ('Pattern.compile("(?:r\$|rs|\$)\s*([0-9]+(?:[.,][0-9]{0,2})?)")', 'Pattern.compile("""(?:r\$|rs|\$)\s*([0-9]+(?:[.,][0-9]{0,2})?)""")'),
        ('Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\s*(km|m)(?!in)")', 'Pattern.compile("""([0-9]+(?:[.,][0-9]+)?)\s*(km|m)(?!in)""")'),
        ('Pattern.compile("([0-9]+)\s*(?:h|hr|hrs|hora)")', 'Pattern.compile("""([0-9]+)\s*(?:h|hr|hrs|hora)""")'),
        ('Pattern.compile("([0-9]+)\s*(?:min|m)(?!in)")', 'Pattern.compile("""([0-9]+)\s*(?:min|m)(?!in)""")')
    ]

    count_regex = 0
    for old, new in replacements:
        if old in final_content:
            final_content = final_content.replace(old, new)
            count_regex += 1
    
    if count_regex > 0:
        print(f"✅ Total de {count_regex} padrões Regex corrigidos.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("\n🎉 Correções aplicadas com sucesso!")
    print("Agora tente compilar novamente.")

if __name__ == "__main__":
    fix_ocr_service()


