from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel


class contrat(MDCard):
    def __init__(self, client, date_contrat, type_traitement, durée, debut_contrat, fin_prévu, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = ("300dp", "360dp")  # Taille ajustée
        self.padding = "8dp"
        self.elevation = 1
        self.orientation = "vertical"
        self.pos_hint= {"center_x": .5, "center_y": .7}
        self.md_bg_color= '#56B5FB'

        #informations
        info_conteneur = MDGridLayout(cols=1, padding=("0dp", "1dp", "0dp", "1dp"))

        info_conteneur.add_widget(MDLabel(text=f"Client : {client}", font_style="H6", halign="left"))
        info_conteneur.add_widget(MDLabel(text=f"Date du contrat : {date_contrat}", font_style="Subtitle1", halign="left"))
        info_conteneur.add_widget(MDLabel(text=f"Traitement(Type) : {type_traitement}", font_style="Subtitle1", halign="left"))
        info_conteneur.add_widget(MDLabel(text=f"Durée du contrat : {durée}", font_style="Subtitle1", halign="left"))
        info_conteneur.add_widget(MDLabel(text=f"Début du contrat : {debut_contrat}", font_style="Subtitle1", halign="left"))
        info_conteneur.add_widget(MDLabel(text=f"Fin prévu du contrat : {fin_prévu}", font_style="Subtitle1", halign="left"))

        #Conteneur principal
        conteneur_main = MDBoxLayout(orientation="vertical")

        #Bouton
        conteneur_btn = MDBoxLayout(size_hint_y=None, height="50dp", padding=("10dp", "80dp", "10dp", "30dp"))
        more_info_btn = MDRaisedButton(
            text="Plus d'informations",
            size_hint=(1, None),
            height="40dp",
            font_size= 17,
            md_bg_color= 'white',
            _default_text_color='black'
        )
        conteneur_btn.add_widget(more_info_btn)

        #Ajouter les éléments à la carte
        conteneur_main.add_widget(info_conteneur)
        conteneur_main.add_widget(conteneur_btn)
        self.add_widget(conteneur_main)
