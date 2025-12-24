import os
import subprocess

# --- FUNÇÕES ---
def find_file(filename, search_path="."):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Arquivo atualizado: {path}")

# ==============================================================================
# 1. ATUALIZAR O ROBÔ (OcrService.kt)
# ==============================================================================
print("\n🤖 Refinando Lógica do Robô...")
ocr_path = find_file("OcrService.kt")

if ocr_path:
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_content = f.read()

    # NOVA LÓGICA DE ANÁLISE (Com filtro de ruído e parser de horas)
    # Nota: Usamos escapes duplos (\\) para Regex em Kotlin
    new_analyze_logic = r"""
    private fun analyzeScreen(rawText: String): Boolean {
        // 1. LIMPEZA ESPECIAL (Solicitação do usuário)
        // Remove avisos de rodapé como "Viagem longa (mais de 30 min)"
        // Removemos isso ANTES de qualquer busca numérica
        var cleanText = rawText.lowercase()
            .replace("mais de 30 min", "")
            .replace("mais de 30min", "")
            .replace("longa", "") 
            .replace("[^0-9a-zA-Z$,. ]".toRegex(), " ") // Limpa caracteres estranhos

        val prices = ArrayList<Double>()
        val dists = ArrayList<Double>()
        val times = ArrayList<Double>()

        // 2. PREÇOS (R$)
        // Aceita formatos: R$ 10, 10,50, 10.5
        val pm = Pattern.compile("(?:r\\$|rs|\\$)\\s*([0-9]+(?:[.,][0-9]{0,2})?)")
        val matP = pm.matcher(cleanText)
        while (matP.find()) {
            val v = matP.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            // Filtro de segurança: ignora taxas de cancelamento (~4.00) e erros (>2000)
            if (v > 4.5 && v < 2000.0) prices.add(v)
        }

        // 3. DISTÂNCIAS (KM)
        val dm = Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*(km|m)(?!in)")
        val matD = dm.matcher(cleanText)
        while (matD.find()) {
            var d = matD.group(1)?.replace(",", ".")?.toDoubleOrNull() ?: 0.0
            val unit = matD.group(2)
            if (unit == "m") d /= 1000.0
            // Filtro de segurança: distâncias > 0.1km e < 400km
            if (d > 0.1 && d < 400.0) dists.add(d)
        }

        // 4. TEMPO (HORAS E MINUTOS - REFINADO)
        // Regex para capturar horas: "1 h 10 min", "1h", "2 h"
        val tmH = Pattern.compile("([0-9]+)\\s*h\\s*(?:([0-9]+)\\s*min)?")
        val matH = tmH.matcher(cleanText)
        while (matH.find()) {
            val h = matH.group(1)?.toIntOrNull() ?: 0
            val m = matH.group(2)?.toIntOrNull() ?: 0
            val totalMinutes = (h * 60) + m
            if (totalMinutes > 0) times.add(totalMinutes.toDouble())
        }
        
        // Removemos do texto o que já foi lido como hora para não duplicar na leitura de minutos
        cleanText = matH.replaceAll(" ") 

        // Regex para capturar minutos restantes: "45 min", "10 min"
        val tmM = Pattern.compile("([0-9]+)\\s*min")
        val matM = tmM.matcher(cleanText)
        while (matM.find()) {
            val m = matM.group(1)?.toDoubleOrNull() ?: 0.0
            if (m > 0) times.add(m)
        }

        // --- HIERARQUIA ESTRITA ---
        
        // Regra: Precisamos de pelo menos 2 tempos e 2 distâncias (Viagem + Busca)
        if (prices.isEmpty() || dists.size < 2 || times.size < 2) {
            return false 
        }

        // Ordenar decrescente (Maiores primeiro)
        prices.sortDescending()
        dists.sortDescending()
        times.sortDescending()

        // Pegamos os valores (Lógica: Soma dos 2 maiores para Tempo/Dist, Maior valor para Preço)
        val finalPrice = prices[0]
        val finalDist = dists[0] + dists[1]
        val finalTime = times[0] + times[1]

        if (finalPrice > 0 && finalDist > 0 && finalTime > 0) {
            lastValidReadTime = System.currentTimeMillis()

            // Só atualiza se mudar algo relevante (estabilidade visual)
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

    # Substituição Segura do Método Inteiro
    start_marker = "private fun analyzeScreen(rawText: String): Boolean {"
    end_marker = "override fun onDestroy()"
    
    start_idx = ocr_content.find(start_marker)
    if start_idx != -1:
        end_idx = ocr_content.find(end_marker, start_idx)
        if end_idx != -1:
            # Substitui o bloco antigo pelo novo
            ocr_content = ocr_content[:start_idx] + new_analyze_logic + "\n\n    " + ocr_content[end_idx:]
            write_file(ocr_path, ocr_content)
        else:
            print("❌ Erro: Não encontrei o fim do método em OcrService.kt")
    else:
        print("❌ Erro: Método analyzeScreen não encontrado.")

# ==============================================================================
# 2. ATUALIZAR WEBVIEW (MainActivity.kt - Download Listener)
# ==============================================================================
print("\n📱 Habilitando Downloads no App...")
main_path = find_file("MainActivity.kt")

if main_path:
    with open(main_path, 'r', encoding='utf-8') as f:
        main_content = f.read()

    # Código do Download Listener
    # Verifica se já existe para não duplicar
    if "setDownloadListener" not in main_content:
        # Ponto de inserção: Logo após habilitar o JavaScript
        anchor = 'webView.settings.userAgentString = webView.settings.userAgentString + " MotoristaProApp"'
        
        listener_code = """
        webView.settings.userAgentString = webView.settings.userAgentString + " MotoristaProApp"
        
        // --- HABILITAR DOWNLOADS ---
        webView.setDownloadListener { url, userAgent, contentDisposition, mimetype, contentLength ->
            try {
                val i = Intent(Intent.ACTION_VIEW)
                i.data = Uri.parse(url)
                startActivity(i)
                Toast.makeText(this, "Iniciando download...", Toast.LENGTH_LONG).show()
            } catch (e: Exception) {
                Toast.makeText(this, "Erro ao abrir download.", Toast.LENGTH_SHORT).show()
            }
        }"""
        
        if anchor in main_content:
            main_content = main_content.replace(anchor, listener_code.strip())
            write_file(main_path, main_content)
        else:
            print("⚠️ Erro: Não encontrei o ponto de inserção no MainActivity.kt. Verifique manualmente.")
    else:
        print("ℹ️ DownloadListener já estava configurado.")

# ==============================================================================
# 3. GIT PUSH AUTOMÁTICO
# ==============================================================================
print("\n🚀 Enviando atualizações para o GitHub...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "Fix: OCR Filters (30min bug) & App Downloads"', shell=True, check=True)
    subprocess.run("git push", shell=True, check=True)
    print("\n✅ Atualização concluída com sucesso!")
except Exception as e:
    print(f"\n❌ Erro no Git: {e}")


