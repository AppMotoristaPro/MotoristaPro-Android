package com.motoristapro.android

import android.Manifest
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.AlertDialog
import android.app.Dialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Message
import android.provider.Settings
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.view.accessibility.AccessibilityManager
import android.webkit.CookieManager
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessaging

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean -> }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        setupWebView()
        askNotificationPermission()
    }

    private fun askNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) !=
                PackageManager.PERMISSION_GRANTED) {
                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.setSupportMultipleWindows(true)
        settings.javaScriptCanOpenWindowsAutomatically = true
        
        val userAgent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
        settings.userAgentString = userAgent
        
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true

        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }

        webView.addJavascriptInterface(WebAppInterface(this), "MotoristaProAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                if (url.startsWith("whatsapp:") || url.startsWith("tel:") || url.startsWith("mailto:")) {
                    try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch (e: Exception) {}
                    return true 
                }
                return false 
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onCreateWindow(view: WebView?, isDialog: Boolean, isUserGesture: Boolean, resultMsg: Message?): Boolean {
                val newWebView = WebView(this@MainActivity)
                val newSettings = newWebView.settings
                newSettings.javaScriptEnabled = true
                newSettings.domStorageEnabled = true
                newSettings.setSupportMultipleWindows(true)
                newSettings.javaScriptCanOpenWindowsAutomatically = true
                newSettings.userAgentString = userAgent

                val cookieManagerPopup = CookieManager.getInstance()
                cookieManagerPopup.setAcceptCookie(true)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    cookieManagerPopup.setAcceptThirdPartyCookies(newWebView, true)
                }
                
                val dialog = Dialog(this@MainActivity)
                dialog.setContentView(newWebView)
                dialog.window?.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
                dialog.show()

                newWebView.webChromeClient = object : WebChromeClient() {
                    override fun onCloseWindow(window: WebView?) { dialog.dismiss() }
                }

                val transport = resultMsg?.obj as? WebView.WebViewTransport
                if (transport != null) {
                    transport.webView = newWebView
                    resultMsg.sendToTarget()
                }
                return true
            }
        }

        webView.loadUrl("https://motorista-pro-app.onrender.com")
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    // --- INTERFACE JAVASCRIPT ---
    class WebAppInterface(private val activity: MainActivity) {
        
        @JavascriptInterface
        fun hasOverlayPermission(): Boolean {
            return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                Settings.canDrawOverlays(activity)
            } else true
        }

        @JavascriptInterface
        fun openOverlaySettings() {
            activity.runOnUiThread {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:${activity.packageName}"))
                    activity.startActivity(intent)
                }
            }
        }

        @JavascriptInterface
        fun hasAccessibilityPermission(): Boolean {
            val am = activity.getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
            val enabledServices = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_GENERIC)
            for (service in enabledServices) {
                if (service.resolveInfo.serviceInfo.packageName == activity.packageName) return true
            }
            return false
        }

        @JavascriptInterface
        fun openAccessibilitySettings() {
            activity.runOnUiThread {
                val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                activity.startActivity(intent)
            }
        }

        @JavascriptInterface
        fun startRobot() {
            activity.runOnUiThread { 
                val intent = Intent(activity, OcrService::class.java)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    activity.startForegroundService(intent)
                } else {
                    activity.startService(intent)
                }
                Toast.makeText(activity, "🚀 Robô Iniciado!", Toast.LENGTH_SHORT).show()
            }
        }

        @JavascriptInterface
        fun subscribeToPush(userId: String) {
            FirebaseMessaging.getInstance().subscribeToTopic("all_users")
            FirebaseMessaging.getInstance().subscribeToTopic("user_$userId")
        }
    }
}
