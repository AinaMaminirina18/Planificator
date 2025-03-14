from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

def gestion_ecran_planning(manager):
    manager.add_widget(Builder.load_file(f'screen/planning/rendu_planning.kv'))
    manager.add_widget(Builder.load_file(f'screen/planning/option_decalage.kv'))
    manager.add_widget(Builder.load_file(f'screen/planning/ecran_decalage.kv'))
    manager.add_widget(Builder.load_file(f'screen/planning/selection_planning.kv'))
    manager.add_widget(Builder.load_file(f'screen/planning/selection_tableau.kv'))
    manager.add_widget(Builder.load_file(f'screen/planning/ajout_remarque.kv'))
