import sys, os, json, re, zipfile, unicodedata
from html import escape

src, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
cfg = json.loads(z.read('config.json'))

name = cfg.get('name') or 'App'
pk = cfg.get('package', '')
if not re.fullmatch(r'[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+', pk):
    sys.exit('Pacote inválido: ' + pk)
ori = cfg.get('orientation', '')
if ori not in ('', 'sensorLandscape', 'portrait'):
    ori = ''
start = re.sub(r'["\\\s]', '', cfg.get('start') or 'index.html')
has_icon = 'icon.png' in z.namelist()


def w(path, data):
    p = os.path.join(out, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode('utf-8'))


w('settings.gradle', """pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositories { google(); mavenCentral() } }
rootProject.name = "App"
include ':app'
""")
w('build.gradle', "plugins { id 'com.android.application' version '8.5.2' apply false }\n")
w('gradle.properties', "android.useAndroidX=true\norg.gradle.jvmargs=-Xmx2048m\n")

w('app/build.gradle', f"""plugins {{ id 'com.android.application' }}
android {{
  namespace '{pk}'
  compileSdk 34
  defaultConfig {{
    applicationId '{pk}'
    minSdk 21
    targetSdk 34
    versionCode 1
    versionName '1.0'
  }}
  compileOptions {{
    sourceCompatibility JavaVersion.VERSION_17
    targetCompatibility JavaVersion.VERSION_17
  }}
}}
dependencies {{ implementation 'androidx.webkit:webkit:1.11.0' }}
""")

icon_attr = ' android:icon="@mipmap/ic_launcher"' if has_icon else ''
ori_attr = f' android:screenOrientation="{ori}"' if ori else ''
w('app/src/main/AndroidManifest.xml', f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
<uses-permission android:name="android.permission.INTERNET"/>
<application android:label="{escape(name, quote=True)}"{icon_attr} android:allowBackup="false" android:usesCleartextTraffic="true" android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
<activity android:name=".MainActivity" android:exported="true"{ori_attr} android:configChanges="orientation|screenSize|keyboardHidden|smallestScreenSize|screenLayout|uiMode">
<intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
</activity>
</application>
</manifest>
""")

w(f"app/src/main/java/{pk.replace('.', '/')}/MainActivity.java", f"""package {pk};

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.*;
import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {{
  private WebView w;

  @Override protected void onCreate(Bundle s) {{
    super.onCreate(s);
    if (Build.VERSION.SDK_INT >= 28) getWindow().getAttributes().layoutInDisplayCutoutMode = 1;
    final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
      .addPathHandler("/", new WebViewAssetLoader.AssetsPathHandler(this)).build();
    w = new WebView(this);
    w.setBackgroundColor(0xFF000000);
    WebSettings t = w.getSettings();
    t.setJavaScriptEnabled(true);
    t.setDomStorageEnabled(true);
    t.setMediaPlaybackRequiresUserGesture(false);
    t.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
    w.setWebChromeClient(new WebChromeClient());
    w.setWebViewClient(new WebViewClient() {{
      @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {{
        return loader.shouldInterceptRequest(r.getUrl());
      }}
    }});
    setContentView(w);
    w.loadUrl("https://appassets.androidplatform.net/www/{start}");
  }}

  @Override public void onWindowFocusChanged(boolean f) {{
    super.onWindowFocusChanged(f);
    if (f) getWindow().getDecorView().setSystemUiVisibility(
      View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN
      | View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
  }}

  @Override public void onBackPressed() {{ if (w.canGoBack()) w.goBack(); else super.onBackPressed(); }}
  @Override protected void onPause() {{ super.onPause(); w.onPause(); }}
  @Override protected void onResume() {{ super.onResume(); w.onResume(); }}
  @Override protected void onDestroy() {{ w.destroy(); super.onDestroy(); }}
}}
""")

if has_icon:
    w('app/src/main/res/mipmap-xxxhdpi/ic_launcher.png', z.read('icon.png'))

n = 0
for info in z.infolist():
    nm = info.filename
    if not nm.startswith('www/') or nm.endswith('/') or '..' in nm.split('/'):
        continue
    w('app/src/main/assets/' + nm, z.read(info))
    n += 1
if n == 0:
    sys.exit('Nenhum arquivo do jogo dentro do zip')

slug = re.sub(r'[^A-Za-z0-9]+', '-', unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()).strip('-') or 'app'
w('apk_name.txt', slug)
print('Projeto gerado:', n, 'arquivos do jogo,', pk)
