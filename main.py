"""
KRISHI-VEDA ANDROID APP
"""
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import threading

Window.size = (400, 700)

class KrishiVedaApp(App):
    def build(self):
        self.title = 'Krishi-Veda'
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Header
        layout.add_widget(Label(
            text='🌾 Krishi-Veda',
            font_size='22sp',
            size_hint_y=None, height=45,
            color=(0.18, 0.31, 0.09, 1)
        ))
        
        # Input
        self.input = TextInput(
            hint_text='Ask your farming question...',
            size_hint_y=None, height=45,
            multiline=False
        )
        layout.add_widget(self.input)
        
        # Button
        btn = Button(
            text='Get Advice',
            size_hint_y=None, height=50,
            background_color=(0.18, 0.31, 0.09, 1)
        )
        btn.bind(on_press=self.ask)
        layout.add_widget(btn)
        
        # Response
        self.response = Label(
            text='Your agricultural advice will appear here...',
            size_hint_y=None, height=400,
            text_size=(380, None),
            halign='left', valign='top',
            color=(0.1, 0.1, 0.1, 1)
        )
        scroll = ScrollView()
        scroll.add_widget(self.response)
        layout.add_widget(scroll)
        
        # Status
        self.status = Label(
            text='🟢 Ready | Offline Mode',
            size_hint_y=None, height=30,
            font_size='10sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status)
        
        return layout
    
    def ask(self, instance):
        query = self.input.text.strip()
        if not query:
            self.response.text = 'Please enter a question.'
            return
        
        self.status.text = '⏳ Getting advice...'
        
        def get_advice():
            try:
                r = requests.get(
                    'http://localhost:5000/ask',
                    params={'query': query},
                    timeout=30
                )
                data = r.json()
                advice = data.get('advice', 'No advice available.')
                vedic = data.get('vedic', {})
                
                text = f"{advice}\n\n"
                text += f"Wellness: {vedic.get('wellness', 'N/A')} | "
                text += f"Stress: {vedic.get('stress_code', 'N/A')}"
                
                self.response.text = text
                self.status.text = '🟢 Ready | 0ms response'
            except Exception as e:
                self.response.text = f'Error: {str(e)}\n\nMake sure Krishi-Veda server is running.'
                self.status.text = '🔴 Error'
        
        threading.Thread(target=get_advice).start()

if __name__ == '__main__':
    KrishiVedaApp().run()
