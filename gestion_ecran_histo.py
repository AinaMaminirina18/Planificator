from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

def gestion_ecran_histo(manager):
    manager.add_widget(Builder.load_file(f'screen/option_histo.kv'))
