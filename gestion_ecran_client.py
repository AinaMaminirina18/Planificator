from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

def gestion_ecran_client(manager):
    manager.add_widget(Builder.load_file(f'screen/client/option_client.kv'))
    manager.add_widget(Builder.load_file(f'screen/client/modification_client.kv'))
