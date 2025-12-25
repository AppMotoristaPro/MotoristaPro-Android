import os

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def main():
    print("🧠 Atualizando cérebro do Robô (Lógica de Horas e Soma)...")
    
    file_path = find_file("OcrService.kt")
    if not file_path:
        print("❌ Erro: OcrService.kt não encontrado.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nova lógica de OCR
    new_analyze_logic = r"""
    private fun analyzeScreen(rawText: String): Boolean {
        // Limpeza básica
        var cleanText = rawText.lowercase()
            .replace(Regex("\\+\\s*r\\$\\s*[0-9.,]+"), "") 
            .replace("mais de 30 min", "")
            .replace("mais de 30min", "")
            .replace("[^0-9a-zA-Z$,. ]".toRegex(), " ")

        val prices = ArrayList<Double>()
        val dists = ArrayList<Double>()
        val times = ArrayList<Double>()

        // 1. PREÇOS
        val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)")
        val matP = pm.matcher(cleanText)
        while (matP.find()) {
            val v = matP.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > 4.5 && v < 2000.0) prices.add(v)
        }

        // 2. DISTÂNCIAS
        val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)")
        val matD = dm.matcher(cleanText)
        while (matD.find()) {
            var d = matD.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = matD.group(2)
            if (unit == "m") d /= 1000.0
            if (d > 0.05 && d < 400.0) dists.add(d)
        }

        // 3. TEMPOS (LÓGICA AVANÇADA DE HORAS)
        
        // A. Primeiro, captura horas explícitas (Ex: "1h", "2 h") e converte para minutos
        val tmH = Pattern.compile("([0-9]+)\\s*h")
        val matH = tmH.matcher(cleanText)
        while (matH.find()) {
            val h = matH.group(1)?.toIntOrNull() ?: 0
            if (h > 0) {
                times.add((h * 60).toDouble()) // Converte 1h -> 60, 2h -> 120
            }
        }
        
        // Remove o que já foi lido como hora para não confundir com minutos
        // (Ex: para não ler o "1" de "1h" como minuto depois)
        cleanText = matH.replaceAll(" ") 

        // B. Captura minutos restantes (Ex: "20 min", "5 min")
        val tmM = Pattern.compile("([0-9]+)\\s*min")
        val matM = tmM.matcher(cleanText)
        while (matM.find()) {
            val m = matM.group(1)?.toDoubleOrNull() ?: 0.0
            if (m > 0) times.add(m)
        }

        // --- VALIDAÇÃO ---
        
        // Precisa de pelo menos 1 preço
        if (prices.isEmpty()) return false
        
        // Precisa de pelo menos 2 distâncias (Viagem + Busca)
        if (dists.size < 2) return false
        
        // Precisa de pelo menos 2 tempos (mas idealmente 3 se tiver hora quebrada)
        if (times.size < 2) return false

        // Ordenar decrescente (Maiores primeiro)
        prices.sortDescending()
        dists.sortDescending()
        times.sortDescending()

        val finalPrice = prices[0]
        
        // Distância: Soma as 2 maiores (Viagem + Busca)
        val finalDist = dists[0] + dists[1]
        
        // Tempo: Soma os 3 maiores (se houver), senão soma os 2 maiores
        // Isso cobre o caso: Busca(5) + ViagemHora(60) + ViagemMin(20) = 85 min
        var finalTime = 0.0
        if (times.size >= 3) {
            finalTime = times[0] + times[1] + times[2]
        } else {
            finalTime = times[0] + times[1]
        }

        if (finalPrice > 0 && finalDist > 0 && finalTime > 0) {
            lastValidReadTime = System.currentTimeMillis()

            if (abs(finalPrice - lastPrice) > 0.1 || abs(finalDist - lastDist) > 0.1) {
                lastPrice = finalPrice
                lastDist = finalDist

                val valPerKm = if (finalDist > 0) finalPrice / finalDist else 0.0
                val valPerHour = if (finalTime > 0) (finalPrice / finalTime) * 60 else 0.0

                // CORES
                var color = Color.parseColor("#FACC15")
                var message = "MÉDIA. ANALISE BEM 🤔"
                var bgAlpha = "#33FACC15"

                if (valPerKm >= goodKm && valPerHour >= goodHour) {
                    color = Color.parseColor("#4ADE80")
                    message = "BOA! ACEITA LOGO 🚀"
                    bgAlpha = "#334ADE80"
                } else if (valPerKm <= badKm && valPerHour <= badHour) {
                    color = Color.parseColor("#F87171")
                    message = "PREJUÍZO! PULA FORA 🛑"
                    bgAlpha = "#33F87171"
                }
                
                val bgDica = GradientDrawable().apply { cornerRadius = 15f; setColor(Color.parseColor(bgAlpha)) }
                
                showCard(finalPrice, finalDist, finalTime, valPerKm, valPerHour, color, message, bgDica)

                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", finalPrice); intent.putExtra("dist", finalDist); intent.putExtra("time", finalTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            return true
        }
        return false
    }"""

    # Substituição
    start_marker = "private fun analyzeScreen(rawText: String): Boolean {"
    end_marker = "override fun onDestroy()"
    
    start_idx = content.find(start_marker)
    if start_idx != -1:
        end_idx = content.find(end_marker, start_idx)
        if end_idx != -1:
            new_content = content[:start_idx] + new_analyze_logic + "\n\n    " + content[end_idx:]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Lógica de tempo corrigida (1h -> 60m / Soma de 3 valores).")
        else:
            print("❌ Fim do método não encontrado.")
    else:
        print("❌ Método analyzeScreen não encontrado.")

if __name__ == "__main__":
    main()


