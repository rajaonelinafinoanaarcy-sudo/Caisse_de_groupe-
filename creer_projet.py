#!/usr/bin/env python3
"""Cree le projet Android (WebView) autour de index.html, puis Gradle construit l'APK."""
import os, base64

FILES = {
    'settings.gradle': r'''pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "CaisseDuGroupe"
include ':app'
''',
    'build.gradle': r'''plugins {
    id 'com.android.application' version '8.5.2' apply false
}
''',
    'gradle.properties': r'''org.gradle.jvmargs=-Xmx2g
android.useAndroidX=true
''',
    'app/build.gradle': r'''plugins {
    id 'com.android.application'
}

android {
    namespace 'mg.caisse.groupe'
    compileSdk 34

    defaultConfig {
        applicationId "mg.caisse.groupe"
        minSdk 29
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release { minifyEnabled false }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}

dependencies {
    implementation 'androidx.webkit:webkit:1.11.0'
}
''',
    'app/src/main/AndroidManifest.xml': r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        android:label="Caisse du groupe"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
''',
    'app/src/main/java/mg/caisse/groupe/MainActivity.java': r'''package mg.caisse.groupe;

import android.app.Activity;
import android.content.ContentValues;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.webkit.WebViewAssetLoader;

import java.io.OutputStream;

public class MainActivity extends Activity {
    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.parseColor("#0A6B3C"));

        web = new WebView(this);
        setContentView(web);

        // Sert les fichiers de assets/ sur une adresse https interne, pour que localStorage fonctionne
        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);

        web.addJavascriptInterface(new Bridge(), "AndroidBridge");
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
        });
        web.loadUrl("https://appassets.androidplatform.net/assets/www/index.html");
    }

    // Permet d'enregistrer le rapport CSV dans le dossier Téléchargements
    private class Bridge {
        @JavascriptInterface
        public void saveFile(final String name, final String content) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        ContentValues v = new ContentValues();
                        v.put(MediaStore.Downloads.DISPLAY_NAME, name);
                        v.put(MediaStore.Downloads.MIME_TYPE, "text/csv");
                        v.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
                        OutputStream out = getContentResolver().openOutputStream(uri);
                        out.write(content.getBytes("UTF-8"));
                        out.close();
                        Toast.makeText(MainActivity.this, "Rapport enregistré dans Téléchargements", Toast.LENGTH_LONG).show();
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "Échec de l'enregistrement du rapport", Toast.LENGTH_LONG).show();
                    }
                }
            });
        }
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }
}
''',
}

ICON_B64 = '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'

def write(path, data, binary=False):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    if binary:
        open(path, 'wb').write(data)
    else:
        open(path, 'w', encoding='utf-8').write(data)

for path, content in FILES.items():
    write(path, content)

write('app/src/main/assets/www/index.html', open('index.html', encoding='utf-8').read())
write('app/src/main/res/mipmap-xxxhdpi/ic_launcher.png', base64.b64decode(ICON_B64), True)
print('Projet Android cree.')
