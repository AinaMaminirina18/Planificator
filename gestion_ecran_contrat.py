from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

def gestion_ecran_contrat(manager):
    manager.add_widget(Builder.load_file(f'screen/contrat/option_contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/contrat/new-contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/contrat/suppr_contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/client/ajout_info_client.kv'))
    manager.add_widget(Builder.load_file(f'screen/client/save_info_client.kv'))
    manager.add_widget(Builder.load_file(f'screen/contrat/ajout_planning_contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/contrat/facture_contrat.kv'))
    manager.add_widget(Builder.load_file(f'screen/contrat/about_treatment.kv'))
