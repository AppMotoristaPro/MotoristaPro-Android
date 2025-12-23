import os

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def update_ocr_service():
    file_path = find_file("OcrService.kt")
    if not file_path:
        print("❌ Arquivo OcrService.kt não encontrado.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nova lógica de análise (AnalyzeScreen)
    # Usa Regex com escape duplo (\\\\) para passar pelo Python e chegar no Kotlin como (\\)
    new_analyze = r"""
    private fun analyzeScreen(rawText: String): Boolean {
        // Limpeza básica
        val cleanText = rawText.replace("[^0-9a-zA-Z$,. ]".toRegex(), " ").lowercase()
        
        // Listas para armazenar todos os valores encontrados no frame
        val prices = ArrayList<Double>()
        val dists = ArrayList<Double>()
        val times = ArrayList<Double>()

        // 1. EXTRAIR PREÇOS (R$)
        val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)")
        val matP = pm.matcher(cleanText)
        while (matP.find()) {
            val v = matP.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > 4.0 && v < 2000.0) prices.add(v)
        }

        // 2. EXTRAIR DISTÂNCIAS (KM ou M)
        val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)")
        val matD = dm.matcher(cleanText)
        while (matD.find()) {
            var d = matD.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = matD.group(2)
            if (unit == "m") d /= 1000.0
            if (d > 0.1 && d < 300.0) dists.add(d)
        }

        // 3. EXTRAIR TEMPOS (H e MIN)
        // Padrão horas (ex: 1h 20min)
        val tmH = Pattern.compile("([0-9]+)\\s*h\\s*(?:([0-9]+)\\s*min)?")
        val matH = tmH.matcher(cleanText)
        while (matH.find()) {
            val h = matH.group(1)?.toIntOrNull() ?: 0
            val m = matH.group(2)?.toIntOrNull() ?: 0
            times.add((h * 60 + m).toDouble())
        }
        // Padrão minutos isolados (ex: 45 min)
        val tmM = Pattern.compile("([0-9]+)\\s*min")
        val matM = tmM.matcher(cleanText)
        while (matM.find()) {
            val m = matM.group(1)?.toDoubleOrNull() ?: 0.0
            // Evita duplicar se já foi pego pelo regex de horas (filtro simples por proximidade seria ideal, mas aqui aceitamos tudo e ordenamos)
            times.add(m)
        }

        // --- LÓGICA ESTRITA (HIERARQUIA) ---
        
        // 1. Validar Quantidade Mínima
        // O usuário exigiu: "achar 2 tempo e 2 distancias" para garantir precisão
        if (prices.isEmpty() || dists.size < 2 || times.size < 2) {
            return false // Leitura inválida/incompleta, tenta próximo frame
        }

        // 2. Ordenar decrescente (Os maiores primeiro)
        prices.sortDescending()
        dists.sortDescending()
        times.sortDescending()

        // 3. Pegar os valores finais
        // Preço: O maior valor encontrado (Geralmente o valor total da corrida)
        val finalPrice = prices[0]

        // Distância: Soma das 2 maiores (Viagem + Busca)
        // Ignoramos a terceira em diante pois pode ser lixo de texto
        val finalDist = dists[0] + dists[1]

        // Tempo: Soma dos 2 maiores (Viagem + Busca)
        val finalTime = times[0] + times[1]

        // Filtro Final de Sanidade
        if (finalPrice > 0 && finalDist > 0 && finalTime > 0) {
            lastValidReadTime = System.currentTimeMillis()

            // Atualiza somente se houver mudança significativa para evitar "piscar"
            if (Math.abs(finalPrice - lastPrice) > 0.1 || Math.abs(finalDist - lastDist) > 0.1) {
                lastPrice = finalPrice
                lastDist = finalDist

                val valPerKm = if (finalDist > 0) finalPrice / finalDist else 0.0
                val valPerHour = if (finalTime > 0) (finalPrice / finalTime) * 60 else 0.0

                showCard(finalPrice, finalDist, finalTime, valPerKm, valPerHour)

                val intent = Intent("OCR_DATA_DETECTED")
                intent.putExtra("price", finalPrice)
                intent.putExtra("dist", finalDist)
                intent.putExtra("time", finalTime)
                LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
            }
            return true
        }

        return false
    }
    """

    # Localiza o método antigo e substitui
    start_marker = "private fun analyzeScreen(rawText: String): Boolean {"
    end_marker = "override fun onDestroy()"
    
    start_idx = content.find(start_marker)
    
    if start_idx != -1:
        # Tenta achar o onDestroy para substituir o bloco anterior a ele
        end_idx = content.find(end_marker, start_idx)
        if end_idx != -1:
            # Substituição cirúrgica
            new_content = content[:start_idx] + new_analyze + "\n\n    " + content[end_idx:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ OcrService.kt atualizado com lógica ESTRITA (2 Tempos/2 Distâncias).")
            
            # Git Push
            os.system('git add .')
            os.system('git commit -m "Fix: OCR Strict Logic (2 Times/2 Dists)"')
            os.system('git push')
        else:
            print("❌ Não encontrei o fim do método (onDestroy).")
    else:
        print("❌ Não encontrei o método analyzeScreen.")

if __name__ == "__main__":
    update_ocr_service()


