from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel


class contrat(MDCard):
    def __init__(self, client, date_contrat, type_traitement, durée, debut_contrat, fin_prévu, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = ("300dp", "390dp")  # Taille ajustée
        self.padding = ("15dp", "15dp", "0dp", "10dp")
        self.elevation = 1
        self.orientation = "vertical"
        self.pos_hint= {"center_x": .5, "center_y": .7}
        self.md_bg_color= '#56B5FB'
        self.radius = 10

        #informations
        info_conteneur = MDGridLayout(cols=1)

        info_conteneur.add_widget(MDLabel(text=f"Client : {client}",
                                          font_style="Body1",
                                          halign="left",
                                          font_name= 'poppins',
                                          font_size= 12))
        info_conteneur.add_widget(MDLabel(text=f"Date du contrat : {date_contrat}",
                                          font_style="Body1",
                                          halign="left",
                                          font_name= 'poppins',
                                          font_size= 12))
        info_conteneur.add_widget(MDLabel(text=f"Traitement(Type) : {type_traitement}",
                                          font_style="Body1",
                                          halign="left",
                                          font_name= 'poppins',
                                          font_size= 12))
        info_conteneur.add_widget(MDLabel(text=f"Durée du contrat : {durée}",
                                          font_style="Body1",
                                          halign="left",
                                          font_name= 'poppins',
                                          font_size= 12))
        info_conteneur.add_widget(MDLabel(text=f"Début du contrat : {debut_contrat}",
                                          font_style="Body1",
                                          halign="left",
                                          font_name= 'poppins',
                                          font_size= 12))
        info_conteneur.add_widget(MDLabel(text=f"Fin prévu du contrat : {fin_prévu}",
                                          font_style="Body1",
                                          halign="left",
                                          font_name= 'poppins',
                                          font_size= 12))

        #Conteneur principal
        conteneur_main = MDBoxLayout(orientation="vertical", padding='15dp')

        #Bouton
        conteneur_btn = MDBoxLayout(size_hint_y=.5,
                                    height="50dp",
                                    padding=("0dp", "50dp", "20dp", "20dp"))
        more_info_btn = MDRectangleFlatButton(
            text="Plus d'informations",
            size_hint=(1, 1.3),
            font_size= 15,
            md_bg_color= 'white',
            _default_text_color='black',
            _radius = 8,
            line_color= 'white',
            font_name= 'poppins'
        )
        conteneur_btn.add_widget(more_info_btn)

        #Ajouter les éléments à la carte
        conteneur_main.add_widget(info_conteneur)
        conteneur_main.add_widget(conteneur_btn)
        self.add_widget(conteneur_main)
