from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

def gestion_ecran_planning(manager):
    manager.add_widget(Builder.load_file(f'screen/rendu_planning.kv'))
