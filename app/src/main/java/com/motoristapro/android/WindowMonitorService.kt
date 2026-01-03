package com.motoristapro.android

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.ColorMatrix
import android.graphics.ColorMatrixColorFilter
import android.graphics.Paint
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.Display
import android.view.accessibility.AccessibilityEvent
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import org.json.JSONArray
import org.json.JSONObject
import android.graphics.Color

class WindowMonitorService : AccessibilityService() {

    private val executor: ExecutorService = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private var lastCaptureTime = 0L
    
    private val CAPTURE_COOLDOWN = 1000L 
    private val DELAY_FAST = 500L
    private val DELAY_RETRY = 1200L
    
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    override fun onServiceConnected() {
        super.onServiceConnected()
        warmUpOcrEngine()
    }

    private fun warmUpOcrEngine() {
        executor.execute {
            try {
                val dummy = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888)
                val image = InputImage.fromBitmap(dummy, 0)
        Logger.log("MLKIT", "Enviando imagem para ML Kit Vision...")
                recognizer.process(image)
            } catch (e: Exception) { e.printStackTrace() }
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null || event.packageName == null) return
        val pkgName = event.packageName.toString()

        if (pkgName.contains("uber") || pkgName.contains("99")) {
            if (event.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ||
                event.eventType == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED) {
                
                triggerCaptureLogic(pkgName)
            }
        }
    }

    private fun triggerCaptureLogic(pkgName: String) {
        Logger.log("MONITOR", "Gatilho de captura acionado para $pkgName")
        val now = System.currentTimeMillis()
        if (now - lastCaptureTime > CAPTURE_COOLDOWN) {
            lastCaptureTime = now
            scheduleScreenshot(DELAY_FAST, pkgName, isRetry = false)
        }
    }

    private fun scheduleScreenshot(delay: Long, pkgName: String, isRetry: Boolean) {
        mainHandler.postDelayed({
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                
                // FORÇAR OCULTAR CARD (Fix Duplicação)
                try { 
                    sendBroadcast(Intent("com.motoristapro.ACTION_HIDE_CARD"))
                    Thread.sleep(300) 
                } catch(e: Exception) {}

                takeScreenshot(
                    Display.DEFAULT_DISPLAY,
                    executor,
                    object : TakeScreenshotCallback {
                        override fun onSuccess(result: ScreenshotResult) {
                            try {
                                val hardwareBuffer = result.hardwareBuffer
                                val colorSpace = result.colorSpace
                                val bitmap = Bitmap.wrapHardwareBuffer(hardwareBuffer, colorSpace)
                                val copy = bitmap?.copy(Bitmap.Config.ARGB_8888, true)
                                hardwareBuffer.close()
                                
                                if (copy != null) {
                                    // APLICA FILTRO AVANÇADO (BINARIZAÇÃO)
                                    val processedBitmap = preprocessAdvanced(copy)
                                    runOcr(processedBitmap, pkgName, isRetry)
                                }
                            } catch (e: Exception) {
                                Log.e("MotoristaPro", "Erro print: ${e.message}")
                            }
                        }
                        override fun onFailure(errorCode: Int) {}
                    }
                )
            }
        }, delay)
    }

    // === MELHORIA 1: VISÃO DE ALTA PRECISÃO ===
    private fun preprocessAdvanced(original: Bitmap): Bitmap {
        try {
            val width = original.width
            val height = original.height
            val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bitmap)
            val paint = Paint()

            // 1. Detectar se é Modo Noturno (Média de brilho)
            // Se for escuro, INVERTE as cores para ficar Fundo Branco/Letra Preta (OCR prefere assim)
            var isDark = false
            // Amostragem simples no centro da imagem
            val samplePixel = original.getPixel(width / 2, height / 2)
            val lum = (0.299 * Color.red(samplePixel) + 0.587 * Color.green(samplePixel) + 0.114 * Color.blue(samplePixel)) / 255
            if (lum < 0.5) isDark = true

            // Matriz de Cor
            val colorMatrix = ColorMatrix()
            
            // Passo A: Escala de Cinza
            colorMatrix.setSaturation(0f) 

            // Passo B: Alto Contraste (Thresholding via Matriz)
            // Aumenta drasticamente o contraste para 'matar' cinzas médios
            val contrast = 4.0f 
            val scale = floatArrayOf(
                contrast, 0f, 0f, 0f, -128f * contrast + 128f,
                0f, contrast, 0f, 0f, -128f * contrast + 128f,
                0f, 0f, contrast, 0f, -128f * contrast + 128f,
                0f, 0f, 0f, 1f, 0f
            )
            colorMatrix.postConcat(ColorMatrix(scale))

            // Passo C: Inversão (se for modo noturno)
            if (isDark) {
                val invert = floatArrayOf(
                    -1f, 0f, 0f, 0f, 255f,
                    0f, -1f, 0f, 0f, 255f,
                    0f, 0f, -1f, 0f, 255f,
                    0f, 0f, 0f, 1f, 0f
                )
                colorMatrix.postConcat(ColorMatrix(invert))
            }

            val filter = ColorMatrixColorFilter(colorMatrix)
            paint.colorFilter = filter
            canvas.drawBitmap(original, 0f, 0f, paint)

            return bitmap
        } catch (e: Exception) {
            return original // Fallback para imagem original se der erro
        }
    }

    private fun runOcr(bitmap: Bitmap, pkgName: String, isRetry: Boolean) {
        val image = InputImage.fromBitmap(bitmap, 0)
        val screenHeight = bitmap.height

        Logger.log("MLKIT", "Enviando imagem para ML Kit Vision...")
        recognizer.process(image)
            .addOnSuccessListener { visionText ->
                val jsonArray = JSONArray()
                
                for (block in visionText.textBlocks) {
                    for (line in block.lines) {
                        val bbox = line.boundingBox
                        if (bbox != null) {
                            val obj = JSONObject()
                            obj.put("text", line.text)
                            obj.put("h", bbox.height())
                            obj.put("y", bbox.top)
                            jsonArray.put(obj)
                        }
                    }
                }

                if (jsonArray.length() > 0) {
                    sendToOverlay(jsonArray.toString(), pkgName, screenHeight)
                } else if (!isRetry) {
                    scheduleScreenshot(DELAY_RETRY - DELAY_FAST, pkgName, true)
                }
            }
    }

    private fun sendToOverlay(jsonData: String, pkg: String, screenH: Int) {
        val intent = Intent("ACTION_PROCESS_TEXT")
        intent.putExtra("JSON_DATA", jsonData)
        intent.putExtra("APP_PACKAGE", pkg)
        intent.putExtra("SCREEN_HEIGHT", screenH)
        intent.setPackage(packageName)
        sendBroadcast(intent)
    }

    override fun onInterrupt() {}
    override fun onDestroy() { super.onDestroy(); executor.shutdown() }
}