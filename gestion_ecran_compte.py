from kivy.lang.builder import Builder


def gestion_ecran_compte(manager):
    manager.add_widget(Builder.load_file('screen/about_compte.kv'))
    manager.add_widget(Builder.load_file('screen/suppr_compte.kv'))
    manager.add_widget(Builder.load_file('screen/modif_compte.kv'))
