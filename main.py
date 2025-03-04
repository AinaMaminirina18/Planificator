from functools import partial

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.core.window import Window

import asyncio
import threading
import aiomysql
from kivymd.uix.pickers import MDDatePicker

from card import contrat
from email import is_valid_email
from gestion_ecran_client import gestion_ecran_client
from gestion_ecran_contrat import gestion_ecran_contrat
from gestion_ecran import gestion_ecran
from gestion_ecran_planning import gestion_ecran_planning
from gestion_ecran_histo import gestion_ecran_histo
from setting_bd import DatabaseManager
import verif_password as vp

Window.size = (1200, 680)
Window.left = 40
Window.top = 20

Window.minimum_height = 680
Window.minimum_width = 1300


class Screen(MDApp):

    copyright = '©Copyright @APEXNova Labs 2025'
    name = 'Planificator'
    description = 'Logiciel de suivi et gestion de contrat'
    CLM = 'Assets/CLM.JPG'
    CL = 'Assets/CL.JPG'


    def on_start(self):
        gestion_ecran(self.root)

        self.ajout_carte()

    def build(self):
        #Parametre de la base de données
        self.loop = asyncio.new_event_loop()
        self.database = DatabaseManager(self.loop)
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        #initialiser la conexion à la base de données
        asyncio.run_coroutine_threadsafe(self.database.connect(), self.loop)

        #Configuration de la fenêtre
        self.theme_cls.theme_style= 'Light'
        self.theme_cls.primary_palette = "BlueGray"
        self.icon = self.CLM
        self.title = 'Planificator'.upper()

        #Gestion des écrans dans contrat
        self.contrat_manager = ScreenManager(size_hint=(None, None))

        self.contrat_manager.transition.duration = 0.1
        gestion_ecran_contrat(self.contrat_manager)

        #Gestion des écrans dans client
        self.client_manager = ScreenManager(size_hint=(None, None))

        self.client_manager.transition.duration = 0.1
        gestion_ecran_client(self.client_manager)

        #Gestionde écrans dans planning
        self.planning_manager = ScreenManager(size_hint=(None, None))

        self.planning_manager.transition.duration = 0.1
        gestion_ecran_planning(self.planning_manager)
        
        #Gestion des écrans dans historique
        self.historic_manager = ScreenManager(size_hint=(None, None))

        self.historic_manager.transition.duration = 0.1
        gestion_ecran_histo(self.historic_manager)

        #Pour les dropdown
        self.menu = None

        screen = ScreenManager()
        screen.add_widget(Builder.load_file('screen/Sidebar.kv'))
        screen.add_widget(Builder.load_file('screen/main.kv'))
        screen.add_widget(Builder.load_file('screen/Signup.kv'))
        screen.add_widget(Builder.load_file('screen/Login.kv'))
        return screen

    def login(self):
        """Gestion de l'action de connexion."""
        username = self.root.get_screen('login').ids.login_username.text
        password = self.root.get_screen('login').ids.login_password.text
        if not username or not password:
            Clock.schedule_once(lambda s: self.show_dialog('Erreur', 'Veuillez completer tous les champs'))
            return
        else:
            async def process_login():
                try:
                    result = await self.database.verify_user(username, password)
                    if result and vp.reverse(password, result[0]):
                        Clock.schedule_once(lambda dt: self.switch_to_main())
                        Clock.schedule_once(lambda a: self.show_dialog("Success", "Login successful!"))
                        Clock.schedule_once(lambda cl: self.clear_fields('login'))

                    else:
                        Clock.schedule_once(lambda dt: self.show_dialog("Erreur", "Aucun compte trouvé dans la base de données"))
                except:
                    self.show_dialog("Error", "Une erreur s'est produite")

            asyncio.run_coroutine_threadsafe(process_login(), self.loop)

    def sign_up(self):
        """Gestion de l'action d'inscription."""
        nom = self.root.get_screen('signup').ids.nom.text
        prenom = self.root.get_screen('signup').ids.prenom.text
        email = self.root.get_screen('signup').ids.Email.text
        type_compte = self.root.get_screen('signup').ids.type.text
        username = self.root.get_screen('signup').ids.signup_username.text
        password = self.root.get_screen('signup').ids.signup_password.text
        confirm_password = self.root.get_screen('signup').ids.confirm_password.text

        valid_password = vp.get_valid_password(nom, prenom, password, confirm_password)

        if not nom or not prenom or not email or not password or not username or not confirm_password:
            Clock.schedule_once(lambda  dt: self.show_dialog("Erreur", "Veuillez completer tous les champs"))
            return

        elif not is_valid_email(email):
            Clock.schedule_once(lambda dt: self.show_dialog('Erreur', 'Verifier votre adresse email'))

        elif 'Le' in str(valid_password):
            Clock.schedule_once(lambda dt: self.show_dialog("Erreur", valid_password))

        else:
            async def add_user_task():
                try:
                    await self.database.add_user(nom, prenom, email, username, valid_password, type_compte)
                    Clock.schedule_once(lambda a: self.switch_to_main())
                    Clock.schedule_once(lambda dt: self.show_dialog("Success", "Compte créé avec succès !"))
                    Clock.schedule_once(lambda cl: self.clear_fields('signup'))
                except aiomysql.IntegrityError:
                    Clock.schedule_once(lambda dt: self.show_dialog("Erreur", "Username already exists."))

            # Exécuter la tâche d'ajout d'utilisateur dans la boucle asyncio
            asyncio.run_coroutine_threadsafe(add_user_task(), self.loop)

    def show_dialog(self, titre, texte):
        # Affiche une boîte de dialogue
        if not hasattr(self, 'dialog') or self.dialog is None:
            self.dialogue = MDDialog(
                title=titre,
                text=texte,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.close_dialog()
                    )
                ],
            )
        if titre == 'Déconnexion':
            self.dialogue = MDDialog(
                title= titre,
                text= texte,
                buttons=[
                    MDFlatButton(
                        text='OUI',
                        on_release= lambda x: self.deconnexion()
                    ),
                    MDFlatButton(
                        text= 'NON',
                        on_release= lambda x: self.close_dialog()
                    )
                ]
            )
        self.dialogue.open()

    def deconnexion(self):
        self.close_dialog()
        self.root.current = 'before login'

    def close_dialog(self):
        self.dialogue.dismiss()

    def reverse_date(self, ex_date):
        y, m, d = str(ex_date).split('-')
        date = f'{d}-{m}-{y}'
        return date

    def calendrier(self, ecran, champ):
        calendrier = MDDatePicker(primary_color= '#A5D8FD')
        calendrier.open()
        calendrier.bind(on_save=partial(self.choix_date, ecran,champ))

    def choix_date(self,ecran, champ, instance, value, date_range):
        manager = self.contrat_manager if 'contrat' in ecran else self.client_manager
        manager.get_screen(ecran).ids[champ].text = str(self.reverse_date(value))

    def fermer_ecran(self):
        self.dialog.dismiss()

    def fenetre_contrat(self, titre, ecran):
        self.contrat_manager.current = ecran
        contrat = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint= (.8, .65),
            content_cls= self.contrat_manager
        )
        hauteur = '500dp' if ecran == 'option_contrat' else '500dp' if ecran == 'ajout_info_client' else '390dp'
        self.contrat_manager.height = hauteur
        self.contrat_manager.width = '1000dp'
        self.dialog = contrat
        self.dialog.bind(on_dismiss=self.dismiss_contrat)

        self.dialog.open()

    def fenetre_client(self, titre, ecran):
        self.client_manager.current = ecran
        client = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint= (.8, .65),
            content_cls= self.client_manager
        )
        self.client_manager.height = '390dp' if ecran == 'option_client' else '550dp'
        self.client_manager.width = '1000dp'

        self.dialog = client
        self.dialog.bind(on_dismiss=self.dismiss_client)

        self.dialog.open()
        
    def fenetre_planning(self, titre, ecran):
        self.planning_manager.current = ecran
        planning = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.8, .58),
            content_cls=self.planning_manager
        )
        self.planning_manager.height = '350dp'
        self.planning_manager.width = '1000dp'

        self.dialog = planning
        self.dialog.bind(on_dismiss=self.dismiss_planning)

        self.dialog.open()


    def fenetre_histo(self, titre, ecran):
        self.historic_manager.current = ecran
        histo = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.8, .65),
            content_cls=self.historic_manager
        )
        self.historic_manager.height = '390dp' if ecran == 'option_historique' else '550dp'
        self.historic_manager.width = '1000dp'

        self.dialog = histo
        self.dialog.bind(on_dismiss=self.dismiss_histo)

        self.dialog.open()

    def dismiss_contrat(self, *args):
        if self.contrat_manager.parent:
            self.contrat_manager.parent.remove_widget(self.contrat_manager)

    def dismiss_client(self, *args):
        if self.client_manager.parent:
            self.client_manager.parent.remove_widget(self.client_manager)

    def dismiss_planning(self, *args):
        if self.planning_manager.parent:
            self.planning_manager.parent.remove_widget(self.planning_manager)
            
    def dismiss_histo(self, *args):
        if self.historic_manager.parent:
            self.historic_manager.parent.remove_widget(self.historic_manager)

    def dropdown_menu(self, button, menu_items, color):
        self.menu = MDDropdownMenu(
            md_bg_color= color,
            items=menu_items,
        )
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item, name, screen, champ):
        if name == 'home':
            self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(screen).ids[champ].text = text_item
        else:
            self.root.get_screen('signup').ids['type'].text = text_item
        self.menu.dismiss()

    def clear_fields(self, screen):
        sign_up = ['nom','prenom','Email','type','signup_username','signup_password','confirm_password']
        login = ['login_username', 'login_password']
        if screen == 'signup':
            for id in sign_up:
                self.root.get_screen('signup').ids[id].text = ''
        if screen == 'login':
            for id in login:
                self.root.get_screen('login').ids[id].text = ''

    def switch_to_contrat(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current = 'contrat'
        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('contrat').ids.tableau_contrat

        self.tableau_contrat(place)

    def switch_to_home(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'Home'

    def switch_to_client(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'client'

        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('client').ids.tableau_client

        self.tableau_client(place)

    def switch_to_historique(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'historique'

        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('historique').ids.tableau_historic

        self.tableau_historic(place)

    def switch_to_planning(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'planning'

        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('planning').ids.tableau_planning

        self.tableau_planning(place)

    def switch_to_about(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'about'

    def switch_to_main(self):
        self.root.current = 'Sidebar'

    def dropdown_compte(self, button, name):
        type_compte = ['Administrateur', 'Simple compte']
        compte = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x, name,'signup', 'type'),
            } for i in type_compte
        ]
        self.dropdown_menu(button, compte, 'white')

    def dropdown_homepage(self, button, name):
        type_tri = ['Contrats', 'Clients', 'Planning']
        home = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x, name,'Home', 'type_contrat'),
                "md_bg_color": (0.647, 0.847, 0.992, 1)
            } for i in type_tri
        ]
        self.dropdown_menu(button, home,  (0.647, 0.847, 0.992, 1))

    def dropdown_contrat(self, button, name):
        type_tri = ['Récents', 'Mois', 'Type de contrat']
        home = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x, name,'contrat', 'tri'),
            } for i in type_tri
        ]
        self.dropdown_menu(button, home, (0.647, 0.847, 0.992, 1))

    def dropdown_new_contrat(self,button,  champ):
        type = ['Dératisation', 'Désinsectisation', 'Désinfection', 'Nettoyage']
        durée = ['12 mois', '6 mois', '4 mois', '3 mois', '2 mois']
        categorie = ['Nouveau contrat', 'Renouvellement contrat']

        item_menu = type if champ == 'type_traitement' else durée if champ == 'duree_new_contrat' else categorie
        menu = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.retour_new(x, champ),
            } for i in item_menu
        ]
        self.dropdown_menu(button, menu, 'white')

    def dropdown_rendu_excel(self,button,  champ):
        type = ['Dératisation', 'Désinsectisation', 'Désinfection', 'Nettoyage']
        mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai']
        client = ['DevCorps', 'ApexNovaLabs', 'Cleanliness Of Madagascar']

        item_menu = type if champ == 'type_traitement_planning' else mois if champ == 'mois_planning' else client
        menu = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.retour_planning(x, champ),
            } for i in item_menu
        ]
        self.dropdown_menu(button, menu, 'white')

    def retour_new(self,text,  champ):
        self.contrat_manager.get_screen('new_contrat').ids[f'{champ}'].text = text
        self.menu.dismiss()

    def retour_planning(self,text,  champ):
        self.planning_manager.get_screen('rendu_planning').ids[f'{champ}'].text = text
        self.menu.dismiss()

    def choose_screen(self, instance):
        if instance in self.root.get_screen('Sidebar').ids.values():
            current_id = list(self.root.get_screen('Sidebar').ids.keys())[list(self.root.get_screen('Sidebar').ids.values()).index(instance)]
            self.root.get_screen('Sidebar').ids[current_id].text_color = 'white'
            for ids, item in self.root.get_screen('Sidebar').ids.items():
                if ids != current_id:
                    self.root.get_screen('Sidebar').ids[ids].text_color = 'black'

    def ajout_carte(self):

        clients = [
            {"name": "Alice Dupont", "phone": "06 12 34 56 78", "email": "alice@mail.com", "address": "12 rue A",
             "city": "Paris", "zip_code": "75001"},
            {"name": "Marc Durand", "phone": "06 98 76 54 32", "email": "marc@mail.com", "address": "34 avenue B",
             "city": "Lyon", "zip_code": "69002"},
            {"name": "Sophie Martin", "phone": "07 56 43 21 09", "email": "sophie@mail.com",
             "address": "56 boulevard C", "city": "Marseille", "zip_code": "13003"},
            {"name": "Jean Morel", "phone": "06 45 67 89 01", "email": "jean@mail.com", "address": "78 allée D",
             "city": "Toulouse", "zip_code": "31000"},
        ]

        client_box = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('Home').ids.contrats
        for client in clients:
            card = contrat(client["name"], client["phone"], client["email"], client["address"], client["city"],
                              client["zip_code"])
            client_box.add_widget(card)

    def tableau_contrat(self, place):
        self.liste_contrat = MDDataTable(
            pos_hint={'center_x':.5, "center_y": .53},
            size_hint=(1,1),
            background_color_header = '#56B5FB',
            background_color= '#56B5FB',
            rows_num=20,
            elevation=0,
            column_data=[
                ("Date du contrat", dp(35)),
                ("Client concerné", dp(60)),
                ("Type de traitement", dp(40)),
                ("Durée", dp(40)),
            ],
            row_data=[
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("26/11/2024", "Cleanliness Madagascar", "Désinsectisation", "01/07/23 au 02/07/24"),
                ("25/11/2024", "DEV-CORPS MDG", "Nettoyage", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Désinfection", "26/11/24 au 27/11/25"),
            ],
        )
        self.liste_contrat.bind(on_row_press=self.row_pressed_contrat)
        place.add_widget(self.liste_contrat)

    def row_pressed_contrat(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        date = row_data[3].split(' ')
        self.contrat_manager.get_screen('option_contrat').ids.titre.text = f'A propos du contrat de {row_data[1]}'
        self.contrat_manager.get_screen('option_contrat').ids.date_contrat.text = f'Contrat du : {row_data[0]}'
        self.contrat_manager.get_screen('option_contrat').ids.debut_contrat.text = f'Début du contrat : {date[0]}'
        self.contrat_manager.get_screen('option_contrat').ids.fin_contrat.text = f'Fin du contrat : {date[2]}'
        self.contrat_manager.get_screen('option_contrat').ids.type_traitement.text = f'Type de traitement : {row_data[2]}'
        self.fenetre_contrat('', 'option_contrat')

    def tableau_client(self, place):
        self.liste_client = MDDataTable(
            pos_hint={'center_x':.5, "center_y": .53},
            size_hint=(1,1),
            background_color_header = '#56B5FB',
            background_color= '#56B5FB',
            rows_num=20,
            elevation=0,
            column_data=[
                ("Client", dp(35)),
                ("Email", dp(60)),
                ("Adresse du client", dp(40)),
                ("Date de contrat du client", dp(40)),
            ],
            row_data=[
                ("DEV-CORPS MDG", "devcorps@dv.mg", "Ankadindramamy", "27/11/25"),
                ("Cleanliness Madagascar", "CleanlinessOfMadagascar@gmail.com", "Anjanahary", " 02/07/24"),
            ],
        )
        self.liste_client.bind(on_row_press=self.row_pressed_client)
        place.add_widget(self.liste_client)

    def row_pressed_client(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        self.client_manager.get_screen('option_client').ids.titre.text = f'A propos de {row_data[0]}'
        self.client_manager.get_screen('option_client').ids.date_contrat.text = f'Contrat du : {row_data[3]}'
        self.client_manager.get_screen('option_client').ids.debut_contrat.text = f'Début du contrat : 28/11/24'
        self.client_manager.get_screen('option_client').ids.fin_contrat.text = f'Fin du contrat : 29/11/25'
        self.client_manager.get_screen('option_client').ids.type_traitement.text = f'Type de traitement : {row_data[1]}'
        self.fenetre_client('', 'option_client')
    
    def tableau_planning(self, place):
        self.liste_planning = MDDataTable(
            pos_hint={'center_x':.5, "center_y": .5},
            size_hint=(1,1),
            background_color_header = '#56B5FB',
            background_color= '#56B5FB',
            rows_num=20,
            elevation=0,
            column_data=[
                ("Client", dp(55)),
                ("Durée du contrat", dp(35)),
                ("Type de traitement", dp(40)),
                ("Option", dp(40)),
            ],
            row_data=[
                ("DEV-CORPS MDG", "12 mois", "Dératisation", "Aucun decalage"),
                ("Cleanliness Madagascar", "6mois", "Nettoyage", "Décalage"),
            ],
        )
        self.liste_planning.bind(on_row_press=self.row_pressed_planning)
        place.add_widget(self.liste_planning)

    def row_pressed_planning(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]
        
    def tableau_historic(self, place):
        self.historique = MDDataTable(
            pos_hint={'center_x':.5, "center_y": .53},
            size_hint=(1,1),
            background_color_header = '#56B5FB',
            background_color= '#56B5FB',
            rows_num=20,
            elevation=0,
            column_data=[
                ("Nom client", dp(60)),
                ("Adresse du client", dp(60)),
                ("Date du contrat", dp(40)),
            ],
            row_data=[
                ("DEV-CORPS MDG", "Ankadindramamy", "27/11/25"),
                ("Cleanliness Madagascar", "Anjanahary", " 02/07/24"),
            ],
        )
        self.historique.bind(on_row_press=self.row_pressed_histo)
        place.add_widget(self.historique)

    def row_pressed_histo(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        print(row_data)
        self.fenetre_histo('', 'option_historique')

    def modification_client(self ,nom):
        #self.client_manager.get_screen('modif_client').ids.titre.text = f'Modifications des informartion sur {nom}'
        self.dismiss_client()
        self.fermer_ecran()
        self.fenetre_client(f'Modifications des informartion sur {nom}', 'modif_client')

    def suppression_contrat(self, titre, contrat, debut, fin):
        client = titre.split(' ')

        self.contrat_manager.get_screen('suppression_contrat').ids.titre.text = f'Suppression du contrat de {client[5] + client[6]}'
        self.contrat_manager.get_screen('suppression_contrat').ids.date_contrat.text = contrat
        self.contrat_manager.get_screen('suppression_contrat').ids.debut_contrat.text = debut
        self.contrat_manager.get_screen('suppression_contrat').ids.fin_contrat.text = fin

        self.dismiss_contrat()
        self.fermer_ecran()
        self.fenetre_contrat('', 'suppression_contrat')

    def open_compte(self, dev):
        import webbrowser
        if dev == 'Mamy':
            webbrowser.open('https://github.com/AinaMaminirina18')
        else:
            webbrowser.open('https://github.com/josoavj')


    def on_stop(self):
        """Arrête proprement la boucle asyncio et le gestionnaire de base de données."""
        if not self.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(self.database.close(), self.loop)
            future.result()

        self.loop.call_soon_threadsafe(self.loop.stop)


if __name__ == "__main__":
    LabelBase.register(name='poppins',
                       fn_regular='font/Poppins-Regular.ttf')
    LabelBase.register(name='poppins-bold',
                       fn_regular='font/Poppins-Bold.ttf')
    Screen().run()
