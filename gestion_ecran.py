from kivy.lang.builder import Builder
from kivy.uix.screenmanager import SlideTransition


def gestion_ecran(root):
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/contrat.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/Home.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/planning.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/about.kv'))
    root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/Client.kv'))

    root.get_screen('Sidebar').ids['gestion_ecran'].transition = SlideTransition(direction='up')