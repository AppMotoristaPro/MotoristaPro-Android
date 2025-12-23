import os
import subprocess

# --- CONFIGURAÇÕES ---
file_path = "app/src/main/java/com/motoristapro/android/OcrService.kt"

# 1. BLOCO DE DESIGN (Balão Branco + Ícone do App)
# Substitui a criação do ícone antigo por um novo layout redondo e branco
old_ui_block = """        iconView = ImageView(this)
        iconView!!.setImageResource(R.drawable.ic_launcher_foreground)
        iconView!!.background = null; iconView!!.elevation = 10f
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(140, 140))"""

new_ui_block = """        // --- NOVO DESIGN: Redondo, Branco e com Ícone do App ---
        val bg = GradientDrawable()
        bg.shape = GradientDrawable.OVAL
        bg.setColor(Color.WHITE)
        bg.setStroke(2, Color.parseColor("#2563EB")) // Azul do Site
        bubbleLayout.background = bg
        bubbleLayout.elevation = 20f

        iconView = ImageView(this)
        // Usa o ícone do próprio APK (que você vai substituir manualmente)
        iconView!!.setImageResource(R.mipmap.ic_launcher_round)
        iconView!!.setPadding(15, 15, 15, 15) // Margem interna para ficar bonito
        
        bubbleLayout.addView(iconView, FrameLayout.LayoutParams(160, 160))
        // -------------------------------------------------------"""

# 2. BLOCO DE LÓGICA (Regex Melhorado)
# Substitui o método analyzeScreen inteiro por uma versão mais robusta
old_analyze_method_start = "private fun analyzeScreen(rawText: String): Boolean {"
new_analyze_method = """    private fun analyzeScreen(rawText: String): Boolean {
        var framePrice = 0.0; var frameDist = 0.0; var frameTime = 0.0
        // Limpeza agressiva: remove tudo que não é alphanumérico ou pontuação chave
        val cleanText = rawText.replace("[^0-9a-zA-Z$,. ]".toRegex(), " ").lowercase()
        
        // 1. PREÇO: Aceita "R$ 10", "10,50", "10.5", "10"
        // Regex busca cifrão seguido de digitos, com ou sem decimais
        val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)").matcher(cleanText)
        while (pm.find()) { 
            val vStr = pm.group(1)?.replace(",", ".") 
            val v = vStr?.toDoubleOrNull() ?: 0.0
            // Filtro de segurança: ignora valores absurdos (ex: R$ 0.00 ou R$ 5000 numa tela só)
            if (v > 1.0 && v < 2000.0 && v > framePrice) framePrice = v 
        }
        
        // 2. DISTÂNCIA: Aceita "1.5 km", "10km", "500m"
        val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)").matcher(cleanText)
        while (dm.find()) { 
            var d = dm.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = dm.group(2)
            if (unit == "m") d /= 1000.0 // Converte metros para KM
            // Filtro: Viagens muito longas (>300km) geralmente são erro de leitura de data/hora
            if (d > 0.1 && d < 300.0) frameDist += d 
        }
        
        // 3. TEMPO: Aceita "1h 20min", "50 min"
        val tm = Pattern.compile("([0-9]+)\\s*h\\s*(?:([0-9]+)\\s*min)?").matcher(cleanText)
        while (tm.find()) { 
            val h = tm.group(1)?.toIntOrNull() ?: 0
            val m = tm.group(2)?.toIntOrNull() ?: 0
            frameTime += (h * 60) + m
        }
        if (frameTime == 0.0) { 
            val mm = Pattern.compile("([0-9]+)\\s*min").matcher(cleanText)
            while (mm.find()) frameTime += mm.group(1)?.toDoubleOrNull() ?: 0.0 
        }

        // --- LÓGICA DE DECISÃO ---
        // Só exibe se tivermos PREÇO e (Distância OU Tempo)
        if (framePrice > 0.0 && (frameDist > 0.0 || frameTime > 0.0)) {
            lastValidReadTime = System.currentTimeMillis()
            
            // Evita ficar piscando a tela com a mesma leitura
            if (abs(framePrice - lastPrice) > 0.1 || abs(frameDist - lastDist) > 0.1) {
                lastPrice = framePrice; lastDist = frameDist
                
                // Cálculos de Rentabilidade
                val valPerKm = if (frameDist > 0) framePrice / frameDist else 0.0
                val valPerHour = if (frameTime > 0) (framePrice / frameTime) * 60 else 0.0
                
                // Exibe o Card (Usa as configs minKm e minHora carregadas do site)
                showCard(framePrice, frameDist, frameTime, valPerKm, valPerHour)
                
                // Envia para o site (WebView)
                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", framePrice); intent.putExtra("dist", frameDist); intent.putExtra("time", frameTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            return true
        }
        return false
    }"""

def run_git_commands():
    try:
        print("\n--- 📦 Git: Adicionando arquivos... ---")
        subprocess.run("git add .", shell=True, check=True)
        
        print("--- 📝 Git: Commitando... ---")
        commit_msg = "Update: Design do Balão (Site Icon) e Melhoria no OCR (Regex Flexível)"
        subprocess.run(f'git commit -m "{commit_msg}"', shell=True, check=True)
        
        print("--- 🚀 Git: Enviando (Push)... ---")
        subprocess.run("git push", shell=True, check=True)
        print("\n✅ Sucesso! Código atualizado.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro no Git: {e}")

def update_file():
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Aplicar Mudança de UI
    if old_ui_block in content:
        content = content.replace(old_ui_block, new_ui_block)
        print("✅ UI do Balão atualizada.")
    elif "GradientDrawable.OVAL" in content:
        print("⚠️ UI já parece estar atualizada.")
    else:
        print("⚠️ Não foi possível localizar o bloco de UI antigo exato. Verifique manualmente.")

    # Aplicar Mudança de Regex (Substitui o método inteiro para garantir integridade)
    # Procuramos o início do método e o final (assumindo que ele acaba antes do onDestroy)
    if old_analyze_method_start in content:
        # Estratégia simples: Localizar o método e substituir até o onDestroy
        start_idx = content.find(old_analyze_method_start)
        end_idx = content.find("override fun onDestroy()", start_idx)
        
        if start_idx != -1 and end_idx != -1:
            # Removemos um pouco de espaço antes do onDestroy para encaixar o novo método
            original_method = content[start_idx:end_idx].strip()
            # Substituição segura
            content = content.replace(original_method, new_analyze_method.strip() + "\n\n    ")
            print("✅ Lógica de OCR (Regex) atualizada.")
        else:
            print("❌ Erro ao localizar limites do método analyzeScreen.")
    else:
        print("⚠️ Método analyzeScreen não encontrado ou já modificado.")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    run_git_commands()

if __name__ == "__main__":
    print("🤖 Atualizando MotoristaPro Android...")
    update_file()


