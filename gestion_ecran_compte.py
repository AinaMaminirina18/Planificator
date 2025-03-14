from kivy.lang.builder import Builder


def gestion_ecran_compte(manager):
    manager.add_widget(Builder.load_file('screen/compte/about_compte.kv'))
    manager.add_widget(Builder.load_file('screen/compte/suppr_compte.kv'))
    manager.add_widget(Builder.load_file('screen/compte/modif_compte.kv'))
