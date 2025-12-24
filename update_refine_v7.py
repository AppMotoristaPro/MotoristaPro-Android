import os
import re

def find_file(filename, search_path="."):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def update_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo atualizado: {path}")

def main():
    print("🔧 Iniciando refinamento do Robô (Distância, Filtros e UI)...")
    
    ocr_path = find_file("OcrService.kt")
    if not ocr_path:
        print("❌ Erro: OcrService.kt não encontrado.")
        return

    with open(ocr_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- 1. AJUSTE DE LARGURA DA JANELA (UI) ---
    # Procura a definição de largura antiga (0.90 ou 90%)
    # Mudamos para 0.65 (65%) para ficar mais estreito horizontalmente
    if "widthPixels * 0.90" in content:
        content = content.replace("widthPixels * 0.90", "widthPixels * 0.65")
        print("✅ Janela flutuante estreitada (90% -> 65%).")
    elif "widthPixels * 0.55" in content: # Caso tenha rodado algum teste anterior
        content = content.replace("widthPixels * 0.55", "widthPixels * 0.65")
        print("✅ Janela ajustada para 65%.")

    # --- 2. NOVA LÓGICA DE LEITURA (AnalyzeScreen) ---
    # Substitui o método inteiro para garantir a ordem correta de limpeza -> regex
    
    new_analyze_method = r"""
    private fun analyzeScreen(rawText: String): Boolean {
        // LIMPEZA PRÉVIA (CRÍTICO)
        // Removemos padrões que confundem o robô ANTES de buscar números.
        // 1. Remove "+R$ ..." (taxas incluídas)
        // 2. Remove "/km" (preço por km informativo)
        // 3. Remove "mais de 30 min" (aviso de viagem longa)
        var cleanText = rawText.lowercase()
            .replace(Regex("\\+\\s*r\\$\\s*[0-9.,]+"), "") 
            .replace(Regex("r\\$\\s*[0-9.,]+\\s*/\\s*km"), "")
            .replace("mais de 30 min", "")
            .replace("mais de 30min", "")
            .replace("[^0-9a-zA-Z$,. ]".toRegex(), " ")

        val prices = ArrayList<Double>()
        val dists = ArrayList<Double>()
        val times = ArrayList<Double>()

        // A. EXTRAIR PREÇOS (R$)
        val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)")
        val matP = pm.matcher(cleanText)
        while (matP.find()) {
            val v = matP.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            if (v > 4.5 && v < 2000.0) prices.add(v)
        }

        // B. EXTRAIR DISTÂNCIAS (KM ou M)
        // O grupo 2 captura a unidade (km ou m)
        val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)")
        val matD = dm.matcher(cleanText)
        while (matD.find()) {
            var d = matD.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = matD.group(2)
            
            // CONVERSÃO DE METROS
            if (unit == "m") {
                d /= 1000.0 // Ex: 500m vira 0.5 km
            }
            
            // Filtro: Aceita corridas curtas (0.1km) até 400km
            if (d > 0.05 && d < 400.0) dists.add(d)
        }

        // C. EXTRAIR TEMPOS (H e MIN)
        val tmH = Pattern.compile("([0-9]+)\\s*h\\s*(?:([0-9]+)\\s*min)?")
        val matH = tmH.matcher(cleanText)
        while (matH.find()) {
            val h = matH.group(1)?.toIntOrNull() ?: 0
            val m = matH.group(2)?.toIntOrNull() ?: 0
            val totalMinutes = (h * 60) + m
            if (totalMinutes > 0) times.add(totalMinutes.toDouble())
        }
        
        // Remove horas lidas para não duplicar minutos
        cleanText = matH.replaceAll(" ") 

        val tmM = Pattern.compile("([0-9]+)\\s*min")
        val matM = tmM.matcher(cleanText)
        while (matM.find()) {
            val m = matM.group(1)?.toDoubleOrNull() ?: 0.0
            if (m > 0) times.add(m)
        }

        // --- LÓGICA ESTRITA ---
        // Exige pelo menos 2 tempos e 2 distâncias (Viagem + Busca)
        if (prices.isEmpty() || dists.size < 2 || times.size < 2) {
            return false 
        }

        // Ordenar decrescente (Maiores primeiro)
        prices.sortDescending()
        dists.sortDescending()
        times.sortDescending()

        val finalPrice = prices[0]
        val finalDist = dists[0] + dists[1]
        val finalTime = times[0] + times[1]

        if (finalPrice > 0 && finalDist > 0 && finalTime > 0) {
            lastValidReadTime = System.currentTimeMillis()

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
    }"""

    # Encontrar limites para substituição
    start_sig = "private fun analyzeScreen(rawText: String): Boolean {"
    end_sig = "override fun onDestroy()"
    
    start_idx = content.find(start_sig)
    if start_idx != -1:
        end_idx = content.find(end_sig, start_idx)
        if end_idx != -1:
            # Substitui
            content = content[:start_idx] + new_analyze_method + "\n\n    " + content[end_idx:]
            print("✅ Lógica de Metros e Filtros aplicada.")
            
            update_file(ocr_path, content)
            
            # Git Push
            print("\n🚀 Enviando para GitHub...")
            os.system('git add .')
            os.system('git commit -m "Fix: OCR Meters Conversion & Ignore Patterns"')
            os.system('git push')
        else:
            print("❌ Erro: Não achei o final do método (onDestroy).")
    else:
        print("❌ Erro: Método analyzeScreen não encontrado.")

if __name__ == "__main__":
    main()


