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

from card import contrat
from email import is_valid_email
from gestion_ecran_contrat import gestion_ecran_contrat
from gestion_ecran import gestion_ecran
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

        self.manager = ScreenManager(size_hint=(None, None))

        self.manager.transition.duration = 0.1
        gestion_ecran_contrat(self.manager)

        #Pour les dropdown
        self.menu = None

        screen = ScreenManager()
        screen.add_widget(Builder.load_file('screen/main.kv'))
        screen.add_widget(Builder.load_file('screen/Sidebar.kv'))
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

    def show_dialog(self, title, text):
        # Affiche une boîte de dialogue
        if not hasattr(self, 'dialog') or self.dialog is None:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.close_dialog()
                    )
                ],
            )
        else:
            self.dialog.title = title
            self.dialog.text = text
        self.dialog.open()

    def close_dialog(self):
        self.dialog.dismiss()


    def fenetre(self, titre, ecran):
        self.manager.current = ecran
        contrat = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint= (.8, .65),
            content_cls= self.manager
        )
        self.manager.height = '500dp' if ecran == 'option_contrat' else '390dp'
        self.manager.width = '1000dp'
        self.dialog = contrat
        self.dialog.bind(on_dismiss= self.dismiss)

        self.dialog.open()

    def dismiss(self, *args):
        if self.manager.parent:
            self.manager.parent.remove_widget(self.manager)

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

        self.ajout_tableau(place)

    def switch_to_home(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'Home'

    def switch_to_client(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'client'

    def switch_to_planning(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'planning'

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
        self.dropdown_menu(button, compte)

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

    def retour_new(self,text,  champ):
        self.manager.get_screen('new_contrat').ids[f'{champ}'].text = text
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

    def ajout_tableau(self, place):
        self.tableau = MDDataTable(
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
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
                ("25/11/2024", "DEV-CORPS MDG", "Dératisation", "26/11/24 au 27/11/25"),
            ],
        )
        self.tableau.bind(on_row_press=self.row_pressed)
        place.add_widget(self.tableau)

    def row_pressed(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        date = row_data[3].split(' ')
        self.manager.get_screen('option_contrat').ids.titre.text = f'A propos du contrat de {row_data[1]}'
        self.manager.get_screen('option_contrat').ids.date_contrat.text = f'Contrat du : {row_data[0]}'
        self.manager.get_screen('option_contrat').ids.debut_contrat.text = f'Début du contrat : {date[0]}'
        self.manager.get_screen('option_contrat').ids.fin_contrat.text = f'Fin du contrat : {date[2]}'
        self.manager.get_screen('option_contrat').ids.type_traitement.text = f'Type de traitement : {row_data[2]}'
        self.fenetre('', 'option_contrat')

    def suppression_contrat(self, titre, contrat, debut, fin):
        client = titre.split(' ')

        self.manager.get_screen('suppression_contrat').ids.titre.text = f'Suppression du contrat de {client[5] + client[6]}'
        self.manager.get_screen('suppression_contrat').ids.date_contrat.text = contrat
        self.manager.get_screen('suppression_contrat').ids.debut_contrat.text = debut
        self.manager.get_screen('suppression_contrat').ids.fin_contrat.text = fin

        self.dismiss()
        self.close_dialog()
        self.fenetre('','suppression_contrat')

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