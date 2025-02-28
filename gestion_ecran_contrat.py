from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

def gestion_ecran_contrat(manager):
    manager.add_widget(Builder.load_file(f'screen/option_contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/new-contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/suppr_contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/option_client.kv'))
