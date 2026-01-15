import os
import re

PROJETO = "MotoristaPro-Android"
ARQUIVO_ALVO = "app/src/main/java/com/motoristapro/android/MainActivity.kt"

# NOVOS TEXTOS PROFISSIONAIS
TEXTO_OVERLAY = """
        if (!Settings.canDrawOverlays(this)) {
            showProfessionalDialog(
                title = "Calculadora Flutuante",
                message = "Para que o Motorista Pro mostre o lucro da corrida em tempo real *em cima* do app da Uber ou 99, precisamos da permissão de sobreposição.\\n\\nIsso permite que o card informativo apareça automaticamente sem você precisar sair do aplicativo de viagens.",
                iconRes = R.drawable.ic_permission_layers,
                isAccessibility = false
            ) {
                val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
                startActivity(intent)
            }
            return
        }
"""

TEXTO_ACESSIBILIDADE = """
        if (!isAccessibilityServiceEnabled()) {
            showProfessionalDialog(
                title = "Leitura Automática",
                message = "Para capturar o preço e a quilometragem da tela automaticamente, o Motorista Pro usa a tecnologia de Acessibilidade do Android.\\n\\n🔒 **Privacidade Garantida:**\\nO robô lê APENAS a tela de oferta de viagens. Nenhuma conversa, senha ou dado bancário é acessado ou salvo. O serviço só age quando detecta o app da Uber ou 99 aberto.",
                iconRes = R.drawable.ic_permission_eye,
                isAccessibility = true
            ) {
                startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            }
            return
        }
"""

def log(msg): print(f"\033[36m[{PROJETO}] {msg}\033[0m")

def aplicar():
    if not os.path.exists(ARQUIVO_ALVO):
        log("Arquivo não encontrado.")
        return

    with open(ARQUIVO_ALVO, 'r', encoding='utf-8') as f:
        content = f.read()

    # Substituição Inteligente usando Regex para capturar os blocos if antigos
    
    # 1. Overlay
    # Procura: if (!Settings.canDrawOverlays(this)) { ... }
    # O regex pega o if até o return correspondente
    regex_overlay = r'if \(!Settings\.canDrawOverlays\(this\)\) \{[\s\S]*?return\s+}'
    
    match_overlay = re.search(regex_overlay, content)
    if match_overlay:
        content = content.replace(match_overlay.group(0), TEXTO_OVERLAY.strip())
        log("Texto de permissão Overlay atualizado.")
    else:
        log("Não encontrei o bloco de permissão Overlay.")

    # 2. Acessibilidade
    # Procura: if (!isAccessibilityServiceEnabled()) { ... }
    regex_access = r'if \(!isAccessibilityServiceEnabled\(\)\) \{[\s\S]*?return\s+}'
    
    match_access = re.search(regex_access, content)
    if match_access:
        content = content.replace(match_access.group(0), TEXTO_ACESSIBILIDADE.strip())
        log("Texto de permissão Acessibilidade atualizado.")
    else:
        log("Não encontrei o bloco de permissão Acessibilidade.")

    with open(ARQUIVO_ALVO, 'w', encoding='utf-8') as f:
        f.write(content)
        
    os.system("git add .")
    os.system('git commit -m "UX: Textos de permissao mais claros e profissionais"')
    os.system("git push")
    log("Git Push realizado.")

if __name__ == "__main__":
    aplicar()

