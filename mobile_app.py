"""
Divine-Earthly Mobile App — Unified Entry Point
Bundles Krishi-Veda + Water Guardian in one APK.
Auto-updates new features from GitHub releases.
"""
import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.webview import WebView
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import json
import os
import zipfile
import shutil

# Config
GITHUB_API = "https://api.github.com/repos/divineearthly/Krishi-Veda-Module/releases/latest"
HF_KRISHI_URL = "https://divinesouljoy-krishi-veda.hf.space"
HF_WATER_URL = "https://divinesouljoy-water-guardian.hf.space"
LOCAL_KRISHI_DIR = "/sdcard/DivineEarthly/krishi_veda"
LOCAL_WATER_DIR = "/sdcard/DivineEarthly/water_guardian"
UPDATE_CHECK_INTERVAL = 86400  # 24 hours


class MainScreen(Screen):
    """Home screen with both app modules."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        header = Label(
            text='🕉️ Divine-Earthly',
            font_size='24sp',
            size_hint=(1, 0.1),
            color=(0.18, 0.42, 0.31, 1)  # #2d6a4f
        )
        layout.add_widget(header)
        
        subheader = Label(
            text='Sovereign AI for Farmers & Communities',
            font_size='14sp',
            size_hint=(1, 0.05),
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(subheader)
        
        # Krishi-Veda Button
        krishi_btn = Button(
            text='🌾 Krishi-Veda\nFarming Advice & Crop Intelligence',
            size_hint=(1, 0.2),
            background_color=(0.18, 0.42, 0.31, 1),
            halign='center',
            valign='middle'
        )
        krishi_btn.bind(on_press=self.open_krishi)
        layout.add_widget(krishi_btn)
        
        # Water Guardian Button
        water_btn = Button(
            text='🛡️ Water Guardian\nWater Quality & Satellite Monitoring',
            size_hint=(1, 0.2),
            background_color=(0.12, 0.35, 0.55, 1),
            halign='center',
            valign='middle'
        )
        water_btn.bind(on_press=self.open_water)
        layout.add_widget(water_btn)
        
        # Offline Status
        self.status_label = Label(
            text='📡 Checking connectivity...',
            font_size='12sp',
            size_hint=(1, 0.1),
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status_label)
        
        # Update button
        update_btn = Button(
            text='🔄 Check for Updates',
            size_hint=(1, 0.1),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        update_btn.bind(on_press=self.check_updates)
        layout.add_widget(update_btn)
        
        # Footer
        footer = Label(
            text='🕉️ Divine-Earthly © 2025\nServing all living beings',
            font_size='10sp',
            size_hint=(1, 0.1),
            color=(0.4, 0.4, 0.4, 1)
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
    
    def open_krishi(self, instance):
        """Open Krishi-Veda PWA."""
        self.manager.current = 'krishi_veda'
    
    def open_water(self, instance):
        """Open Water Guardian."""
        self.manager.current = 'water_guardian'
    
    def check_updates(self, instance):
        """Check GitHub for new releases."""
        self.status_label.text = '🔄 Checking for updates...'
        
        def on_success(req, result):
            try:
                latest_version = result.get('tag_name', '')
                current_version = '1.0.0'
                
                if latest_version > current_version:
                    self.status_label.text = f'⬆️ Update available: {latest_version}'
                    # Download update
                    assets = result.get('assets', [])
                    for asset in assets:
                        if asset['name'].endswith('.zip'):
                            self.download_update(asset['browser_download_url'])
                            break
                else:
                    self.status_label.text = '✅ You have the latest version'
            except Exception:
                self.status_label.text = '✅ Using offline mode'
        
        def on_error(req, error):
            self.status_label.text = '📵 Offline — using cached data'
        
        UrlRequest(GITHUB_API, on_success=on_success, on_error=on_error, timeout=10)
    
    def download_update(self, url):
        """Download and apply update."""
        self.status_label.text = '⬇️ Downloading update...'
        
        def on_success(req, result):
            update_path = '/sdcard/DivineEarthly/update.zip'
            with open(update_path, 'wb') as f:
                f.write(result)
            
            self.status_label.text = '📦 Installing update...'
            
            # Extract update
            extract_dir = '/sdcard/DivineEarthly/update_temp'
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.makedirs(extract_dir)
            
            with zipfile.ZipFile(update_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Apply updated files
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    src = os.path.join(root, file)
                    rel_path = os.path.relpath(src, extract_dir)
                    dst = os.path.join(LOCAL_KRISHI_DIR, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
            
            shutil.rmtree(extract_dir)
            os.remove(update_path)
            self.status_label.text = '✅ Update installed! Restart app.'
        
        def on_error(req, error):
            self.status_label.text = '❌ Update failed — try later'
        
        UrlRequest(url, on_success=on_success, on_error=on_error, timeout=300)


class KrishiVedaScreen(Screen):
    """Krishi-Veda PWA WebView."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # WebView loading Krishi-Veda PWA
        self.webview = WebView(
            url=HF_KRISHI_URL,
            enable_javascript=True,
            enable_zoom=True
        )
        layout.add_widget(self.webview)
        
        # Back button
        back_btn = Button(
            text='← Back to Home',
            size_hint=(1, 0.08),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'


class WaterGuardianScreen(Screen):
    """Water Guardian WebView."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.webview = WebView(
            url=HF_WATER_URL,
            enable_javascript=True,
            enable_zoom=True
        )
        layout.add_widget(self.webview)
        
        back_btn = Button(
            text='← Back to Home',
            size_hint=(1, 0.08),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'


class DivineEarthlyApp(App):
    """Main Divine-Earthly Android App."""
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(KrishiVedaScreen(name='krishi_veda'))
        sm.add_widget(WaterGuardianScreen(name='water_guardian'))
        return sm
    
    def on_start(self):
        """Check for updates on app start."""
        Clock.schedule_once(lambda dt: self.check_first_update(), 3)
    
    def check_first_update(self):
        main_screen = self.root.get_screen('main')
        main_screen.check_updates(None)


if __name__ == '__main__':
    DivineEarthlyApp().run()
