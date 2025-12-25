import os
import re
import time

def find_file(name, path="."):
    for root, dirs, files in os.walk(path):
        if name in files: return os.path.join(root, name)
    return None

def main():
    print("🚑 Iniciando Correção Dupla (OCR + Versionamento)...")

    # ==========================================================================
    # 1. ATUALIZAR OCR (Lógica de Horas)
    # ==========================================================================
    ocr_path = find_file("OcrService.kt")
    if ocr_path:
        with open(ocr_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Nova lógica de análise (AnalyzeScreen)
        new_analyze = r"""
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

        // 3. TEMPOS (Correção 1h -> 60min)
        
        // A. Captura Horas (h, hr, hrs)
        val tmH = Pattern.compile("([0-9]+)\\s*(?:h|hr|hrs|hora)")
        val matH = tmH.matcher(cleanText)
        while (matH.find()) {
            val h = matH.group(1)?.toIntOrNull() ?: 0
            if (h > 0) {
                times.add((h * 60).toDouble()) // Converte para minutos
            }
        }
        
        // Remove as horas encontradas para não confundir com minutos soltos
        cleanText = matH.replaceAll(" ") 

        // B. Captura Minutos (min, m)
        val tmM = Pattern.compile("([0-9]+)\\s*(?:min|m)(?!in)")
        val matM = tmM.matcher(cleanText)
        while (matM.find()) {
            val m = matM.group(1)?.toDoubleOrNull() ?: 0.0
            if (m > 0) times.add(m)
        }

        // --- VALIDAÇÃO ---
        if (prices.isEmpty()) return false
        
        // Exige pelo menos 2 distâncias (Viagem + Busca)
        if (dists.size < 2) return false
        
        // Exige pelo menos 2 tempos (Viagem + Busca)
        // OBS: Se tivermos "1h" e "20min", isso conta como 2 tempos na lista 'times', então ok.
        if (times.size < 2) return false

        // Ordenar decrescente
        prices.sortDescending()
        dists.sortDescending()
        times.sortDescending()

        val finalPrice = prices[0]
        val finalDist = dists[0] + dists[1]
        
        // SOMA DE TEMPOS (Correção: Soma até 3 valores)
        // Ex: 1h (60) + 20min (20) + Busca (5) = 85
        // A lista times estaria ordenada: [60, 20, 5]
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

                // CORES HÍBRIDAS
                var color = Color.parseColor("#FACC15") // Amarelo
                var message = "MÉDIA. ANALISE BEM 🤔"
                var bgAlpha = "#33FACC15"

                if (valPerKm >= goodKm && valPerHour >= goodHour) {
                    color = Color.parseColor("#4ADE80") // Verde
                    message = "BOA! ACEITA LOGO 🚀"
                    bgAlpha = "#334ADE80"
                } else if (valPerKm <= badKm && valPerHour <= badHour) {
                    color = Color.parseColor("#F87171") // Vermelho
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

        start_marker = "private fun analyzeScreen(rawText: String): Boolean {"
        end_marker = "override fun onDestroy()"
        
        idx_s = content.find(start_marker)
        if idx_s != -1:
            idx_e = content.find(end_marker, idx_s)
            if idx_e != -1:
                content = content[:idx_s] + new_analyze + "\n\n    " + content[idx_e:]
                with open(ocr_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Lógica OCR atualizada (Soma 3 valores, Híbrido, Horas).")

    # ==========================================================================
    # 2. ATUALIZAR VERSIONADOR (Timestamp)
    # ==========================================================================
    auto_ver_code = r"""import re
import os
import time

gradle_path = "app/build.gradle.kts"

def increment_version():
    if not os.path.exists(gradle_path):
        print(f"❌ {gradle_path} não encontrado.")
        return

    with open(gradle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Timestamp atual (segundos desde 1970)
    # Ex: 1703480000. Isso garante unicidade.
    ts = int(time.time())
    
    # Atualiza versionCode
    new_content = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {ts}', content)
    
    # Atualiza versionName (Data legível ou simples)
    new_content = re.sub(r'versionName\s*=\s*".*?"', f'versionName = "2.0.{ts}"', new_content)

    with open(gradle_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Versão definida para Timestamp: {ts}")

if __name__ == "__main__":
    increment_version()
"""
    with open("auto_version.py", "w", encoding='utf-8') as f:
        f.write(auto_ver_code)
    print("✅ auto_version.py atualizado para usar Timestamp.")
    
    # Roda a versão uma vez para aplicar já
    os.system("python3 auto_version.py")

if __name__ == "__main__":
    main()


