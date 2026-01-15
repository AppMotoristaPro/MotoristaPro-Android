import os

PROJETO = "MotoristaPro-Android"
ARQUIVO_ALVO = "app/src/main/java/com/motoristapro/android/OcrService.kt"

# Nova lógica de análise mais inteligente e blindada contra logs
NOVA_LOGICA = r"""
    private fun analyzeSmartData(jsonString: String, pkgName: String, screenHeight: Int) {
        try {
            if (!isMonitoring) return

            val blocks = JSONArray(jsonString)
            var bestPrice = 0.0
            var maxPriceFontSize = 0
            
            // Variáveis para evitar duplicidade de soma no mesmo frame
            var pickupDist = 0.0
            var tripDist = 0.0
            var pickupTime = 0.0
            var tripTime = 0.0
            
            val detectedApp = if (pkgName.contains("taxis99") || pkgName.contains("didi") || pkgName.contains("99")) "99" else "UBER"
            val ignoreTopLimit = screenHeight * 0.10

            // saveLog("\n=== NOVA LEITURA ($detectedApp) ===")

            for (i in 0 until blocks.length()) {
                val obj = blocks.getJSONObject(i)
                val rawText = obj.getString("text")
                val h = obj.getInt("h")
                val y = obj.getInt("y")
                
                if (y < ignoreTopLimit) continue

                val cleanText = sanitizeOcrErrors(rawText)

                // --- FILTROS DE SEGURANÇA (ANTI-ESPELHO) ---
                // Ignora textos que parecem ser logs do próprio sistema ou notificações
                if (cleanText.startsWith("[") && cleanText.contains("]")) continue // Ignora timestamp de log
                if (cleanText.contains("lido:") || cleanText.contains("limpo:") || cleanText.contains("conclusão:")) continue
                if (cleanText.contains("candidato") || cleanText.contains("detectada:")) continue
                if (cleanText.contains("motorista pro") || cleanText.contains("configurações")) continue
                
                // Filtros de palavras irrelevantes dos apps
                if (cleanText.contains("ganhe r$") || cleanText.contains("meta de ganhos")) continue
                if (cleanText.contains("r$/km") || cleanText.contains("r$/h")) continue // Evita ler o card flutuante antigo

                // A. PREÇO (Lógica Mantida)
                val matPrice = Pattern.compile("(?:r\\$|rs)\\s*([0-9]+(?:\\.[0-9]{2})?)").matcher(cleanText)
                if (matPrice.find()) {
                    val v = matPrice.group(1)?.toDoubleOrNull() ?: 0.0
                    if (v > 4.5 && v < 2000.0) { // Preço máximo razoável
                        if (h > maxPriceFontSize) {
                            maxPriceFontSize = h; bestPrice = v
                        } else if (h == maxPriceFontSize && v > bestPrice) {
                            bestPrice = v
                        }
                    }
                }
                // Fallback Preço (Numero isolado grande)
                if (bestPrice == 0.0 && h > 75) { // Reduzi um pouco a altura mínima
                     val matPrice2 = Pattern.compile("^([0-9]+(?:\\.[0-9]{2}))$").matcher(cleanText.trim())
                     if (matPrice2.find()) {
                         val v = matPrice2.group(1)?.toDoubleOrNull() ?: 0.0
                         if (v > 5.0 && v < 600.0) { 
                             bestPrice = v; maxPriceFontSize = h 
                         }
                     }
                }

                // B. DISTÂNCIA (Lógica Refinada: Separa Pickup de Trip)
                // O padrão da Uber geralmente coloca a distância de busca antes (Y menor) ou depois. 
                // Mas para simplificar, vamos somar apenas valores razoáveis e não repetidos.
                val matDist = Pattern.compile("\\(?([0-9]+(?:\\.[0-9]+)?)\\s*(km|m)\\)?").matcher(cleanText)
                while (matDist.find()) {
                    val valStr = matDist.group(1) ?: "0"
                    val unit = matDist.group(2) ?: "km"
                    var value = valStr.toDoubleOrNull() ?: 0.0
                    if (unit == "m") value /= 1000.0
                    
                    if (value > 0.0 && value < 800.0) { // Limite de 800km para evitar erros bizarros
                        // Se for a primeira distância encontrada, assume busca ou viagem
                        if (pickupDist == 0.0) pickupDist = value
                        else if (tripDist == 0.0) tripDist = value
                        else {
                            // Se já tem 2 distâncias, pode ser um erro de leitura duplicada ou uma terceira parada
                            // Vamos somar apenas se for diferente das anteriores para evitar ler a mesma linha 2x
                            if (value != pickupDist && value != tripDist) {
                                tripDist += value
                            }
                        }
                        // saveLog("  -> DIST: $value km (Raw: $valStr $unit)")
                    }
                }

                // C. TEMPO
                var textForTime = cleanText.replace(Regex("\\d{1,2}:\\d{2}"), " ") // Remove horas tipo 12:30
                
                // Horas
                val matHour = Pattern.compile("(\\d+)\\s*(?:h|hr|hrs|hora|horas)\\b")
                val mHour = matHour.matcher(textForTime)
                while (mHour.find()) {
                    val hVal = mHour.group(1)?.toDoubleOrNull() ?: 0.0
                    if (hVal > 0 && hVal < 24) { 
                        if (pickupTime == 0.0) pickupTime = hVal * 60
                        else tripTime += hVal * 60
                    }
                }
                
                // Minutos
                val matMin = Pattern.compile("(\\d+)\\s*(?:min|minutos|m1n|m1ns|mins)(?!in|etro|l|e|a|o)")
                val mMin = matMin.matcher(textForTime)
                while (mMin.find()) {
                    val mVal = mMin.group(1)?.toDoubleOrNull() ?: 0.0
                    if (mVal > 0 && mVal < 600) { 
                        // Adiciona aos minutos (se já tiver horas no pickupTime, soma lá, senão tripTime)
                        // Logica simplificada: Soma tudo no final, mas tenta evitar duplicatas exatas na mesma linha
                        if (tripTime == 0.0 && pickupTime > 0) tripTime += mVal
                        else if (pickupTime == 0.0) pickupTime = mVal
                        else tripTime += mVal
                    }
                }
            }

            // D. CONSOLIDAÇÃO
            val totalDist = pickupDist + tripDist
            val totalTime = pickupTime + tripTime

            // E. VALIDAÇÃO FINAL
            if (bestPrice > 0.0) {
                // saveLog("PARCIAL: R$ $bestPrice | Dist: $pickupDist + $tripDist | Tempo: $pickupTime + $tripTime")
                
                if ((totalDist > 0.0) || (totalTime > 0.0)) {
                    val currentReading = RideData(bestPrice, totalDist, totalTime)
                    
                    // Anti-Duplicidade de evento (mesma tela processada várias vezes)
                    if (lastRideData != null && lastRideData == currentReading) {
                        return
                    }
                    lastRideData = currentReading

                    val safeDist = if (totalDist == 0.0) 0.1 else totalDist
                    val safeTime = if (totalTime == 0.0) 1.0 else totalTime 
                    val valPerKm = bestPrice / safeDist
                    val valPerHour = (bestPrice / safeTime) * 60.0
                    
                    saveLog("SUCESSO: R$ $bestPrice | $totalDist km | $totalTime min")
                    
                    val resultStyle = if (valPerKm >= goodKm && valPerHour >= goodHour) {
                        Triple(Color.parseColor("#4ADE80"), "ÓTIMA 🚀", "#334ADE80")
                    } else if (valPerKm <= badKm && valPerHour <= badHour) {
                        Triple(Color.parseColor("#F87171"), "RECUSAR 🛑", "#33F87171")
                    } else {
                        Triple(Color.parseColor("#FACC15"), "ANALISAR 🤔", "#33FACC15")
                    }
                    
                    val (finalColor, finalMsg, finalAlpha) = resultStyle
                    val bgDica = GradientDrawable().apply { cornerRadius = 15f; setColor(Color.parseColor(finalAlpha)) }
                    
                    showCard(bestPrice, totalDist, totalTime, valPerKm, valPerHour, finalColor, finalMsg, bgDica, detectedApp)
                }
            }

        } catch (e: Exception) { 
            e.printStackTrace()
            // saveLog("ERRO: ${e.message}")
        }
    }
"""

def log(msg): print(f"\033[36m[{PROJETO}] {msg}\033[0m")

def aplicar():
    if not os.path.exists(ARQUIVO_ALVO):
        log("Arquivo OcrService.kt não encontrado.")
        return

    with open(ARQUIVO_ALVO, 'r', encoding='utf-8') as f:
        content = f.read()

    # Substitui o método analyzeSmartData inteiro
    import re
    pattern = r'private fun analyzeSmartData.*?private fun showCard'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        new_content = content.replace(match.group(0), NOVA_LOGICA.strip() + "\n\n    private fun showCard")
        
        with open(ARQUIVO_ALVO, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        log("Lógica OCR atualizada: Filtro de Logs e Soma Inteligente aplicados.")
        
        # Git Push
        os.system("git add .")
        os.system('git commit -m "Fix: OCR lendo logs proprios e duplicando valores"')
        os.system("git push")
    else:
        log("Erro ao localizar o bloco de código para substituição.")

if __name__ == "__main__":
    aplicar()


