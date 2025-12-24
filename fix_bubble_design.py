import os
import subprocess

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def main():
    print("🎨 Ajustando Balão Flutuante (Sem bordas, Recorte Circular)...")
    
    file_path = find_file("OcrService.kt")
    if not file_path:
        print("❌ Erro: OcrService.kt não encontrado.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Adicionar Imports Necessários para o Recorte (Outline)
    # Precisamos de ViewOutlineProvider e Outline
    if "import android.view.ViewOutlineProvider" not in content:
        content = content.replace("import android.view.*", "import android.view.*\nimport android.view.ViewOutlineProvider\nimport android.graphics.Outline")
        print("✅ Imports de Design adicionados.")

    # 2. Substituir o Bloco de Design
    # Vamos procurar o bloco que criamos anteriormente
    
    # Marcador de início (baseado no script anterior)
    start_marker = "// --- DESIGN:" 
    # Marcador de fim (onde adicionamos a view no layout)
    end_marker = "bubbleLayout.addView(iconView"

    # Novo Código: Sem GradientDrawable, com ClipToOutline
    new_design = """// --- DESIGN: Ícone Limpo e Circular ---
        // Removemos qualquer fundo do container
        bubbleLayout.background = null 

        iconView = ImageView(this)
        iconView!!.setImageResource(R.mipmap.ic_launcher_round)
        iconView!!.scaleType = ImageView.ScaleType.CENTER_CROP
        
        // APLICA MÁSCARA CIRCULAR (Corta os cantos do PNG)
        iconView!!.outlineProvider = object : ViewOutlineProvider() {
            override fun getOutline(view: View, outline: Outline) {
                // Define a área de corte como um oval do tamanho da view
                outline.setOval(0, 0, view.width, view.height)
            }
        }
        iconView!!.clipToOutline = true // Ativa o corte
        
        """

    # Tenta localizar o bloco antigo
    idx_start = content.find("val bg = GradientDrawable()")
    if idx_start == -1:
        # Tenta achar pelo comentário se o código mudou
        idx_start = content.find("// --- DESIGN:")
    
    if idx_start != -1:
        idx_end = content.find(end_marker, idx_start)
        
        if idx_end != -1:
            # Substituição
            content = content[:idx_start] + new_design + content[idx_end:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Design atualizado: Apenas o ícone circular, sem bordas.")
            
            # 3. Git Push
            print("\n🚀 Enviando para o GitHub...")
            try:
                subprocess.run("git add .", shell=True, check=True)
                subprocess.run('git commit -m "Style: Balão flutuante limpo (Circular Clip, No Border)"', shell=True, check=True)
                subprocess.run("git push", shell=True, check=True)
                print("✅ Atualização concluída!")
            except Exception as e:
                print(f"\n❌ Erro no Git: {e}")
        else:
            print("❌ Erro: Não encontrei o final do bloco de design.")
    else:
        print("❌ Erro: Não encontrei o bloco de design antigo para substituir.")
        print("   Verifique se o arquivo OcrService.kt tem o comentário '// --- DESIGN:'")

if __name__ == "__main__":
    main()


