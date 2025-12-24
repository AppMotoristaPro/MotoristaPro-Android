import os
import subprocess

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def main():
    print("🕹️ Tornando o balão flutuante móvel...")
    
    file_path = find_file("OcrService.kt")
    if not file_path:
        print("❌ Erro: OcrService.kt não encontrado.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Código antigo (apenas clique)
    target_line = "bubbleLayout.setOnClickListener { showControls() }"
    
    # Novo código (Lógica de Arrastar + Clique)
    # Usamos Math.abs para calcular a distância do movimento
    new_logic = """
        // --- TORNAR ARRASTÁVEL ---
        bubbleLayout.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View?, event: MotionEvent?): Boolean {
                when (event!!.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialX = params.x
                        initialY = params.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        params.x = initialX + (event.rawX - initialTouchX).toInt()
                        params.y = initialY + (event.rawY - initialTouchY).toInt()
                        windowManager.updateViewLayout(bubbleView, params)
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        // Se moveu menos de 10 pixels, considera um CLIQUE
                        if (Math.abs(event.rawX - initialTouchX) < 10 && Math.abs(event.rawY - initialTouchY) < 10) {
                            showControls()
                        }
                        return true
                    }
                }
                return false
            }
        })
    """

    if target_line in content:
        new_content = content.replace(target_line, new_logic)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Lógica de toque e arraste aplicada com sucesso.")
        
        # Git Push
        print("\n🚀 Enviando para o GitHub...")
        try:
            subprocess.run("git add .", shell=True, check=True)
            subprocess.run('git commit -m "Feat: Balão flutuante agora é móvel (Draggable Bubble)"', shell=True, check=True)
            subprocess.run("git push", shell=True, check=True)
            print("✅ Atualização concluída!")
        except Exception as e:
            print(f"❌ Erro no Git: {e}")
            
    else:
        print("⚠️ Não encontrei a linha exata 'bubbleLayout.setOnClickListener'.")
        print("   O código pode já ter sido alterado. Verifique se o balão já se move.")

if __name__ == "__main__":
    main()


