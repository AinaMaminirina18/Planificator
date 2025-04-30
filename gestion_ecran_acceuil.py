from kivy.lang.builder import Builder


def gestion_ecran_home(manager):
    manager.add_widget(Builder.load_file('screen/about_contrat.kv'))
    manager.add_widget(Builder.load_file('screen/Facture.kv'))
