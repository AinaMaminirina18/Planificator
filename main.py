from kivymd.app import MDApp
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

from setting_bd import DatabaseManager
from verif_password import get_valid_password

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
        self.root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/Home.kv'))
        self.root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/about.kv'))
        self.root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/contrat.kv'))
        self.root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/Client.kv'))
        self.root.get_screen('Sidebar').ids['gestion_ecran'].add_widget(Builder.load_file('screen/planning.kv'))

        self.root.get_screen('Sidebar').ids['gestion_ecran'].transition =  SlideTransition(direction='up')

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

        async def process_login():
            try:
                result = await self.database.verify_user(username, password)
                if result:
                    Clock.schedule_once(lambda dt: self.switch_to_main())
                    Clock.schedule_once(lambda a: self.show_dialog("Success", "Login successful!"))
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

        if not nom or not prenom or not email or not password or not confirm_password:
            Clock.schedule_once(lambda  dt: self.show_dialog("Error", "Veuillez completer tous les champs"))
            return
        #elif get_valid_password( nom, prenom, password, type_compte):

        else:
            async def add_user_task():
                try:
                    await self.database.add_user(nom, prenom, email, password, type_compte)
                    Clock.schedule_once(lambda dt: self.show_dialog("Success", "Account created!"))
                except aiomysql.IntegrityError:
                    Clock.schedule_once(lambda dt: self.show_dialog("Error", "Username already exists."))
                except Exception as e:
                    Clock.schedule_once(lambda dt: self.show_dialog("Error", f"Database error: {e}"))

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
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
        else:
            self.dialog.title = title
            self.dialog.text = text
        self.dialog.open()

    def dropdown_menu(self, button, menu_items):
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item,name, screen, champ):
        if name == 'home':
            self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(screen).ids[champ].text = text_item
        else:
            self.root.get_screen('signup').ids['type'].text = text_item
        self.menu.dismiss()

    def switch_to_contrat(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current = 'contrat'

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

    def on_stop(self):
        """Arrête proprement la boucle asyncio et le gestionnaire de base de données."""
        asyncio.run_coroutine_threadsafe(self.database.close(), self.loop)
        self.loop.call_soon_threadsafe(self.loop.stop)

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
            } for i in type_tri
        ]
        self.dropdown_menu(button, home)

    def dropdown_contrat(self, button, name):
        type_tri = ['Récents', 'Mois', 'Type de contrat']
        home = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x, name,'contrat', 'tri'),
            } for i in type_tri
        ]
        self.dropdown_menu(button, home)

    def choose_screen(self, instance):
        if instance in self.root.get_screen('Sidebar').ids.values():
            current_id = list(self.root.get_screen('Sidebar').ids.keys())[list(self.root.get_screen('Sidebar').ids.values()).index(instance)]
            self.root.get_screen('Sidebar').ids[current_id].text_color = 'white'
            for ids, item in self.root.get_screen('Sidebar').ids.items():
                if ids != current_id:
                    self.root.get_screen('Sidebar').ids[ids].text_color = 'black'

    def open_compte(self, dev):
        import webbrowser
        if dev == 'Mamy':
            webbrowser.open('https://github.com/AinaMaminirina18')
        else:
            webbrowser.open('https://github.com/josoavj')


if __name__ == "__main__":
    LabelBase.register(name='poppins',
                       fn_regular='font/Poppins-Regular.ttf')
    LabelBase.register(name='poppins-bold',
                       fn_regular='font/Poppins-Bold.ttf')
    Screen().run()