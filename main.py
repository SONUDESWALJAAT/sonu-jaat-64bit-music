import os
import shutil
from mutagen.mp3 import MP3
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.card import MDCard

class Tab(MDBoxLayout, MDTabsBase):
    pass

class AudioSorterApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"
        
        screen = Screen()
        main_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        main_layout.add_widget(MDLabel(
            text="🎵 SONU JAAT music Tester", 
            font_style="H5", 
            halign="center",
            size_hint_y=None, 
            height=50,
            theme_text_color="Custom",
            text_color=(0.7, 0.2, 1, 1)
        ))
        
        self.source_input = MDTextField(hint_text="गाने वाले फोल्डर का पाथ (Source Path)", text="/sdcard/Music")
        self.target_input = MDTextField(hint_text="टार्गेट फोल्डर का पाथ (Target Path)", text="/sdcard/SortedMusic")
        main_layout.add_widget(self.source_input)
        main_layout.add_widget(self.target_input)
        
        btn_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        scan_btn = MDRaisedButton(text="🔍 स्कैन करें", on_release=self.scan_songs)
        clear_btn = MDRaisedButton(text="🧹 क्लियर लिस्ट", md_bg_color=(0.7, 0.1, 0.1, 1), on_release=self.clear_all)
        btn_layout.add_widget(scan_btn)
        btn_layout.add_widget(clear_btn)
        main_layout.add_widget(btn_layout)
        
        self.tabs = MDTabs()
        main_layout.add_widget(self.tabs)
        
        screen.add_widget(main_layout)
        self.audio_data = {}
        return screen

    def clear_all(self, *args):
        self.tabs.clear_widgets()
        self.audio_data = {}

    def scan_songs(self, *args):
        self.clear_all()
        source_dir = self.source_input.text
        
        if not os.path.exists(source_dir):
            return
            
        bitrate_buckets = {"128 kbps": [], "192 kbps": [], "320 kbps": [], "Others": []}
        try:
            files = [f for f in os.listdir(source_dir) if f.lower().endswith('.mp3')]
        except Exception:
            return
        
        for file in files:
            file_path = os.path.join(source_dir, file)
            size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            
            try:
                audio = MP3(file_path)
                bitrate_kbps = int(audio.info.bitrate / 1000)
                
                if bitrate_kbps == 128: bucket = "128 kbps"
                elif bitrate_kbps == 192: bucket = "192 kbps"
                elif bitrate_kbps == 320: bucket = "320 kbps"
                else: bucket = "Others"
            except:
                bucket = "Others"
                
            bitrate_buckets[bucket].append({"name": file, "path": file_path, "size": f"{size_mb} MB"})
            
        self.audio_data = {k: v for k, v in bitrate_buckets.items() if v}
        self.update_ui()

    def update_ui(self):
        for bucket, songs in self.audio_data.items():
            tab = Tab(title=f"{bucket} ({len(songs)})", orientation='vertical', padding=10, spacing=10)
            
            bulk_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
            cp_all = MDRaisedButton(text="Copy All", on_release=lambda x, b=bucket: self.bulk_action(b, "copy"))
            mv_all = MDRaisedButton(text="Move All", on_release=lambda x, b=bucket: self.bulk_action(b, "move"))
            bulk_layout.add_widget(cp_all)
            bulk_layout.add_widget(mv_all)
            tab.add_widget(bulk_layout)
            
            scroll = ScrollView()
            grid = MDGridLayout(cols=1, spacing=10, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            for idx, song in enumerate(songs):
                card = MDCard(orientation='horizontal', padding=10, size_hint_y=None, height=70, md_bg_color=(0.2,0.2,0.2,1))
                
                text_layout = MDBoxLayout(orientation='vertical')
                text_layout.add_widget(MDLabel(text=song['name'], font_style="Subtitle1", theme_text_color="Custom", text_color=(1,1,1,1)))
                text_layout.add_widget(MDLabel(text=song['size'], font_style="Caption", theme_text_color="Hint"))
                card.add_widget(text_layout)
                
                btn_box = MDBoxLayout(orientation='horizontal', size_hint_x=None, width=100, spacing=5)
                del_btn = MDIconButton(icon="delete", theme_text_color="Custom", text_color=(1,0,0,1), on_release=lambda x, s=song, b=bucket, i=idx: self.delete_song(s, b, i))
                cp_btn = MDIconButton(icon="content-copy", theme_text_color="Custom", text_color=(0,1,0,1), on_release=lambda x, s=song: self.copy_single(s))
                
                btn_box.add_widget(cp_btn)
                btn_box.add_widget(del_btn)
                card.add_widget(btn_box)
                
                grid.add_widget(card)
                
            scroll.add_widget(grid)
            tab.add_widget(scroll)
            self.tabs.add_widget(tab)

    def copy_single(self, song):
        target_dir = self.target_input.text
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(song['path'], os.path.join(target_dir, song['name']))

    def delete_song(self, song, bucket, idx):
        if os.path.exists(song['path']):
            os.remove(song['path'])
            self.audio_data[bucket].pop(idx)
            self.scan_songs()

    def bulk_action(self, bucket, action_type):
        target_dir = os.path.join(self.target_input.text, bucket.replace(" ", "_"))
        if not self.target_input.text: return
        os.makedirs(target_dir, exist_ok=True)
        
        for song in self.audio_data[bucket]:
            if action_type == "copy":
                shutil.copy(song['path'], os.path.join(target_dir, song['name']))
            elif action_type == "move":
                shutil.move(song['path'], os.path.join(target_dir, song['name']))
                
        self.scan_songs()

if __name__ == '__main__':
    AudioSorterApp().run()
