import os

PROJETO = "MotoristaPro-Android"
ARQUIVO_ALVO = "app/src/main/java/com/motoristapro/android/OcrService.kt"

# Vamos substituir o método analyzeSmartData inteiro por uma versão "Verborrágica" (Cheia de logs)
NOVO_ANALYZE = r"""
    private fun analyzeSmartData(jsonString: String, pkgName: String, screenHeight: Int) {
        try {
            if (!isMonitoring) return

            val blocks = JSONArray(jsonString)
            var bestPrice = 0.0
            var maxPriceFontSize = 0
            var totalDist = 0.0
            var totalTime = 0.0
            
            val detectedApp = if (pkgName.contains("taxis99") || pkgName.contains("didi") || pkgName.contains("99")) "99" else "UBER"
            val ignoreTopLimit = screenHeight * 0.10

            // LOG DE INÍCIO DE CICLO (Para separar as leituras)
            saveLog("\n=== NOVA LEITURA ($detectedApp) ===")

            for (i in 0 until blocks.length()) {
                val obj = blocks.getJSONObject(i)
                val rawText = obj.getString("text")
                val h = obj.getInt("h")
                val y = obj.getInt("y")
                
                if (y < ignoreTopLimit) continue

                val cleanText = sanitizeOcrErrors(rawText)

                // Filtros de Ignorar (Logs opcionais para não poluir muito, mas útil saber o que ignorou)
                if (cleanText.contains("ganhe r$") || cleanText.contains("meta")) {
                    // saveLog("IGNORADO (Filtro): $cleanText")
                    continue
                }

                // LOG DO TEXTO PROCESSADO (CRUCIAL PARA DEBUG)
                // Se encontrar números, loga para vermos como o OCR está lendo
                if (cleanText.any { it.isDigit() }) {
                    saveLog("LIDO: '$rawText' -> LIMPO: '$cleanText' (h=$h)")
                }
                
                // A. PREÇO
                val matPrice = Pattern.compile("(?:r\\$|rs)\\s*([0-9]+(?:\\.[0-9]{2})?)").matcher(cleanText)
                if (matPrice.find()) {
                    val v = matPrice.group(1)?.toDoubleOrNull() ?: 0.0
                    saveLog("  -> CANDIDATO PREÇO: R$ $v (Fonte: $h)")
                    if (v > 4.5) {
                        if (h > maxPriceFontSize) {
                            maxPriceFontSize = h; bestPrice = v
                        } else if (h == maxPriceFontSize && v > bestPrice) {
                            bestPrice = v
                        }
                    }
                }
                // Fallback Preço (Numero isolado grande)
                if (bestPrice == 0.0 && h > 80) {
                     val matPrice2 = Pattern.compile("^([0-9]+(?:\\.[0-9]{2}))$").matcher(cleanText.trim())
                     if (matPrice2.find()) {
                         val v = matPrice2.group(1)?.toDoubleOrNull() ?: 0.0
                         if (v > 5.0 && v < 500.0) { 
                             bestPrice = v; maxPriceFontSize = h 
                             saveLog("  -> CANDIDATO PREÇO (ISOLADO): R$ $v")
                         }
                     }
                }

                // B. DISTÂNCIA
                val matDist = Pattern.compile("\\(?([0-9]+(?:\\.[0-9]+)?)\\s*(km|m)\\)?").matcher(cleanText)
                while (matDist.find()) {
                    val valStr = matDist.group(1) ?: "0"
                    val unit = matDist.group(2) ?: "km"
                    var value = valStr.toDoubleOrNull() ?: 0.0
                    if (unit == "m") value /= 1000.0
                    if (value > 0.1 && value < 300.0) { 
                        totalDist += value 
                        saveLog("  -> DISTÂNCIA DETECTADA: $value km (Original: $valStr $unit)")
                    }
                }

                // C. TEMPO
                var textForTime = cleanText.replace(Regex("\\d{1,2}:\\d{2}"), " ")
                val matHour = Pattern.compile("(\\d+)\\s*(?:h|hr|hrs|hora|horas)\\b")
                val mHour = matHour.matcher(textForTime)
                while (mHour.find()) {
                    val hVal = mHour.group(1)?.toDoubleOrNull() ?: 0.0
                    if (hVal > 0 && hVal < 24) { 
                        totalTime += (hVal * 60)
                        saveLog("  -> TEMPO (HORAS): $hVal h")
                    }
                }
                val matMin = Pattern.compile("(\\d+)\\s*(?:min|minutos|m1n|m1ns|mins)(?!in|etro|l|e|a|o)")
                val mMin = matMin.matcher(textForTime)
                while (mMin.find()) {
                    val mVal = mMin.group(1)?.toDoubleOrNull() ?: 0.0
                    if (mVal > 0 && mVal < 600) { 
                        totalTime += mVal
                        saveLog("  -> TEMPO (MIN): $mVal min")
                    }
                }
            }

            // D. VALIDAÇÃO E LOG FINAL
            if (bestPrice > 0.0) {
                val status = if ((totalDist > 0.0) || (totalTime > 0.0)) "DADOS COMPLETOS" else "DADOS PARCIAIS"
                saveLog("CONCLUSÃO: $status | R$ $bestPrice | ${"%.1f".format(totalDist)} km | ${"%.0f".format(totalTime)} min")
                
                if (status == "DADOS COMPLETOS") {
                    val currentReading = RideData(bestPrice, totalDist, totalTime)
                    if (lastRideData != null && lastRideData == currentReading) {
                        saveLog("AÇÃO: Ignorado (Duplicidade)")
                        return
                    }
                    lastRideData = currentReading

                    val safeDist = if (totalDist == 0.0) 0.1 else totalDist
                    val safeTime = if (totalTime == 0.0) 1.0 else totalTime 
                    val valPerKm = bestPrice / safeDist
                    val valPerHour = (bestPrice / safeTime) * 60.0
                    
                    // Lógica de Cores
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
            } else {
                // saveLog("CONCLUSÃO: Nenhum preço identificado.")
            }

        } catch (e: Exception) { 
            e.printStackTrace()
            saveLog("ERRO FATAL NA ANÁLISE: ${e.message}")
        }
    }
"""

def log(msg): print(f"\033[36m[{PROJETO}] {msg}\033[0m")

def aplicar():
    if not os.path.exists(ARQUIVO_ALVO):
        log("Arquivo não encontrado.")
        return

    with open(ARQUIVO_ALVO, 'r', encoding='utf-8') as f:
        content = f.read()

    # Usa Regex para encontrar e substituir o método analyzeSmartData antigo
    # Procura desde "private fun analyzeSmartData" até o fechamento antes de "private fun showCard"
    
    # Estratégia: Identificar o cabeçalho da função e substituir tudo até o início da próxima função
    pattern = r'private fun analyzeSmartData.*?private fun showCard'
    
    # Verifica se a próxima função é showCard (padrão do arquivo que mandei)
    import re
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Reconstrói o bloco substituindo o corpo
        novo_bloco = NOVO_ANALYZE.strip() + "\n\n    private fun showCard"
        new_content = content.replace(match.group(0), novo_bloco)
        
        with open(ARQUIVO_ALVO, 'w', encoding='utf-8') as f:
            f.write(new_content)
        log("Logs de diagnóstico detalhados aplicados com sucesso!")
        
        os.system("git add .")
        os.system('git commit -m "Dev: Logs detalhados de OCR para diagnostico"')
        os.system("git push")
        log("Git Push realizado.")
    else:
        log("Não foi possível localizar o método analyzeSmartData para substituição.")

if __name__ == "__main__":
    aplicar()

