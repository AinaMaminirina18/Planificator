from kivy.config import Config
Config.set('graphics', 'resizable', False)

from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.core.window import Window

Window.size = (1300, 680)
Window.left = 30
Window.top = 80

import asyncio
import threading
import locale
locale.setlocale(locale.LC_TIME, "fr_FR.utf8")

from datetime import datetime
from functools import partial

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.spinner import MDSpinner

from gestion_ecran_acceuil import gestion_ecran_home
from gestion_ecran_client import gestion_ecran_client
from gestion_ecran_compte import gestion_ecran_compte
from gestion_ecran_contrat import gestion_ecran_contrat
from gestion_ecran import gestion_ecran
from gestion_ecran_planning import gestion_ecran_planning
from gestion_ecran_histo import gestion_ecran_histo


class MyDatatable(MDDataTable):
    def set_default_first_row(self, *args):
        pass

class Screen(MDApp):

    copyright = '©Copyright @APEXNova Labs 2025'
    name = 'Planificator'
    description = 'Logiciel de suivi et gestion de contrat'
    CLM = 'Assets/CLM.JPG'
    CL = 'Assets/CL.JPG'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from setting_bd import DatabaseManager
        # Parametre de la base de données
        self.loop = asyncio.new_event_loop()
        self.database = DatabaseManager(self.loop)
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        asyncio.run_coroutine_threadsafe(self.database.connect(), self.loop)

    def on_start(self):
        gestion_ecran(self.root)

        asyncio.run_coroutine_threadsafe(self.populate_tables(), self.loop)

    def build(self):
        #Configuration de la fenêtre
        self.theme_cls.theme_style= 'Light'
        self.theme_cls.primary_palette = "BlueGray"
        self.icon = self.CLM
        self.title = 'Planificator'.upper()

        self.admin = False
        self.compte = None
        self.not_admin = None
        self.current_client = None
        self.card = None
        self.dialog = None

        self.table_en_cours = MDDataTable(
            use_pagination=True,
            rows_num=7,
            elevation=0,
            background_color_header='#56B5FB',
            column_data=[
                ("Date", dp(30)),
                ("Nom", dp(30)),
                ("État", dp(25)),
            ]
        )

        self.table_prevision = MDDataTable(
            use_pagination=True,
            rows_num=7,
            elevation=0,
            background_color_header='#56B5FB',
            column_data=[
                ("Date", dp(30)),
                ("Nom", dp(30)),
                ("État", dp(25)),
            ]
        )

        self.liste_contrat = MDDataTable(
                pos_hint={'center_x': 0.5, "center_y": 0.53},
                size_hint=(1, 1),
                background_color_header='#56B5FB',
                background_color='#56B5FB',
                rows_num=8,
                use_pagination= True,
                elevation=0,
                column_data=[
                    ("Client concerné", dp(60)),
                    ("Date du contrat", dp(35)),
                    ("Type de traitement", dp(40)),
                    ("Durée", dp(40)),
                ],
            )

        self.all_treat = MDDataTable(
            pos_hint={'center_x': 0.5, "center_y": 0.53},
            size_hint=(.7, 1),
            background_color_header='#56B5FB',
            background_color='#56B5FB',
            rows_num=4,
            use_pagination=True,
            elevation=0,
            column_data=[
                ("Date du contrat", dp(40)),
                ("Type de traitement", dp(50)),
                ("Durée", dp(40)),
            ],
        )
        self.liste_planning = MDDataTable(
            pos_hint={'center_x': .5, "center_y": .5},
            size_hint=(1, 1),
            background_color_header='#56B5FB',
            background_color='#56B5FB',
            rows_num=8,
            use_pagination=True,
            elevation=0,
            column_data=[
                ("Client", dp(50)),
                ("Type de traitement", dp(50)),
                ("Durée du contrat", dp(30)),
                ("Option", dp(45)),
            ]
        )
        self.liste_planning = MDDataTable(
            pos_hint={'center_x': .5, "center_y": .5},
            size_hint=(1, 1),
            background_color_header='#56B5FB',
            background_color='#56B5FB',
            rows_num=8,
            use_pagination=True,
            elevation=0,
            column_data=[
                ("Client", dp(50)),
                ("Type de traitement", dp(50)),
                ("Durée du contrat", dp(30)),
                ("Option", dp(45)),
            ]
        )
        self.liste_client = MDDataTable(
            pos_hint={'center_x': 0.5, "center_y": 0.53},
            size_hint=(1, 1),
            background_color_header='#56B5FB',
            background_color='#56B5FB',
            rows_num=8,
            use_pagination=True,
            elevation=0,
            column_data=[
                ("Client", dp(35)),
                ("Email", dp(60)),
                ("Adresse du client", dp(40)),
                ("Date de contrat du client", dp(40)),
            ]
        )

        self.historique = MDDataTable(
            pos_hint={'center_x': .5, "center_y": .53},
            size_hint=(1, 1),
            background_color_header='#56B5FB',
            background_color='#56B5FB',
            rows_num=8,
            use_pagination=True,
            elevation=0,
            column_data=[
                ("Client", dp(50)),
                ("Durée", dp(40)),
                ("Type de traitement", dp(40)),
                ("Remarques", dp(40))
            ]
        )

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

        #Gestion des écrans dans compte
        self.account_manager = ScreenManager(size_hint=(None, None))

        self.account_manager.transition.duration = 0.1
        gestion_ecran_compte(self.account_manager)

        #Gestion des écrans dans acceuil
        self.home_manager = ScreenManager(size_hint=(None, None))

        self.home_manager.transition.duration = 0.1
        gestion_ecran_home(self.home_manager)

        #Pour les dropdown
        self.menu = None

        self.dialogue = None

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
            Clock.schedule_once(lambda s: self.show_dialog('Erreur', 'Veuillez compléter tous les champs'), 0)
            return

        # Appel sécurisé de la coroutine
        asyncio.run_coroutine_threadsafe(self.process_login(username, password), self.loop)

    async def process_login(self, username, password):
        import verif_password as vp

        try:
            result = await self.database.verify_user(username)

            if result and vp.reverse(password, result[5]):
                Clock.schedule_once(lambda dt: self.switch_to_main(), 0)
                Clock.schedule_once(lambda a: self.show_dialog("Succès", "Connexion réussie !"), 0)
                Clock.schedule_once(lambda cl: self.clear_fields('login'), 0.5)
                self.compte = result

                if result[6] == 'Administrateur':
                    self.admin = True

            else:
                Clock.schedule_once(
                    lambda dt: self.show_dialog("Erreur", "Aucun compte trouvé dans la base de données"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_dialog("Erreur", f"Erreur : {str(e)}"))

    def sign_up(self):
        import verif_password as vp
        from email_verification import is_valid_email

        """Gestion de l'action d'inscription."""
        screen = self.root.get_screen('signup')
        nom = screen.ids.nom.text
        prenom = screen.ids.prenom.text
        email = screen.ids.Email.text
        type_compte = screen.ids.type.text
        username = screen.ids.signup_username.text
        password = screen.ids.signup_password.text
        confirm_password = screen.ids.confirm_password.text

        # 1. Validation des champs vides
        if not all([nom, prenom, email, username, password, confirm_password]):
            Clock.schedule_once(lambda dt: self.show_dialog("Erreur", "Veuillez compléter tous les champs"))
            return

        # 2. Validation de l'email
        if not is_valid_email(email):
            Clock.schedule_once(lambda dt: self.show_dialog('Erreur', 'Veuillez vérifier votre adresse email'))
            return

        # 3. Validation du mot de passe
        is_password_valid, password_validation_message = vp.get_valid_password(nom, prenom, password, confirm_password)
        if not is_password_valid:
            Clock.schedule_once(lambda dt: self.show_dialog("Erreur", password_validation_message))
            return

        # Le mot de passe validé (potentiellement hashé)
        validated_password = password_validation_message
        asyncio.run_coroutine_threadsafe(
            self._add_user_and_handle_feedback(nom, prenom, email, username, validated_password, type_compte),
            self.loop
        )

    async def _add_user_and_handle_feedback(self, nom, prenom, email, username, password, type_compte):
        from aiomysql import OperationalError

        try:
            await self.database.add_user(nom, prenom, email, username, password, type_compte)
            Clock.schedule_once(lambda dt: self.switch_to_login())
            Clock.schedule_once(lambda dt: self.show_dialog("Succès", "Compte créé avec succès !"))
            Clock.schedule_once(lambda dt: self.clear_fields('signup'))

        except OperationalError as error:
            # Gérer les erreurs spécifiques de la base de données
            if len(error.args) >= 1 and error.args[0] == 1644:
                Clock.schedule_once(lambda dt: self.show_dialog('Erreur', 'Un compte administrateur existe déjà'))

            else:
                # Afficher le message d'erreur de la base de données si disponible
                error_message = error.args[1] if len(error.args) >= 2 else str(error)
                Clock.schedule_once(
                    lambda dt: self.show_dialog('Erreur', f"Erreur de base de données: {error_message}"))
            print(f"OperationalError: {error}")  # Pour le débogage

        except Exception as e:
            # Capturer toute autre erreur inattendue
            Clock.schedule_once(lambda dt: self.show_dialog('Erreur', 'Une erreur inattendue est survenue.'))
            print(f"Erreur inattendue: {e}")  # Pour le débogage

    def creer_contrat(self):
        from dateutil.relativedelta import relativedelta

        ecran = self.contrat_manager.get_screen('ajout_info_client')
        nom = ecran.ids.nom_client.text
        prenom = ecran.ids.responsable_client.text
        email = ecran.ids.email_client.text
        telephone = ecran.ids.telephone.text
        adresse = ecran.ids.adresse_client.text
        categorie_client = ecran.ids.cat_client.text
        axe = ecran.ids.axe_client.text
        date_ajout = ecran.ids.ajout_client.text

        duree_contrat = self.contrat_manager.get_screen('new_contrat').ids.duree_new_contrat.text
        categorie_contrat = self.contrat_manager.get_screen('new_contrat').ids.cat_contrat.text
        date_contrat = self.contrat_manager.get_screen('new_contrat').ids.date_new_contrat.text
        date_debut = self.contrat_manager.get_screen('new_contrat').ids.debut_new_contrat.text
        date_fin = self.contrat_manager.get_screen('new_contrat').ids.date_new_contrat.text if duree_contrat == 'Déterminée' else 'Indéterminée'

        if date_fin == "Indéterminée":
            duree = 12
            fin_contrat = 'Indéterminée'
        else:
            fin_contrat_rev = self.reverse_date(date_fin)
            debut_rev = self.reverse_date(date_debut)

            fin_contrat = datetime.strptime(fin_contrat_rev, "%Y-%m-%d").date()
            debut_date = datetime.strptime(debut_rev, "%Y-%m-%d").date()

            diff = relativedelta(fin_contrat, debut_date)
            duree = diff.years * 12 + diff.months

        def maj():
            self.contrat_manager.get_screen('ajout_facture').ids.axe_client.text = axe
            self.contrat_manager.get_screen('ajout_planning').ids.axe_client.text = axe

        async def create():
            self.id_traitement = []
            try:
                self.traitement, self.categorie_trait = self.get_trait_from_form()

                client = await self.database.create_client(
                    nom, prenom, email, telephone, adresse,
                    self.reverse_date(date_ajout), categorie_client, axe
                )

                self.contrat = await self.database.create_contrat(
                    client,
                    self.reverse_date(date_contrat),
                    self.reverse_date(date_debut),
                    fin_contrat,
                    duree,
                    duree_contrat,
                    categorie_contrat
                )

                for i in range(len(self.traitement)):
                    type_traitement = await self.database.typetraitement(
                        self.categorie_trait[i], self.traitement[i]
                    )
                    traitement_id = await self.database.creation_traitement(self.contrat, type_traitement)
                    self.id_traitement.append(traitement_id)

                Clock.schedule_once(lambda dt: self.dismiss_contrat(), 0)
                Clock.schedule_once(lambda dt: self.fermer_ecran(), 0)
                Clock.schedule_once(lambda dt: maj(), 0)
                Clock.schedule_once(lambda dt: self.fenetre_contrat('Ajout du planning', 'ajout_planning'), 0)

            except Exception as e:
                print(f"Une erreur inattendue est survenue lors de la création du contrat : {e}")

        asyncio.run_coroutine_threadsafe(create(), self.loop)

    async def get_client(self):
        try:
            result = await self.database.get_client()
            if result:
                place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('contrat').ids.tableau_contrat
                threading.Thread(target = partial(self.update_contract_table,place, result)).start()

        except Exception as e:
            print(f"Erreur lors de la récupération des clients: {e}")
            self.show_dialog("Erreur", "Une erreur est survenue lors du chargement des clients.")

    def gestion_planning(self):
        ajout_planning_screen = self.contrat_manager.get_screen('ajout_planning')
        mois_fin = ajout_planning_screen.ids.mois_fin.text
        mois_debut = ajout_planning_screen.ids.mois_date.text
        date_prevu = ajout_planning_screen.ids.date_prevu.text
        redondance = ajout_planning_screen.ids.red_trait.text

        bouton = self.contrat_manager.get_screen('ajout_facture').ids.accept

        if self.contrat_manager.current == 'ajout_planning':
            if self.verifier_mois(mois_debut) != 'Erreur':
                self.contrat_manager.get_screen('ajout_facture').ids.mois_fin.text = mois_fin
                self.contrat_manager.get_screen('ajout_facture').ids.montant.text = ''
                self.contrat_manager.get_screen('ajout_facture').ids.date_prevu.text = date_prevu
                self.contrat_manager.get_screen('ajout_facture').ids.red_trait.text = redondance
                self.contrat_manager.get_screen('ajout_facture').ids.traitement_c.text = self.traitement[0]
                if len(self.traitement) == 1:
                    bouton.text = 'Enregistrer'

                self.fermer_ecran()
                self.fenetre_contrat('Ajout de la facture','ajout_facture')
                self.traitement.pop(0)
            else:
                self.show_dialog('Erreur', 'Mot non reconnu comme mois, veuillez verifier')

        elif not self.traitement:
            self.dismiss_contrat()
            self.fermer_ecran()
            asyncio.run_coroutine_threadsafe(self.populate_tables(), self.loop)

            self.clear_fields('new_contrat')
            self.show_dialog('Enregistrement réussie', 'Le contrat a été bien enregistré')
            self.remove_tables('contrat')

        else:

            ajout_planning_screen.ids.get('mois_date').text = ''
            ajout_planning_screen.ids.get('mois_fin').text= 'Indéterminée' if mois_fin == 'Indéterminée' else ''
            ajout_planning_screen.ids.get('date_prevu').text = ''
            ajout_planning_screen.ids.get('red_trait').text = '1 mois'
            ajout_planning_screen.ids.type_traitement.text = self.traitement[0]
            self.fermer_ecran()
            self.fenetre_contrat('Ajout du planning','ajout_planning')

    def save_planning(self):
        mois_debut = self.contrat_manager.get_screen('ajout_planning').ids.mois_date.text
        mois_fin = self.contrat_manager.get_screen('ajout_planning').ids.mois_fin.text
        date_prevu = self.contrat_manager.get_screen('ajout_planning').ids.date_prevu.text
        redondance = self.contrat_manager.get_screen('ajout_planning').ids.red_trait.text
        date_debut = self.contrat_manager.get_screen('new_contrat').ids.debut_new_contrat.text
        temp = date_debut.split('-')
        date_fin = datetime.strptime(f'{temp[0]}-{(int(temp[1])+11) % 12}-{(int(temp[2]) + 1) if temp[1] != 1 else temp[2]}',  "%d-%m-%Y").date()

        montant = self.contrat_manager.get_screen('ajout_facture').ids.montant.text
        axe_client = self.contrat_manager.get_screen('ajout_facture').ids.axe_client.text
        if redondance != 'une seule fois':
            int_red = redondance.split(" ")[0]
        else:
            int_red = 12

        async def save():
            debut = datetime.strptime(self.verifier_mois(mois_debut), "%B").month
            fin = datetime.strptime(self.verifier_mois(mois_fin), "%B").month if mois_fin != 'Indéterminée' else 0
            try:
                if int_red == 12:
                    await self.database.un_jour(self.contrat)
                    self.contrat = None
                planning = await self.database.create_planning(self.id_traitement[0],
                                                               self.reverse_date(date_debut),
                                                               debut,
                                                               fin,
                                                               int_red,
                                                               date_fin)

                dates_planifiees = self.planning_per_year(date_prevu, int_red)

                for date in dates_planifiees:
                    try:
                        planning_detail = await self.database.create_planning_details(planning, date)
                        await self.database.create_facture(planning_detail,
                                                           int(montant) if ' ' not in montant else int(montant.replace(' ', '')),
                                                           date,
                                                           axe_client)

                    except Exception as e:
                        print("enregistrement planning detail ", e)

                self.id_traitement.pop(0)

            except Exception as e:
                print('eto', e)

        asyncio.run_coroutine_threadsafe(save(), self.loop)
        self.gestion_planning()

    def planning_per_year(self, debut, redondance):
        from datetime import timedelta
        from tester_date import ajuster_si_weekend, jours_feries


        #red = redondance.split(' ')
        pas = int(redondance)
        date = datetime.strptime(self.reverse_date(debut), "%Y-%m-%d").date()

        def ajouter_mois(date_depart, nombre_mois):
            import calendar

            """Ajoute un nombre de mois à une date."""
            mois = date_depart.month - 1 + nombre_mois
            annee = date_depart.year + mois // 12
            mois = mois % 12 + 1
            jour = min(date_depart.day, calendar.monthrange(annee, mois)[1])
            return datetime(annee, mois, jour).date()

        dates = []
        for i in range(12 // pas):
            date_suivante = ajouter_mois(date, i * pas)
            date_suivante = ajuster_si_weekend(date_suivante)
            feries = jours_feries(date_suivante.year)
            while date_suivante in feries.values():
                date_suivante += timedelta(days=1)

            dates.append(date_suivante)

        return dates

    async def get_all_planning(self):
        try:
            return await self.database.get_all_planning()
        except Exception as e:
            print('func get_all_planning', e)
            return []  # Retourne une liste vide en cas d'erreur

        #asyncio.run_coroutine_threadsafe(all_planning(), self.loop)

    def update_account(self, nom, prenom, email, username, password, confirm):
        import verif_password as vp
        from email_verification import is_valid_email

        is_valid, valid_password = vp.get_valid_password(nom, prenom, password, confirm)

        if not all([nom, prenom, email, username, password, confirm]):
            Clock.schedule_once(partial(self.show_dialog, "Erreur", "Veuillez compléter tous les champs."))
            return

        if not is_valid_email(email):
            Clock.schedule_once(partial(self.show_dialog, 'Erreur', 'Veuillez vérifier votre adresse email.'))
            return

        if not is_valid:
            Clock.schedule_once(lambda dt: self.show_dialog("Erreur", valid_password))
            return

        async def update_user_task():
            try:
                await self.database.update_user(nom, prenom, email, username, valid_password, self.compte[0])

                def _post_update_ui_actions():
                    self.show_dialog("Succès", "Les modifications ont été enregistrées avec succès !")
                    self.clear_fields('modif_info_compte')
                    self.current_compte()
                    self.dismiss_compte()
                    self.fermer_ecran()

                Clock.schedule_once(lambda dt: _post_update_ui_actions(), 0)
            except Exception as error:
                print(error)

        asyncio.run_coroutine_threadsafe(update_user_task(), self.loop)

    def current_compte(self):
        ecran = 'compte' if self.admin else 'not_admin'
        target_screen = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(ecran)
        async def current():
            compte = await self.database.get_current_user(self.compte[0])
            target_screen.ids.nom.text = f'Nom : {compte[1]}'
            target_screen.ids.prenom.text = f'Prénom : {compte[2]}'
            target_screen.ids.email.text = f'Email : {compte[3]}'
            target_screen.ids.username.text = f"Nom d'utilisateur : {compte[4]}"

            self.compte = compte

        asyncio.run_coroutine_threadsafe(current(), self.loop)

    async def supprimer_client(self):
        try:
            await self.database.delete_client(self.current_client[0])
            await self.populate_tables()

        except Exception as e:
            print('suppression', e)

    def delete_client(self):
        self.fermer_ecran()
        self.dismiss_contrat()
        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('planning').ids.tableau_planning
        place.clear_widgets()

        def dlt():
            asyncio.run_coroutine_threadsafe(self.supprimer_client(), self.loop)

        Clock.schedule_once(lambda dt: dlt(),0)
        Clock.schedule_once(lambda dt: self.show_dialog('Suppression réussi', 'Le client abien été supprimé'), 0)
        Clock.schedule_once(lambda dt: self.remove_tables('contrat'),0)


    def delete_account(self, admin_password):
        import verif_password as vp

        if vp.reverse(admin_password,self.compte[5]):
            async def suppression():
                try:
                    await self.database.delete_user(self.not_admin[3])
                    Clock.schedule_once(lambda dt: self.dismiss_compte())
                    Clock.schedule_once(lambda dt: self.fermer_ecran())
                    Clock.schedule_once(lambda dt: self.show_dialog('', 'Suppression du compte réussie'))
                    Clock.schedule_once(lambda dt: self.remove_tables('compte'))

                except Exception as error:
                    erreur = error
                    Clock.schedule_once(lambda dt : self.show_dialog('Erreur', f'{erreur}'))

            asyncio.run_coroutine_threadsafe(suppression(), self.loop)
        else:
            self.account_manager.get_screen('suppression_compte').ids.admin_password.helper_text = 'Verifier le mot de passe'
            self.show_dialog('Erreur', f"Le mot de passe n'est pas correct")

    def get_trait_from_form(self):

        traitement = []
        categorie =[]
        dératisation = self.contrat_manager.get_screen('new_contrat').ids.deratisation.active
        désinfection = self.contrat_manager.get_screen('new_contrat').ids.desinfection.active
        désinsectisation = self.contrat_manager.get_screen('new_contrat').ids.desinsectisation.active
        nettoyage = self.contrat_manager.get_screen('new_contrat').ids.nettoyage.active
        fumigation = self.contrat_manager.get_screen('new_contrat').ids.fumigation.active
        ramassage = self.contrat_manager.get_screen('new_contrat').ids.ramassage.active
        anti_termite = self.contrat_manager.get_screen('new_contrat').ids.anti_ter.active

        if dératisation:
            traitement.append('Dératisation (PC)')
            categorie.append('PC')
        if désinfection:
            traitement.append('Désinfection (PC)')
            categorie.append('PC')
        if désinsectisation:
            categorie.append('PC')
            traitement.append('Désinsectisation (PC)')
        if nettoyage:
            categorie.append('NI: Nettoyage Industriel')
            traitement.append('Nettoyage industriel (NI)')
        if fumigation:
            categorie.append('PC')
            traitement.append('Fumigation (PC)')
        if ramassage:
            categorie.append("RO: Ramassage Ordures")
            traitement.append("Ramassage ordures (RO)")
        if anti_termite:
            categorie.append('AT: Anti termites')
            traitement.append('Anti termites (AT)')

        return traitement, categorie

    def search(self, text, search='False'):
        if search:
            print(self.verifier_mois(text))

    def verifier_mois(self, text ):
        from fuzzywuzzy import process

        mois_valides = [
            "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"
        ]
        mot_corigees, score = process.extractOne(text.lower(), mois_valides)
        if score >= 80:
            return mot_corigees
        else:
            return 'Erreur'

    def show_dialog(self, titre, texte):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton


        # Affiche une boîte de dialogue
        if not hasattr(self, 'dialogue') or self.dialogue is None or titre != 'Déconnexion':
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
        self.admin = False
        self.compte = None

    def close_dialog(self):
        self.dialogue.dismiss()

    def reverse_date(self, ex_date):
        y, m, d = str(ex_date).split('-')
        date = f'{d}-{m}-{y}'
        return date

    def calendrier(self, ecran, champ):
        from kivymd.uix.pickers import MDDatePicker

        if ecran == 'ecran_decalage' or ecran == 'modif_date':
            calendrier = MDDatePicker(year = self.planning_detail[9].year,
                                      month = self.planning_detail[9].month,
                                      day = self.planning_detail[9].day,
                                      primary_color= '#A5D8FD')
        else:
            calendrier = MDDatePicker(primary_color= '#A5D8FD')

        calendrier.open()
        calendrier.bind(on_save=partial(self.choix_date, ecran,champ))

    def choix_date(self, ecran, champ, instance, value, date_range):
        manager = self.planning_manager if ecran == 'ecran_decalage' else self.contrat_manager if 'contrat' or 'planning' in ecran else self.client_manager
        if ecran == 'modif_date' :
            manager = self.home_manager 
        manager.get_screen(ecran).ids[champ].text = ''
        manager.get_screen(ecran).ids[champ].text = str(self.reverse_date(value))

    def fermer_ecran(self):
        self.dialog.dismiss()

    def fenetre_contrat(self, titre, ecran):
        from kivymd.uix.dialog import MDDialog

        self.contrat_manager.current = ecran
        contrat = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.8, .8) if ecran == 'ajout_info_client' else (.8, .65) ,
            content_cls= self.contrat_manager
        )
        hauteur = '500dp' if ecran == 'option_contrat' else '500dp' if ecran == 'ajout_info_client' else '400dp'
        self.contrat_manager.height = hauteur
        self.contrat_manager.width = '1000dp'
        self.dialog = contrat
        self.dialog.bind(on_dismiss=self.dismiss_contrat)

        self.dialog.open()

    def modifier_date(self, source=None):
        from kivymd.uix.dialog import MDDialog

        if source == 'planning':
            self.dismiss_planning()
            self.fermer_ecran()

        self.home_manager.current = 'modif_date'
        acceuil = MDDialog(
            md_bg_color='#56B5FB',
            type='custom',
            size_hint=(.5, .5),
            content_cls=self.home_manager
        )

        self.home_manager.height = '300dp'
        self.home_manager.width = '600dp'

        self.dialog = acceuil
        self.dialog.bind(on_dismiss=self.dismiss_home)

        self.dialog.open()

    def changer_date(self):
        date = self.home_manager.get_scren('modif_date').ids.date_decalage.text

        async def modifier(date):
            await self.database.modifier_date(self.planning_detail[8], self.reverse_date(date))
            date = ''

        self.dismiss_planning()
        self.fermer_ecran()

        if date:
            asyncio.run_coroutine_threadsafe(modifier(date))
        else:
            self.show_dialog('Erreur', 'Aucune date est choisie')

    def afficher_facture(self, titre ,ecran, base):
        from kivymd.uix.dialog import MDDialog

        self.fermer_ecran()
        if base == 'contrat':
            self.dismiss_contrat()

        self.home_manager.current = ecran
        acceuil = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.7, .6),
            content_cls=self.home_manager
        )
        self.home_manager.height = '500dp'
        self.home_manager.width = '850dp'

        place = self.home_manager.get_screen('facture').ids.tableau_facture
        place.clear_widgets()
        self.dialog = acceuil
        self.dialog.bind(on_dismiss=self.dismiss_home)
        self.home_manager.get_screen('facture').ids.titre.text = f'Les factures de {self.current_client[1]} pour {self.current_client[5]}'

        def recup():
            asyncio.run_coroutine_threadsafe(self.recuperer_donnée(place), self.loop)

        Clock.schedule_once(lambda dt: recup(), 0.5)
        Clock.schedule_once(lambda dt: self.loading_spinner(self.home_manager, 'facture'), 0)

        self.dialog.open()

    async def recuperer_donnée(self, place):
        try:
            facture, paye, non_paye = await self.database.get_facture(self.current_client[0], self.current_client[5])
            Clock.schedule_once(lambda dt: self.afficher_tableau_facture(place, facture, paye, non_paye), 0)

        except Exception as e:
            print('recup don', e)

    def afficher_tableau_facture(self, place, result, paye, non_paye):
        if result:
            self.home_manager.get_screen('facture').ids.non_payé.text = f'Non payé :  {non_paye} AR'
            self.home_manager.get_screen('facture').ids.payé.text = f'Payé : {paye} AR'
            row_data = [(self.reverse_date(i[0]), f'{i[1]} Ar', i[2]) for i in result ]

            self.facture = MDDataTable(
                pos_hint={'center_x':.5, "center_y": .6},
                size_hint=(.75,.9),
                background_color_header = '#56B5FB',
                background_color= '#56B5FB',
                rows_num=5,
                elevation=0,
                use_pagination= True,
                column_data=[
                    ("Date", dp(50)),
                    ("Montant", dp(40)),
                    ("Etat", dp(30)),
                ],
                row_data=row_data
            )

            #self.liste_planning.bind(on_row_press=lambda instance, row:self.row_pressed_planning(liste_id, instance, row))
            place.add_widget(self.facture)

    def fenetre_acceuil(self, titre, ecran, client, date,type_traitement, durée, debut_contrat, fin_prévu):
        from kivymd.uix.dialog import MDDialog

        self.home_manager.current = ecran
        acceuil = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.7, .6),
            content_cls= self.home_manager
        )
        self.home_manager.height = '400dp'
        self.home_manager.width = '850dp'

        self.client_name = client
        asyncio.run_coroutine_threadsafe(self.current_client_info(client, date), self.loop)

        self.home_manager.get_screen('about_contrat').ids.titre.text =f" A propos du contrat de {client}"
        self.home_manager.get_screen('about_contrat').ids.date_contrat.text =f"Début du contrat : {date}"
        self.home_manager.get_screen('about_contrat').ids.debut_contrat.text =f"Début du contrat : {debut_contrat}"
        self.home_manager.get_screen('about_contrat').ids.fin_contrat.text =f"Fin du contrat : {fin_prévu}"
        self.home_manager.get_screen('about_contrat').ids.type_traitement.text =f"Type de traitement : {type_traitement}"
        self.home_manager.get_screen('about_contrat').ids.duree.text =f"Durée du contrat : {durée} mois"
        self.dialog = acceuil
        self.dialog.bind(on_dismiss=self.dismiss_home)

        self.dialog.open()

    def fenetre_client(self, titre, ecran):
        from kivymd.uix.dialog import MDDialog

        self.client_manager.current = ecran
        client = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint= (.8, .65) if ecran == 'option_client' else (.8, .85),
            content_cls= self.client_manager
        )
        self.client_manager.height = '390dp' if ecran == 'option_client' else '550dp'
        self.client_manager.width = '1000dp'

        self.dialog = client
        self.dialog.bind(on_dismiss=self.dismiss_client)

        self.dialog.open()

    def fenetre_planning(self, titre, ecran):
        from kivymd.uix.dialog import MDDialog

        self.dismiss_planning()
        if self.dialog != None:
            self.fermer_ecran()
        self.planning_manager.current = ecran
        height = {"option_decalage": '200dp',
                  "ecran_decalage": '360dp',
                  "selection_planning": '500dp',
                  "rendu_planning": '350dp',
                  "selection_element_tableau": "300dp",
                  "ajout_remarque": "350dp"}

        size_tableau = {"option_decalage": (.6, .3),
                        "ecran_decalage": (.7, .6),
                        "selection_planning": (.8, .6),
                        "rendu_planning": (.8, .58),
                        "selection_element_tableau": (.6, .4),
                        "ajout_remarque": (.6, .55)}

        width = {"option_decalage": '700dp',
                        "ecran_decalage": '1000dp',
                        "selection_planning": '1000dp',
                        "rendu_planning": '1000dp',
                        "selection_element_tableau": '750dp',
                        "ajout_remarque": '750dp'}

        planning = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=size_tableau[ecran],
            content_cls=self.planning_manager
        )

        self.planning_manager.height = height[ecran]
        self.planning_manager.width = width[ecran]

        self.dialog = planning
        self.dialog.bind(on_dismiss=self.dismiss_planning)

        self.dialog.open()

    def fenetre_histo(self, titre, ecran):
        from kivymd.uix.dialog import MDDialog

        self.historic_manager.current = ecran

        if self.historic_manager.parent:
            self.historic_manager.parent.remove_widget(self.historic_manager)
            self.fermer_ecran()

        histo = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.8, .65),
            content_cls=self.historic_manager
        )
        self.historic_manager.height ='500dp'
        self.historic_manager.width = '1000dp'

        self.dialog = histo

        self.dialog.open()

    def fenetre_account(self, titre, ecran):
        from kivymd.uix.dialog import MDDialog

        self.account_manager.current = ecran
        compte = MDDialog(
            md_bg_color='#56B5FB',
            title=titre,
            type='custom',
            size_hint=(.5, .35) if ecran != 'modif_info_compte' else (.8, .73),
            content_cls=self.account_manager
        )
        height = '300dp' if ecran == 'suppression_compte' else '450dp' if ecran == 'modif_info_compte' else'200dp'
        width = '630dp' if ecran == 'suppression_compte' else '1000dp' if ecran == 'modif_info_compte' else '600dp'
        self.account_manager.height = height
        self.account_manager.width = width

        self.dialog = compte
        self.dialog.bind(on_dismiss=self.dismiss_compte)

        self.dialog.open()

    def dismiss_contrat(self, *args):
        if self.contrat_manager.parent:
            self.contrat_manager.parent.remove_widget(self.contrat_manager)

    def dismiss_home(self, *args):
        if self.home_manager.parent:
            self.home_manager.parent.remove_widget(self.home_manager)

    def dismiss_client(self, *args):
        if self.client_manager.parent:
            self.client_manager.parent.remove_widget(self.client_manager)

    def dismiss_planning(self, *args):
        if self.planning_manager.parent:
            self.planning_manager.parent.remove_widget(self.planning_manager)

    def dismiss_histo(self, *args):
        if self.historic_manager.parent:
            self.historic_manager.parent.remove_widget(self.historic_manager)

    def dismiss_compte(self, *args):
        if self.account_manager.parent:
            self.account_manager.parent.remove_widget(self.account_manager)

    def dropdown_menu(self, button, menu_items, color):
        from kivymd.uix.menu import MDDropdownMenu

        self.menu = MDDropdownMenu(
            md_bg_color= color,
            items=menu_items,
            max_height = dp(146)
        )
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item, name, screen, champ):
        if screen == 'contrat':
            self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(screen).ids[champ].text = text_item
        elif screen == 'Home':
            self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(screen).ids[champ].text = text_item
        else:
            self.root.get_screen('signup').ids['type'].text = text_item
        self.menu.dismiss()

    def clear_fields(self, screen):
        sign_up = ['nom','prenom','Email','type','signup_username','signup_password','confirm_password']
        modif_compte = ['nom','prenom','email','username','password','confirm_password']
        login = ['login_username', 'login_password']
        new_contrat = ['date_new_contrat', 'debut_new_contrat', 'fin_new_contrat']
        new_client = ['date_contrat_client', 'ajout_client', 'nom_client', 'email_client', 'adresse_client', 'responsable_client', 'telephone']
        planning = ['mois_date', 'mois_fin', 'axe_client', 'type_traitement', 'date_prevu']
        facture = ['montant', 'mois_fin', 'axe_client', 'traitement_c', 'date_prevu', 'red_trait']
        signalement = ['motif', 'date_decalage', 'date_prevu']

        if screen == 'new_contrat':
            #pour l'ecran new_contrat
            self.contrat_manager.get_screen('new_contrat').ids['duree_new_contrat'].text = 'Déterminée'
            self.contrat_manager.get_screen('new_contrat').ids['cat_contrat'].text = 'Nouveau'

            #pour l'ecran ajout_client
            self.contrat_manager.get_screen('ajout_info_client').ids['axe_client'].text = 'Nord (N)'

            #pour l'ajout du planning
            self.contrat_manager.get_screen('ajout_planning').ids['red_trait'].text = '1 mois'

            for id in new_contrat:
                self.contrat_manager.get_screen('new_contrat').ids[id].text = ''
            for id in new_client:
                self.contrat_manager.get_screen('ajout_info_client').ids[id].text = ''
            for id in planning:
                self.contrat_manager.get_screen('ajout_planning').ids[id].text = ''
            for id in facture:
                self.contrat_manager.get_screen('ajout_facture').ids[id].text = ''

            self.contrat_manager.get_screen('new_contrat').ids.deratisation.active = False
            self.contrat_manager.get_screen('new_contrat').ids.desinfection.active = False
            self.contrat_manager.get_screen('new_contrat').ids.desinsectisation.active = False
            self.contrat_manager.get_screen('new_contrat').ids.nettoyage.active = False
            self.contrat_manager.get_screen('new_contrat').ids.fumigation.active = False
            self.contrat_manager.get_screen('new_contrat').ids.ramassage.active = False
            self.contrat_manager.get_screen('new_contrat').ids.anti_ter.active = False

        if screen == 'signup':
            for id in sign_up:
                self.root.get_screen('signup').ids[id].text = ''
        if screen == 'signalement':
            for id in signalement:
                self.planning_manager.get_screen('ecran_decalage').ids[id].text = ''
        if screen == 'login':
            for id in login:
                self.root.get_screen('login').ids[id].text = ''
        if screen == 'modif_info_compte':
            for id in modif_compte:
                self.account_manager.get_screen('modif_info_compte').ids[id].text = ''

    def enregistrer_client(self,nom, prenom, email, telephone, adresse, date_ajout, categorie_client, axe ):
        if not nom or not prenom or not email or not telephone or not adresse or not date_ajout or not categorie_client or not axe:
            self.show_dialog('Erreur', 'Veuillez remplir tous les champs')
        else:
            self.contrat_manager.get_screen('save_info_client').ids.titre.text = f'Enregistrement des informations sur {nom.capitalize()}'
            self.dismiss_contrat()
            self.fermer_ecran()
            self.fenetre_contrat('', 'save_info_client')

    def enregistrer_contrat(self, date_contrat, date_debut, date_fin, duree_contrat, categorie_contrat):
        dératisation = self.contrat_manager.get_screen('new_contrat').ids.deratisation.active
        désinfection = self.contrat_manager.get_screen('new_contrat').ids.desinfection.active
        désinsectisation = self.contrat_manager.get_screen('new_contrat').ids.desinsectisation.active
        nettoyage = self.contrat_manager.get_screen('new_contrat').ids.nettoyage.active
        fumigation = self.contrat_manager.get_screen('new_contrat').ids.fumigation.active
        ramassage = self.contrat_manager.get_screen('new_contrat').ids.ramassage.active
        anti_termite = self.contrat_manager.get_screen('new_contrat').ids.anti_ter.active

        if not dératisation and not désinfection and not désinsectisation and not nettoyage and not fumigation and not ramassage and not anti_termite:
            self.show_dialog("Erreur", "Veuillez choisir au moins un traitement")
            return

        if not date_contrat or not date_debut or not duree_contrat or not categorie_contrat:
            self.show_dialog('Erreur', 'Veuillez remplir tous les champs')
            return
        else:
            self.dismiss_contrat()
            self.fermer_ecran()
            self.contrat_manager.get_screen('ajout_info_client').ids.ajout_client.text = date_contrat
            self.contrat_manager.get_screen('ajout_info_client').ids.date_contrat_client.text = date_contrat

            self.contrat_manager.get_screen('save_info_client').ids.date_contrat.text = f'Date du contrat : {date_contrat}'
            self.contrat_manager.get_screen('save_info_client').ids.debut_contrat.text = f'Début du contrat : {date_debut}'
            self.contrat_manager.get_screen('save_info_client').ids.fin_contrat.text = 'Fin du contrat : Indéterminée'  if date_fin == '' else f'Fin du contrat : {date_fin}'

            self.fenetre_contrat('Ajout des informations sur le clients', 'ajout_info_client')

    async def all_clients(self, place):
        try:
            client_data = await self.database.get_all_client()
            if client_data:
                Clock.schedule_once(lambda dt: self.update_client_table_and_switch(place,client_data), 0.1)
            else:
                self.show_dialog('Information', 'Aucun client trouvé.')

        except Exception as e:
            print(f"Erreur lors de la récupération des clients: {e}")
            self.show_dialog('Erreur', 'Une erreur est survenue lors du chargement des clients.')

    def signaler(self):
        motif = self.planning_manager.get_screen('ecran_decalage').ids.motif.text
        date_decalage = self.planning_manager.get_screen('ecran_decalage').ids.date_decalage.text
        decaler = self.planning_manager.get_screen('ecran_decalage').ids.changer
        garder = self.planning_manager.get_screen('ecran_decalage').ids.garder

        self.fermer_ecran()
        self.dismiss_planning()
        async def enregistrer_signalment():
            from dateutil.relativedelta import relativedelta

            try:
                if decaler.active:
                    date  = datetime.strptime(self.reverse_date(date_decalage), '%Y-%m-%d')
                    newdate = abs(relativedelta(self.planning_detail[9], date))
                    await self.database.modifier_date_signalement(self.planning_detail[7], self.planning_detail[8], self.option.lower(), newdate.months)
                elif garder.active:
                    await self.database.modifier_date(self.planning_detail[8], self.reverse_date(date_decalage))

                await self.database.creer_signalment(self.planning_detail[8], motif, self.option.capitalize())
                Clock.schedule_once(lambda dt: self.show_dialog('', f"Signalement d'un {self.option.lower()} effectué"))
                Clock.schedule_once(lambda dt: self.clear_fields('signalement'))

            except Exception as e:
                print('enregistrement',e)

        asyncio.run_coroutine_threadsafe(enregistrer_signalment(), self.loop)

    def option_decalage(self, titre):
        self.planning_manager.get_screen('ecran_decalage').ids.titre.text= f'Signalement d\'un {titre} pour {self.planning_detail[0]}'
        label = "l'avancement" if titre == 'avancement' else 'le décalage'
        self.planning_manager.get_screen('ecran_decalage').ids.date_prevu.text = self.reverse_date(self.planning_detail[9])
        self.planning_manager.get_screen('ecran_decalage').ids.label_decalage.text = f'Date pour {label}'
        self.option = titre
        self.fenetre_planning('', 'ecran_decalage')

    def switch_to_home(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'Home'

    def switch_to_login(self):
        self.root.current =  'login'

    def switch_to_compte(self):
        ecran = 'compte' if self.admin else 'not_admin'
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  ecran
        if self.admin:
            place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('compte').ids.tableau_compte
            self.all_users(place)

        self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(ecran).ids.nom.text = f'Nom : {self.compte[1]}'
        self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(ecran).ids.prenom.text = f'Prénom : {self.compte[2]}'
        self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(ecran).ids.email.text = f'Email : {self.compte[3]}'
        self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(ecran).ids.username.text = f"Nom d'utilisateur : {self.compte[4]}"

    def switch_to_historique(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current ='choix_type'

    def switch_to_planning(self):
        root = self.root.get_screen('Sidebar').ids['gestion_ecran']
        place = root.get_screen('planning').ids.tableau_planning
        root.current = 'planning'

        # Afficher le spinner de chargement immédiatement
        Clock.schedule_once(lambda dt: self.loading_spinner('Sidebar', 'planning'), 0)

        # Charger les données en arrière-plan
        future = asyncio.run_coroutine_threadsafe(self.get_all_planning(), self.loop)

        # Une fois les données prêtes, injecter dans l'UI avec Clock
        def handle_result(future):
            try:
                result = future.result()
                Clock.schedule_once(lambda dt: self.tableau_planning(place, result), 0.5)
            except Exception as e:
                print("Erreur de chargement planning :", e)

        # Lancer le traitement une fois les données reçues
        threading.Thread(target=lambda: handle_result(future)).start()

    def switch_to_about(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'about'

    def switch_to_main(self):
        self.root.current = 'Sidebar'
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current =  'Home'
        self.reset()

    def switch_to_contrat(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current = 'contrat'
        boutton = self.root.get_screen('Sidebar').ids.contrat
        self.choose_screen(boutton)

        def chargement_contrat():
            asyncio.run_coroutine_threadsafe(self.get_client(), self.loop)

        Clock.schedule_once(lambda dt: self.loading_spinner('Sidebar','contrat'), 0)
        Clock.schedule_once(lambda dt: threading.Thread(target= chargement_contrat()), 0.5)

    def switch_to_client(self):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current = 'client'
        boutton = self.root.get_screen('Sidebar').ids.clients
        self.choose_screen(boutton)
        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('client').ids.tableau_client
        #place.clear_widgets()
        def chargement_client():
            asyncio.run_coroutine_threadsafe(self.all_clients(place), self.loop)

        Clock.schedule_once(lambda dt: self.loading_spinner('Sidebar','client'), 0)
        Clock.schedule_once(lambda dt: chargement_client(), 0.5)

    def afficher_historique(self, type_trait):
        from kivy.uix.screenmanager import SlideTransition

        self.root.get_screen('Sidebar').ids['gestion_ecran'].transition = SlideTransition(direction='left')
        self.root.get_screen('Sidebar').ids['gestion_ecran'].current ='historique'
        self.root.get_screen('Sidebar').ids['gestion_ecran'].transition = SlideTransition(direction='up')
        if type_trait == 'AT':
            categorie = 'AT: Anti termites'
        if type_trait == 'PC':
            categorie = 'PC'
        if type_trait == 'NI':
            categorie = 'NI: Nettoyage Industriel'
        if type_trait == 'RO':
            categorie = 'RO: Ramassage Ordures'

        self.historique_par_categorie(categorie)

    def loading_spinner(self,manager, ecran, show=True):
        gestion = None
        if manager == 'Sidebar':
            gestion = self.root.get_screen('Sidebar').ids['gestion_ecran']
        else:
            gestion = manager

        gestion.get_screen(ecran).ids.spinner.active = show
        gestion.get_screen(ecran).ids.spinner.opacity = 1 if show else 0

    def traitement_par_client(self, source):
        self.fermer_ecran()
        self.contrat_manager.get_screen('all_treatment').ids.titre.text = f'Tous les traitements de {self.current_client[1]}'
        place = self.contrat_manager.get_screen('all_treatment').ids.tableau_treat
        place.clear_widgets()

        if source == 'home':
            self.dismiss_home()
        if source == 'client':
            self.dismiss_client()

        Clock.schedule_once(lambda dt: self.switch_to_contrat(),0)
        Clock.schedule_once(lambda dt: self.fenetre_contrat('', 'all_treatment'), 0.5)

        def maj_ecran():
            asyncio.run_coroutine_threadsafe(self.liste_traitement_par_client(place, self.current_client[0]), self.loop)

        Clock.schedule_once(lambda dt: self.loading_spinner(self.contrat_manager, 'all_treatment'), 0)
        Clock.schedule_once(lambda dt: maj_ecran(), 0.8)

    def voir_planning_par_traitement(self):
        self.dismiss_contrat()
        self.fermer_ecran()
        btn_planning = self.root.get_screen('Sidebar').ids.planning
        self.choose_screen(btn_planning)
        self.fenetre_planning('', 'selection_planning')
        Clock.schedule_once(lambda dt: self.switch_to_planning(), 0)
        Clock.schedule_once(lambda dt: self.get_and_update(self.current_client[5], self.current_client[1],self.current_client[13]), 0)

    def voir_info_client(self,source, option):
        self.fermer_ecran()
        if source == 'home':
            self.dismiss_home()
        if source == 'contrat':
            self.dismiss_contrat()

        Clock.schedule_once(lambda dt: self.modification_client(self.current_client[1], option), 0.5)
        Clock.schedule_once(lambda dt: self.switch_to_client(),0)

    def dropdown_compte(self, button, name):
        type_compte = ['Administrateur', 'Utilisateur']
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
        type_trait = ['Dératisation', 'Désinsectisation', 'Désinfection', 'Nettoyage industriel',"Ramassages d'ordures", 'Fumigation']
        menu = type_tri if name=='home' else type_trait
        screen = 'tri' if name == 'home' else 'tri_trait'
        home = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x, name,'contrat', screen),
            } for i in menu
        ]
        self.dropdown_menu(button, home, (0.647, 0.847, 0.992, 1))

    def dropdown_histo(self, button, name):
        tri = ['Récents', 'Mois', 'Type de contrat']
        tri_trait = ['Dératisation', 'Désinsectisation', 'Désinfection', 'Nettoyage industriel',"Ramassages d'ordures", 'Fumigation']
        menu = tri if name=='tri' else tri_trait
        home = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.retour_histo(name,x),
            } for i in menu
        ]
        self.dropdown_menu(button, home, (0.647, 0.847, 0.992, 1))

    def retour_histo(self, champ, text):
        self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('historique').ids[champ].text = text
        self.menu.dismiss()

    def dropdown_new_contrat(self,button,  champ, screen):
        axe = ['Nord (N)', 'Sud (S)', 'Est (E)', 'Ouest (O)']
        durée = ['Déterminée', 'Indéterminée']
        categorie = ['Nouveau ', 'Renouvellement']
        type_client = ['Société', 'Organisation', 'Particulier']
        redondance = ['une seule fois', '1 mois', '2 mois', '3 mois', '4 mois', '6 mois']

        item_menu = axe if champ == 'axe_client' else durée if champ == 'duree_new_contrat' else categorie if champ == "cat_contrat" else redondance if champ == 'red_trait' else type_client
        menu = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.retour_new(x, champ, screen),
            } for i in item_menu
        ]
        self.dropdown_menu(button, menu, 'white')

    def render_excel(self):
        self.fenetre_planning('', 'rendu_planning')
        asyncio.run_coroutine_threadsafe(self.get_all_client(), self.loop)

    async def get_all_client(self):
        self.all_client = []

        try:
            client_data = await self.database.get_all_client_name()

            if client_data:
                for row in client_data:
                    if isinstance(row, tuple) and len(row) > 0:
                        self.all_client.append(row[0])
                    else:
                        self.all_client.append(row)

        except Exception as e:
            print(f"Une erreur est survenue lors de la récupération des clients: {e}")

    def dropdown_rendu_excel(self,button,  champ):
        type = ['Dératisation', 'Désinsectisation', 'Désinfection', 'Nettoyage Industriel', 'Anti Termites', 'Fumigation']
        mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', "Décembre"]
        client = self.all_client

        item_menu = type if champ == 'type_traitement_planning' else mois if champ == 'mois_planning' else client
        menu = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.retour_planning(x, champ),
            } for i in item_menu
        ]
        self.dropdown_menu(button, menu, 'white')

    def retour_new(self,text,  champ, screen):
        categ_client = ['Organisation', 'Entreprise', 'Particulier']
        if text == 'Indéterminée':
            self.contrat_manager.get_screen(screen).ids.fin_new_contrat.pos_hint = {"center_x": 0, "center_y": -10}
            self.contrat_manager.get_screen(screen).ids.label_fin.text = ''
            self.contrat_manager.get_screen(screen).ids.fin_icon.pos_hint = {"center_x": 0, "center_y": -10}

            #Ecran ajout planning
            self.contrat_manager.get_screen('ajout_planning').ids.mois_fin.pos_hint = {"center_x": 0, "center_y": -10}
            self.contrat_manager.get_screen('ajout_planning').ids.mois_fin.text = 'Indéterminée'
            self.contrat_manager.get_screen('ajout_planning').ids.label_fin_planning.text = ''

            #Ecran ajout facture
            self.contrat_manager.get_screen('ajout_facture').ids.mois_fin.pos_hint = {"center_x": 0, "center_y": -10}
            self.contrat_manager.get_screen('ajout_facture').ids.mois_fin.text = 'Indéterminée'
            self.contrat_manager.get_screen('ajout_facture').ids.label_fin_facture.text = ''

        elif text == 'Déterminée':
            self.contrat_manager.get_screen(screen).ids.fin_new_contrat.pos_hint = {"center_x": .83, "center_y": .8}
            self.contrat_manager.get_screen(screen).ids.fin_icon.pos_hint = {"center_x": .93, "center_y":.8}
            self.contrat_manager.get_screen(screen).ids.label_fin.text = 'Fin du contrat'

            #Ecran ajout planning
            self.contrat_manager.get_screen('ajout_facture').ids.mois_fin.text = ''
            self.contrat_manager.get_screen('ajout_planning').ids.mois_fin.pos_hint = {"center_x": .5, "center_y": .8}
            self.contrat_manager.get_screen('ajout_planning').ids.label_fin_planning.text = 'Mois de fin du traitement :'

            #Ecran ajout facture
            self.contrat_manager.get_screen('ajout_facture').ids.mois_fin.text = ''
            self.contrat_manager.get_screen('ajout_facture').ids.mois_fin.pos_hint = {"center_x": .5, "center_y": .8}
            self.contrat_manager.get_screen('ajout_facture').ids.label_fin_facture.text = 'Mois de fin du traitement :'

        elif text in categ_client:
            if text == 'Particulier':
                self.contrat_manager.get_screen(screen).ids.label_resp.text = 'Prénom'
            else:
                self.contrat_manager.get_screen(screen).ids.label_resp.text = 'Responsable'
        self.contrat_manager.get_screen(screen).ids[f'{champ}'].text = text
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

    def reset(self):
        for ids, item in self.root.get_screen('Sidebar').ids.items():
            if ids == 'home':
                self.root.get_screen('Sidebar').ids[ids].text_color = 'white'
            else:
                self.root.get_screen('Sidebar').ids[ids].text_color = 'black'

    def remove_tables(self, screen):
        if screen == 'compte':
            place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('compte').ids.tableau_compte
            place.remove_widget(self.account)

            self.all_users(place)

        elif screen == 'contrat':
            place1 = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('contrat').ids.tableau_contrat
            place1.remove_widget(self.liste_contrat)
            asyncio.run_coroutine_threadsafe(self.get_client(), self.loop)
            place2 = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen(
                 'client').ids.tableau_client
            place2.remove_widget(self.liste_client)
            asyncio.run_coroutine_threadsafe(self.all_clients(place2), self.loop)

    @mainthread
    def update_contract_table(self, place, contract_data):
        from kivymd.uix.label import MDLabel

        if not contract_data:
            label = MDLabel(
                text="Aucune donnée de planning disponible",
                halign="center"
            )
            place.add_widget(label)
            return

        row_data = []
        client_id = []
        for item in contract_data:
            try:
                # Vérifier que l'item contient au moins 4 éléments
                if len(item) >= 4:
                    client = item[0] if item[0] is not None else "N/A"
                    date = self.reverse_date(item[1]) if item[1] is not None else "N/A"
                    traitement = item[7] if item[7] is not None else "N/A"
                    duree = item[3] if item[3] is not None else 0

                    client_id.append(item[8])
                    row_data.append((client, date, traitement, f'{duree} mois' ))
                else:
                    print(f"Warning: Planning item doesn't have enough elements: {item}")

            except Exception as e:
                print(f"Error processing planning item: {e}")

        try:
            if self.liste_contrat.parent:
                self.liste_contrat.parent.remove_widget(self.liste_contrat)

            pagination = self.liste_contrat.pagination  # instance de TablePagination

            # Boutons disponibles dans TablePagination (selon version) :
            btn_prev = pagination.ids.button_back  # bouton "page précédente"
            btn_next = pagination.ids.button_forward

            self.page = 1

            def on_press_page(direction, instance=None):
                print(direction)
                max_page = (len(row_data) - 1) // 5 + 1
                if direction == 'moins' and self.page > 1:
                    self.page -= 1
                elif direction == 'plus' and self.page < max_page:
                    self.page += 1
                print(self.page)

            btn_prev.bind(on_press=partial(on_press_page, 'moins'))
            btn_next.bind(on_press=partial(on_press_page, 'plus'))

            self.liste_contrat.row_data = row_data
            self.liste_contrat.bind(on_row_press=partial(self.get_traitement_par_client, client_id))
            place.add_widget(self.liste_contrat)

        except Exception as e:
            print(f"Error creating contract table: {e}")

    def get_traitement_par_client(self, id, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        if self.contrat_manager.parent:
            self.contrat_manager.parent.remove_widget(self.contrat_manager)
            self.fermer_ecran()

        place = self.contrat_manager.get_screen('all_treatment').ids.tableau_treat
        place.clear_widgets()
        index_global = (self.page - 1) * 8 + row_num

        if 0 <= index_global < len(table.row_data):
            row_value = table.row_data[index_global]

        self.fenetre_contrat('', 'all_treatment')

        self.contrat_manager.get_screen('all_treatment').ids.titre.text = f'Tous les traitements de {row_value[0]}'
        self.client_name = row_value[0]

        def maj_ecran():
            asyncio.run_coroutine_threadsafe(self.liste_traitement_par_client(place, id[row_num]), self.loop)

        Clock.schedule_once(lambda dt: self.loading_spinner(self.contrat_manager,'all_treatment'),0.5)
        Clock.schedule_once(lambda dt: maj_ecran(),0.5)

    async def liste_traitement_par_client(self, place, nom_client):
        try:
            result = await self.database.traitement_par_client(nom_client)
            if result:
                Clock.schedule_once(lambda dt : self.show_about_treatment(place, result), 0.1)

        except Exception as e:
            print('erreur get traitement'+ str(e))

    def show_about_treatment(self, place, data):
        from kivymd.uix.label import MDLabel

        if not data:
            label = MDLabel(
                text="Aucune donnée de planning disponible",
                halign="center"
            )
            place.add_widget(label)
            return

        row_data = []
        for item in data:
            try:
                # Vérifier que l'item contient au moins 4 éléments
                if len(item) >= 3:
                    date = self.reverse_date(item[1]) if item[1] is not None else "N/A"
                    traitement = item[2] if item[2] is not None else "N/A"
                    duree = item[3] if item[3] is not None else "N/A"

                    row_data.append((date, traitement, f'{duree} jours' if item[7] == 12 else f'{duree} mois'))
                else:
                    print(f"Warning: Planning item doesn't have enough elements: {item}")
            except Exception as e:
                print(f"Error processing planning item: {e}")

            try:
                if self.all_treat.parent:
                    self.all_treat.parent.remove_widget(self.all_treat)
                self.all_treat.row_data = row_data

                pagination = self.all_treat.pagination  # instance de TablePagination

                # Boutons disponibles dans TablePagination (selon version) :
                btn_prev = pagination.ids.button_back  # bouton "page précédente"
                btn_next = pagination.ids.button_forward

                self.page = 1

                def on_press_page(direction, instance=None):
                    print(direction)
                    max_page = (len(row_data) - 1) // 5 + 1
                    if direction == 'moins' and self.page > 1:
                        self.page -= 1
                    elif direction == 'plus' and self.page < max_page:
                        self.page += 1
                    print(self.page)

                btn_prev.bind(on_press=partial(on_press_page, 'moins'))
                btn_next.bind(on_press=partial(on_press_page, 'plus'))

                self.all_treat.bind(on_row_press=self.row_pressed_contrat)
                place.add_widget(self.all_treat)
            except Exception as e:
                print(f'Error creating traitement table: {e}')

    def row_pressed_contrat(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        self.dismiss_contrat()
        self.fermer_ecran()
        self.fenetre_contrat('', 'option_contrat')

        index_global = (self.page - 1) * 8 + row_num

        if 0 <= index_global < len(table.row_data):
            row_value = table.row_data[index_global]

        async def maj_ecran():
            try:
                self.current_client = await self.database.get_current_contrat(self.client_name,self.reverse_date(row_value[0]), row_value[1])

                if self.current_client[3] == 'Particulier':
                    nom = self.current_client[1] + ' ' + self.current_client[2]
                else:
                    nom = self.current_client[1]

                if self.current_client[6] == 'Indéterminée':
                    fin = self.reverse_date(self.current_client[8])
                else :
                    fin = self.current_client[8]

                self.contrat_manager.get_screen('option_contrat').ids.titre.text = f'A propos de {nom}'
                self.contrat_manager.get_screen(
                    'option_contrat').ids.date_contrat.text = f'Contrat du : {self.reverse_date(self.current_client[4])}'
                self.contrat_manager.get_screen(
                    'option_contrat').ids.debut_contrat.text = f'Début du contrat : {self.reverse_date(self.current_client[7])}'
                self.contrat_manager.get_screen(
                    'option_contrat').ids.fin_contrat.text = f'Fin du contrat : {fin}'
                self.contrat_manager.get_screen(
                    'option_contrat').ids.type_traitement.text = f'Type de traitement : {self.current_client[5]}'
                self.contrat_manager.get_screen(
                    'option_contrat').ids.duree.text = f'Durée du contrat : {self.current_client[6]}'
                self.contrat_manager.get_screen(
                    'option_contrat').ids.axe.text = f'Axe du client: {self.current_client[11]}'

            except Exception as e:
                print(e)

        def ecran():
            asyncio.run_coroutine_threadsafe(maj_ecran(),self.loop)

        Clock.schedule_once(lambda x: ecran(), 0.5)

    def update_client_table_and_switch(self, place, client_data):
        if client_data:
            row_data = [(i[0], i[1], i[2], self.reverse_date(i[3])) for i in client_data]

            if self.liste_client.parent:
                self.liste_client.parent.remove_widget(self.liste_client)

            pagination = self.liste_client.pagination  # instance de TablePagination

            # Boutons disponibles dans TablePagination (selon version) :
            btn_prev = pagination.ids.button_back  # bouton "page précédente"
            btn_next = pagination.ids.button_forward

            self.page = 1

            def on_press_page(direction, instance=None):
                print(direction)
                max_page = (len(row_data) - 1) // 5 + 1
                if direction == 'moins' and self.page > 1:
                    self.page -= 1
                elif direction == 'plus' and self.page < max_page:
                    self.page += 1
                print(self.page)

            btn_prev.bind(on_press=partial(on_press_page, 'moins'))
            btn_next.bind(on_press=partial(on_press_page, 'plus'))

            self.liste_client.row_data = row_data
            self.liste_client.bind(on_row_press=self.row_pressed_client)
            place.clear_widgets()  # Supprimer l'ancien tableau si nécessaire
            place.add_widget(self.liste_client)

    def historique_par_client(self, source):
        self.fermer_ecran()
        self.dismiss_client()

        self.root.get_screen('Sidebar').ids['gestion_ecran'].current = 'historique'

        boutton = self.root.get_screen('Sidebar').ids.historique
        self.choose_screen(boutton)
        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('historique').ids.tableau_historic
        place.clear_widgets()

        async def get_histo():
            try:
                print(self.current_client)
                result = await self.database.get_historic_par_client(self.current_client[1])
                data = []
                id_planning = []

                if result:
                    for i in result:
                        data.append(i)
                        id_planning.append(i[4])
                else:
                    data.append(('Aucun', 'Aucun', 'Aucun', 'Aucun'))

                Clock.schedule_once(lambda dt: self.tableau_historic(place, data, id_planning), 0)

            except Exception as e:
                print('par client',e)

        def maj_ecran():
            asyncio.run_coroutine_threadsafe(get_histo(), self.loop)

        Clock.schedule_once(lambda dt: self.loading_spinner('Sidebar', 'historique'), 0)
        Clock.schedule_once(lambda dt: maj_ecran(), 0.5)

    async def current_client_info(self, nom_client, date):
        try:
            self.current_client = await self.database.get_current_client(nom_client,
                                                                        self.reverse_date(date))
        except Exception as e:
            print(e)

    def row_pressed_client(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]
        index_global = (self.page - 1) * 8 + row_num

        if 0 <= index_global < len(table.row_data):
            row_value = table.row_data[index_global]

        asyncio.run_coroutine_threadsafe(self.current_client_info(row_value[0], row_value[3]),self.loop)
        def maj_ecran():
            if self.current_client[3] == 'Particulier':
                nom = self.current_client[1] + ' ' + self.current_client[2]
            else:
                nom = self.current_client[1]

            if self.current_client[6] == 'Indéterminée':
                fin = self.reverse_date(self.current_client[8])
            else :
                fin = self.current_client[8]

            self.client_manager.get_screen('option_client').ids.titre.text = f'A propos de {nom}'
            self.client_manager.get_screen('option_client').ids.date_contrat.text = f'Contrat du : {self.reverse_date(self.current_client[4])}'
            self.client_manager.get_screen('option_client').ids.debut_contrat.text = f'Début du contrat : {self.reverse_date(self.current_client[7])}'
            self.client_manager.get_screen('option_client').ids.fin_contrat.text = f'Fin du contrat : {fin}'
            self.client_manager.get_screen('option_client').ids.type_traitement.text = f'Type de traitement : {self.current_client[4]}'
            self.client_manager.get_screen('option_client').ids.duree.text = f'Durée du contrat : {self.current_client[6]}'

        Clock.schedule_once(lambda x: self.fenetre_client('', 'option_client'))
        Clock.schedule_once(lambda x: maj_ecran())

    @mainthread
    def tableau_planning(self, place, result, dt=None):
        from kivymd.uix.label import MDLabel
        place.clear_widgets()
        # Vérifier si result existe et contient des données
        if not result:
            label = MDLabel(
                text="Aucune donnée de planning disponible",
                halign="center"
            )
            place.add_widget(label)
            return

        # Initialiser les listes pour les données
        row_data = []
        liste_id = []

        # Traiter les données avec vérification des indices
        for item in result:
            try:
                # Vérifier que l'item contient au moins 4 éléments
                if len(item) >= 4:
                    client = item[0] if item[0] is not None else "N/A"
                    traitement = item[1] if item[1] is not None else "N/A"
                    duree = item[2] if item[2] is not None else "N/A"
                    id_planning = item[3] if item[3] is not None else 0

                    row_data.append((client, traitement, duree, 'Aucun decalage'))
                    liste_id.append(id_planning)
                else:
                    print(f"Warning: Planning item doesn't have enough elements: {item}")
            except Exception as e:
                print(f"Error processing planning item: {e}")
                # Continuer avec les autres éléments sans interrompre

        # Vérifier si des données valides ont été trouvées
        if not row_data:
            label = MDLabel(
                text="Données de planning invalides ou mal formatées",
                halign="center"
            )
            place.add_widget(label)
            return

        try:
            if self.liste_planning.parent:
                self.liste_planning.parent.remove_widget(self.liste_planning)

            pagination = self.liste_planning.pagination

            btn_prev = pagination.ids.button_back
            btn_next = pagination.ids.button_forward

            self.page = 1

            def on_press_page(direction, instance=None):
                print(direction)
                max_page = (len(row_data) - 1) // 5 + 1
                if direction == 'moins' and self.page > 1:
                    self.page -= 1
                elif direction == 'plus' and self.page < max_page:
                    self.page += 1
                print(self.page)

            btn_prev.bind(on_press=partial(on_press_page, 'moins'))
            btn_next.bind(on_press=partial(on_press_page, 'plus'))
            self.liste_planning.row_data = row_data

            self.liste_planning.bind(on_row_press= partial(self.row_pressed_planning, liste_id))

            place.add_widget(self.liste_planning)
            #del self.liste_planning
        except Exception as e:
            print(f"Error creating planning table: {e}")

    @mainthread
    def tableau_selection_planning(self, place, data, traitement):
        from kivymd.uix.label import MDLabel

        if hasattr(self, 'liste_select_planning') and self.liste_select_planning is not None:
            if self.liste_select_planning.parent:
                self.liste_select_planning.parent.remove_widget(self.liste_select_planning)

        place.clear_widgets()

        if not data:
            label = MDLabel(
                text="Aucune donnée de planning disponible",
                halign="center"
            )
            place.add_widget(label)
            return

        row_data = []
        for mois, item in enumerate(data):
            try:
                # Vérifier que l'item contient au moins 4 éléments
                if len(item) >= 2:
                    date = self.reverse_date(item[0]) if item[0] is not None else "N/A"
                    etat = item[1] if item[1] is not None else "N/A"

                    row_data.append((date, f'{mois + 1}e mois' , etat))
                else:
                    print(f"Warning: Planning item doesn't have enough elements: {item}")
            except Exception as e:
                print(f"Error processing planning item: {e}")

        try:
            self.liste_select_planning = MyDatatable(
                pos_hint={'center_x': .5, "center_y": .5},
                size_hint=(.6, .85),
                elevation=0,
                rows_num=5,
                use_pagination=True,
                column_data=[
                    ("Date", dp(35)),
                    ("Statistique", dp(35)),
                    ("Etat du traitement", dp(40)),
                ]
            )

            self.liste_select_planning.row_data = row_data
            pagination = self.liste_select_planning.pagination
            btn_prev = pagination.ids.button_back
            btn_next = pagination.ids.button_forward

            self.page = 1

            def on_press_page( direction, instance=None):
                print(direction)
                max_page = (len(row_data) - 1) // 5 + 1
                if direction == 'moins' and self.page > 1:
                    self.page -= 1
                elif direction == 'plus' and self.page < max_page:
                    self.page += 1
                print(self.page)

            btn_prev.bind(on_press=partial(on_press_page,  'moins'))
            btn_next.bind(on_press=partial(on_press_page,  'plus'))

            self.liste_select_planning.bind(
                on_row_press=lambda instance, row: self.row_pressed_tableau_planning(traitement, instance, row))
            place.add_widget(self.liste_select_planning)

        except Exception as e:
            print(f'Error creating planning_detail table: {e}')

    def row_pressed_planning(self, list_id, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        index_global = (self.page - 1) * 8 + row_num

        if 0 <= index_global < len(table.row_data):
            row_value = table.row_data[index_global]

        self.fenetre_planning('', 'selection_planning')

        Clock.schedule_once(lambda dt: self.get_and_update(row_value[1], row_value[0], list_id[row_num]), 0.5)

    def get_and_update(self, data1, data2, data3):
        asyncio.run_coroutine_threadsafe(self.planning_par_traitement(data1, data2, data3), self.loop)

    async def planning_par_traitement(self, traitement, client, id_traitement):
        titre = traitement.partition('(')[0].strip()
        screen = self.planning_manager.get_screen('selection_planning')
        screen.ids.titre.text = f'Planning de {titre} pour {client}'

        place = screen.ids.tableau_select_planning
        Clock.schedule_once(lambda dt: place.clear_widgets(), 0)

        async def details():
            try:
                result = await self.database.get_details(id_traitement)
                if result:
                    threading.Thread(target=self.tableau_selection_planning(place, result, id_traitement)).start()
                    Clock.schedule_once(lambda dt :self.loading_spinner(self.planning_manager, 'selection_planning', show=True))
            except Exception as e:
                print('misy erreur :', e)

        def maj_ecran():
            asyncio.run_coroutine_threadsafe(details(), self.loop)

        Clock.schedule_once(lambda ct: maj_ecran(), 0.5)

    def row_pressed_tableau_planning(self, traitement,  table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        index_global = (self.page - 1) * 5 + row_num

        if 0 <= index_global < len(table.row_data):
            row_value = table.row_data[index_global]

        print(row_value)

        self.dismiss_planning()
        self.fermer_ecran()

        async def get():
            self.planning_detail = await self.database.get_info_planning(traitement, self.reverse_date(row_value[0]))
            print(self.planning_detail, type(self.planning_detail))

        asyncio.run_coroutine_threadsafe(get(), self.loop)

        if row.index % 3 == 0:
            self.home_manager.get_screen('modif_date').ids.date_prevu.text = row_value[0]
            self.modifier_date(source='planning')
        else:
            Clock.schedule_once(lambda dt: self.fenetre_planning('', 'selection_element_tableau'))
            Clock.schedule_once(lambda dt: maj_ui())

        def maj_ui():
            try:
                print('Maj ui', self.planning_detail)
                titre = self.planning_detail[1].split(' ')
                self.planning_manager.get_screen('selection_element_tableau').ids['titre'].text = f'{titre[0]} pour {self.planning_detail[0]}'
                self.planning_manager.get_screen('ajout_remarque').ids['titre'].text = f'{titre[0]} pour {self.planning_detail[0]}'
                self.planning_manager.get_screen('option_decalage').ids.client.text = f'Client: {self.planning_detail[0]}'

                self.planning_manager.get_screen('selection_element_tableau').ids['contrat'].text = f'Contrat du {self.reverse_date(self.planning_detail[3])} au {self.planning_detail[4]}'

                self.planning_manager.get_screen('selection_element_tableau').ids['mois'].text = f'Date du traitement : {row_value[0]}'
                self.planning_manager.get_screen('ajout_remarque').ids['date'].text = f'Date du traitement : {row_value[0]}'

                self.planning_manager.get_screen('selection_element_tableau').ids['mois_trait'].text = f'Mois du traitement: {row_value[1]}'
                self.planning_manager.get_screen('ajout_remarque').ids['mois_trait'].text = f'Mois du traitement: {row_value[1]}'

                self.planning_manager.get_screen('ajout_remarque').ids['duree'].text = f'Durée total du traitement : {self.planning_detail[2]}'

            except Exception as e:
                print( 'affichage detail ',e)

    def create_remarque(self):
        contenu = self.planning_manager.get_screen('ajout_remarque').ids.remarque.text
        paye = bool(self.planning_manager.get_screen('ajout_remarque').ids.paye_facture.active)

        if contenu:
            async def remarque(etat_paye):
                try:
                    await self.database.create_remarque(self.planning_detail[5],
                                                        self.planning_detail[8],
                                                        self.planning_detail[6],
                                                        contenu)

                    await self.database.update_etat_planning(self.planning_detail[8])
                    if etat_paye:
                        await self.database.update_etat_facture(self.planning_detail[6])
                    Clock.schedule_once(lambda dt: self.show_dialog('', 'Enregistrement réussi'))

                    Clock.schedule_once(lambda dt: self.fermer_ecran())
                    Clock.schedule_once(lambda dt: self.dismiss_planning())


                except Exception as e:
                    print('remarque tsy db',e)

            asyncio.run_coroutine_threadsafe(remarque(paye), self.loop)
            self.planning_manager.get_screen('ajout_remarque').ids.remarque.text = ''
            paye = False

        else:
            self.show_dialog('Erreur', 'Veuillez remplir la case de remarque')

    def historique_par_categorie(self, categorie):
        place = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('historique').ids.tableau_historic
        place.clear_widgets()

        datas = []
        id_planning = []
        async def get_histo():
            try:
                result = await self.database.get_historic(categorie)
                for i in result:
                    if None not in i:
                        datas.append(i)
                        id_planning.append(i[4])
                    else:
                        datas.append(('Aucun', 'Aucun', 'Aucun', 'Aucun'))

                Clock.schedule_once(lambda dt: self.tableau_historic(place, datas, id_planning))

            except Exception as e:
                print('histo par categ', e)

        def maj_ecran():
            asyncio.run_coroutine_threadsafe(get_histo(), self.loop)

        Clock.schedule_once(lambda dt: self.loading_spinner('Sidebar', 'historique'), 0)
        Clock.schedule_once(lambda dt: maj_ecran(), 0.5)

    def tableau_historic(self, place, data, planning_id):
        row_data = [(i[0], i[1], i[2], i[3] if i [3] != 'None' else 'pas de remarque') for i in data]
        if self.historique.parent:
            self.historique.parent.remove_widget(self.historique)

        pagination = self.historique.pagination  # instance de TablePagination

        # Boutons disponibles dans TablePagination (selon version) :
        btn_prev = pagination.ids.button_back  # bouton "page précédente"
        btn_next = pagination.ids.button_forward

        self.page = 1

        def on_press_page( direction, instance=None):
            print(direction)
            max_page = (len(row_data) - 1) // 5 + 1
            if direction == 'moins' and self.page > 1:
                self.page -= 1
            elif direction == 'plus' and self.page < max_page:
                self.page += 1
            print(self.page)

        btn_prev.bind(on_press=partial(on_press_page,  'moins'))
        btn_next.bind(on_press=partial(on_press_page,  'plus'))

        self.historique.row_data = row_data
        self.historique.bind(on_row_press=lambda instance, row: self.row_pressed_histo(instance, row, planning_id))
        place.add_widget(self.historique)

    def row_pressed_histo(self, table, row, planning_id):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data
        index_global = (self.page - 1) * 5 + row_num

        if 0 <= index_global < len(table.row_data):
            row_value = table.row_data[index_global]

        if row_value[0] == 'Aucun':
            return

        place = self.historic_manager.get_screen('histo_remarque').ids.tableau_rem_histo
        place.clear_widgets()
        self.fenetre_histo('', 'histo_remarque')
        def get_data():
            asyncio.run_coroutine_threadsafe(self.historique_remarque(place, planning_id[row_num]), self.loop)

        Clock.schedule_once(lambda c: self.loading_spinner(self.historic_manager, 'histo_remarque'), 0.5)
        Clock.schedule_once(lambda c: get_data(), 0.5)

    async def historique_remarque(self, place, planning_id):
        from kivymd.uix.label import MDLabel

        try:
            resultat = await self.database.get_historique_remarque(planning_id)
            Clock.schedule_once(lambda dt: self.tableau_rem_histo(place, resultat if resultat else []), 0)
        except Exception as e:
            print('Erreur lors de la récupération des remarques :', e)
            if place:
                place.clear_widgets()
                error_label = MDLabel(
                    text=f"Erreur lors du chargement de l'historique des remarques : {e}",
                    halign="center"
                )
                place.add_widget(error_label)
            else:
                print("Erreur: 'place' est None, impossible d'afficher le message d'erreur.")

    def tableau_rem_histo(self, place, data):
        from kivy.metrics import dp
        from kivymd.uix.label import MDLabel

        place.clear_widgets()

        row_data = []
        for item in data:
            try:
                if len(item) >= 2:
                    date = self.reverse_date(item[0]) if item[0] is not None else "N/A"
                    remarque = item[1] if item[1] is not None else "N/A"
                    avance = item[2] if item[2] is not None else 'Aucun'
                    decale = item[3] if item[3] is not None else 'Aucun'
                    row_data.append((date, remarque, avance, decale, item[4]))
                else:
                    print(f"Warning: L'élément de remarque historique n'a pas assez d'éléments (attendu 2+): {item}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'élément de remarque historique : {e}")

        if not row_data:
            label = MDLabel(
                text="Aucune remarque d'historique disponible.",
                halign="center"
            )
            place.add_widget(label)
            return

        try:
            if not hasattr(self, 'remarque_historique'):
                self.remarque_historique = MyDatatable(
                    pos_hint={'center_x': .5, "center_y": .53},
                    size_hint=(1, 1),
                    rows_num=5,
                    elevation=0,
                    column_data=[
                        ("Date", dp(30)),
                        ("Remarque", dp(60)),
                        ("Avancement", dp(35)),
                        ("Décalage", dp(35)),
                        ("Motif", dp(40)),
                    ]
                )

                self.remarque_historique.row_data = row_data

            place.add_widget(self.remarque_historique)

            del self.remarque_historique
        except Exception as e:
            print(f'Erreur lors de la création du tableau des remarques historiques : {e}')

    def all_users(self, place):
        async def data_account():
            try:
                users = await self.database.get_all_user()
                if users:
                    Clock.schedule_once(lambda dt: self.tableau_compte(place, users))
            except:
                self.show_dialog('erreur', 'Merde !!!')

        asyncio.run_coroutine_threadsafe(data_account(), self.loop)

    def tableau_compte(self, place, data):
        self.account = MDDataTable(
            pos_hint={'center_x': .5, "center_y": .53},
            size_hint=(1, 1),
            background_color_header='#D9D9D9',
            rows_num=len(data),
            elevation=0,
            column_data=[
                ("Nom d'utilisateur", dp(62)),
                ("Email", dp(80)),
            ],
            row_data=data
        )
        self.account.bind(on_row_press=self.row_pressed_compte)
        place.add_widget(self.account)

    def maj_compte(self, compte):
        self.account_manager.get_screen('compte_abt').ids['titre'].text = f'A propos de {compte[4]}'
        self.account_manager.get_screen('compte_abt').ids['nom'].text = f'Nom : {compte[1]}'
        self.account_manager.get_screen('compte_abt').ids['prenom'].text = f'Prénom : {compte[2]}'
        self.account_manager.get_screen('compte_abt').ids['email'].text = f'Email : {compte[3]}'

    def row_pressed_compte(self, table, row):
        row_num = int(row.index / len(table.column_data))
        row_data = table.row_data[row_num]

        async def about():
            self.not_admin = await self.database.get_user(row_data[0])
            Clock.schedule_once(lambda dt: self.dismiss_compte())
            Clock.schedule_once(lambda dt: self.maj_compte(self.not_admin))
            Clock.schedule_once(lambda dt: self.fenetre_account('', 'compte_abt'))

        asyncio.run_coroutine_threadsafe(about(), self.loop)

    def suppression_compte(self, username):
        nom = username.split(' ')
        self.account_manager.get_screen('suppression_compte').ids['titre'].text = f'Suppression du compte de {nom[3]}'
        self.dismiss_compte()
        self.fermer_ecran()
        self.fenetre_account('', 'suppression_compte')

    def modification_compte(self):
        self.dismiss_compte()

        titre = "Modification des informations de l'administrateur"  if self.compte[6] == 'Administrateur' else f"Modification des informations de {self.compte[4]}"
        self.account_manager.get_screen('modif_info_compte').ids.nom.text = self.compte[1]
        self.account_manager.get_screen('modif_info_compte').ids.prenom.text = self.compte[2]
        self.account_manager.get_screen('modif_info_compte').ids.email.text = self.compte[3]
        self.account_manager.get_screen('modif_info_compte').ids.username.text = self.compte[4]
        self.account_manager.get_screen('modif_info_compte').ids.titre_info.text = titre
        self.fenetre_account('', 'modif_info_compte')

    def modification_client(self ,nom,option ):
        self.dismiss_client()
        self.fermer_ecran()

        btn_enregistrer = self.client_manager.get_screen('modif_client').ids.enregistrer
        btn_annuler = self.client_manager.get_screen('modif_client').ids.annuler

        if option == 'voir':
            btn_annuler.text = 'Fermer'
            btn_enregistrer.opacity = 0
        else:
            btn_annuler.text = 'Annuler'
            btn_enregistrer.opacity = 1

        if self.current_client[3] == 'Particulier':
            self.client_manager.get_screen('modif_client').ids.label_resp.text = 'Prenom'
            nom = self.current_client[1] + ' ' + self.current_client[2]
        else:
            self.client_manager.get_screen('modif_client').ids.label_resp.text = 'Responsable'
            nom = self.current_client[1]

        self.client_manager.get_screen('modif_client').ids.date_contrat_client.text = self.reverse_date(self.current_client[4])
        self.client_manager.get_screen('modif_client').ids.cat_client.text = self.current_client[3]
        self.client_manager.get_screen('modif_client').ids.nom_client.text = self.current_client[1]
        self.client_manager.get_screen('modif_client').ids.email_client.text = self.current_client[9]
        self.client_manager.get_screen('modif_client').ids.adresse_client.text = self.current_client[10]
        self.client_manager.get_screen('modif_client').ids.axe_client.text = self.current_client[11]
        self.client_manager.get_screen('modif_client').ids.resp_client.text = self.current_client[2]
        self.client_manager.get_screen('modif_client').ids.telephone.text = self.current_client[12]
        self.fenetre_client(f'Modifications des informartion sur {nom}', 'modif_client')

    def enregistrer_modif_client(self,btn, nom, prenom, email, telephone, adresse, categorie, axe):
        if btn.opacity == 1:
            async def save():
                try:
                    Clock.schedule_once(lambda x: self.show_dialog('Enregistrements réussie', 'Les modifications sont enregistrer'))
                    Clock.schedule_once(lambda x: self.dismiss_client())
                    Clock.schedule_once(lambda x: self.fermer_ecran())
                    await self.database.update_client(self.current_client[0], nom, prenom, email, telephone, adresse, categorie, axe)
                    Clock.schedule_once(lambda c: self.remove_tables('contrat'))
                    self.current_client = None
                except Exception as e:
                    print(e)

            asyncio.run_coroutine_threadsafe(save(), self.loop)

    def suppression_contrat(self):

        fin = self.reverse_date(self.current_client[8]) if self.current_client[8] != 'Indéterminée' else 'Indéterminée'
        self.contrat_manager.get_screen('suppression_contrat').ids.titre.text = f'Suppression du contrat de {self.current_client[1]}'
        self.contrat_manager.get_screen('suppression_contrat').ids.date_contrat.text = f'Date du contrat: {self.reverse_date(self.current_client[4])}'
        self.contrat_manager.get_screen('suppression_contrat').ids.debut_contrat.text = f'Début du contrat: {self.reverse_date(self.current_client[7])}'
        self.contrat_manager.get_screen('suppression_contrat').ids.fin_contrat.text = f'Fin du contrat: {fin}'

        self.dismiss_contrat()
        self.fermer_ecran()
        self.fenetre_contrat('', 'suppression_contrat')

    async def populate_tables(self):
        data_current = []
        data_next = []
        home = self.root.get_screen('Sidebar').ids['gestion_ecran'].get_screen('Home')
        now = datetime.now()

        data_en_cours, data_prevision = await asyncio.gather(self.database.traitement_en_cours(now.year, now.month),self.database.traitement_prevision(now.year, now.month))

        # Création de data_current
        data_current = []
        for i in data_en_cours:
            data_current.append((self.reverse_date(i["date"]), i["traitement"], i['etat']))

        # Pour vérifier si un traitement spécifique existe dans data_current
        for i in data_prevision:
            traitement_a_verifier = i['traitement']

            # Vérifiez si ce traitement existe dans data_current (dans l'indice 1 de chaque tuple)
            traitement_existe = any(item[1] == traitement_a_verifier for item in data_current)

            # Vous pouvez également utiliser cette vérification pour décider si ajouter à data_next
            if not traitement_existe:  # Ajouter seulement si le traitement n'existe pas déjà
                row = (self.reverse_date(i["date"]), i["traitement"], i['etat'])
                data_next.append(row)

        Clock.schedule_once(lambda dt: self.home_tables(data_current, data_next, home))
        print('current', data_current)
        print('next' ,data_next)

    def home_tables(self, current, next, home):

        self.table_en_cours.row_data = current
        self.table_prevision.row_data = next

        if self.table_en_cours.parent and self.table_prevision.parent:
            self.table_en_cours.parent.remove_widget(self.table_en_cours)
            self.table_prevision.parent.remove_widget(self.table_prevision)

        home.ids.box_current.add_widget(self.table_en_cours)
        home.ids.box_next.add_widget(self.table_prevision)

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
    from kivy.core.text import LabelBase

    LabelBase.register(name='poppins',
                       fn_regular='font/Poppins-Regular.ttf')
    LabelBase.register(name='poppins-bold',
                       fn_regular='font/Poppins-Bold.ttf')
    Screen().run()
