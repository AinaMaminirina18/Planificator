from kivy.lang.builder import Builder
from kivy.uix.screenmanager import SlideTransition


def gestion_ecran(root):
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/Home.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/historique/historique.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/contrat/contrat.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/planning/planning.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/about.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/client/Client.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/compte/compte.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/compte/compte_not_admin.kv'))

    root.get_screen('Sidebar').ids['gestion_ecran'].transition = SlideTransition(direction='up')
