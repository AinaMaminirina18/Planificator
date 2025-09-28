import asyncio
import datetime
import random

import aiomysql

import json
import os
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)


class DatabaseManager:
    """Gestionnaire de la base de données utilisant aiomysql."""
    def __init__(self, loop):
        self.loop = loop
        self.pool = None
        self.lock = asyncio.Lock()

    async def connect(self):
        try:
            """Crée un pool de connexions à la base de données."""
            self.pool = await aiomysql.create_pool(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                db="Planificator",
                loop=self.loop
            )
        except Exception as e:
            print('Erreur', e)

    async def add_user(self, nom, prenom, email, username,  password, type_compte):
        """Ajoute un utilisateur dans la base de données."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO Account (nom, prenom, email, username, password, type_compte) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nom, prenom, email, username, password, type_compte)
                )
                await conn.commit()

    async def update_user(self,new_nom, new_prenom, new_email, new_username, new_password, id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await conn.begin()
                await cur.execute(
                    "UPDATE Account SET nom = %s, prenom= %s, email=%s, username=%s, password=%s WHERE id_compte = %s",
                    (new_nom, new_prenom, new_email, new_username, new_password, id)
                )
                await conn.commit()

    async def delete_user(self, email):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM Account WHERE email = %s",
                    email
                )
                await conn.commit()

    async def get_facture(self, client_id, traitement):
        def format_montant(montant):
            return f"{montant:,}".replace(",", " ")

        factures = []
        total_paye = 0
        total_non_paye = 0
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("""SELECT  pdl.date_planification,
                                                    f.montant,
                                                    f.etat
                                            FROM
                                                Client c
                                            JOIN
                                                Contrat co ON c.client_id = co.client_id
                                            JOIN
                                                Traitement t ON co.contrat_id = t.contrat_id
                                            JOIN
                                                Planning p ON t.traitement_id = p.traitement_id
                                            JOIN
                                                TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                            JOIN
                                                PlanningDetails pdl ON p.planning_id = pdl.planning_id 
                                            JOIN
                                                Facture f ON pdl.planning_detail_id = f.planning_detail_id
                                            WHERE
                                                c.client_id = %s
                                            AND
                                                tt.typeTraitement = %s
                                            ORDER BY 
                                                pdl.date_planification""", (client_id,traitement))

                    resultat = await cursor.fetchall()

                    for row in resultat:
                        date, montant, etat = row
                        factures.append((date, format_montant(montant), etat))

                        if etat == 'Payé':
                            total_paye += montant
                        else:
                            total_non_paye += montant
                    return factures, format_montant(total_paye), format_montant(total_non_paye)
                except Exception as e:
                    print('get_facture' ,e)

    async def verify_user(self, username):
        """Vérifie si un utilisateur existe avec les informations données."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM Account WHERE username = (%s);", username
                )
                result = await cursor.fetchone()
                return result

    async def get_all_user(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT username, email FROM Account WHERE type_compte != 'Administrateur' ORDER BY username ASC"
                )
                resultat = await cursor.fetchall()
                return resultat

    async def get_current_user(self, id_compte):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM Account WHERE id_compte = %s",
                    id_compte
                )
                current = await cursor.fetchone()
                return current

    async def get_user(self, username):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM Account WHERE username = %s",
                    username
                )
                current = await cursor.fetchone()
                return current

    async def create_contrat(self, client_id,numero_contrat,  date_contrat, date_debut, date_fin, duree, duree_contrat, categorie,
                             max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.lock:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "INSERT INTO Contrat (client_id,reference_contrat, date_contrat, date_debut, date_fin, duree_contrat, duree, categorie) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                (client_id, numero_contrat, date_contrat, date_debut, date_fin, duree, duree_contrat, categorie)
                            )
                            await conn.commit()
                            return cur.lastrowid

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour create_contrat: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None

    async def create_client(self, nom, prenom, email, telephone, adresse, date_ajout, categorie, axe, nif, stat,
                            max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.lock:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "INSERT INTO Client (nom, prenom, email, telephone, adresse, nif, stat, date_ajout, categorie, axe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (nom, prenom, email, telephone, adresse, nif, stat, date_ajout, categorie, axe)
                            )
                            await conn.commit()
                            return cur.lastrowid

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour create_client: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None

    async def get_all_client(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT DISTINCT nom, email, adresse, date_ajout FROM Client ORDER BY nom ASC")
                return await cur.fetchall()

    async def typetraitement(self, categorie, type, max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.lock:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cursor:
                            await cursor.execute(
                                "INSERT INTO TypeTraitement (categorieTraitement, typeTraitement) VALUES (%s, %s)",
                                (categorie, type)
                            )
                            await conn.commit()
                            return cursor.lastrowid

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour typetraitement: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None

    async def creation_traitement(self, contrat_id, id_type_traitement, max_retries=3):
        async with self.lock:
            # Boucle de retry
            for attempt in range(max_retries):
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        try:
                            await conn.begin()
                            await cur.execute("""
                                INSERT INTO Traitement (contrat_id, id_type_traitement) 
                                VALUES (%s, %s)
                            """, (contrat_id, id_type_traitement))

                            await conn.commit()
                            print(f"✅ Traitement créé avec succès, ID: {cur.lastrowid}")
                            return cur.lastrowid

                        except Exception as e:
                            await conn.rollback()
                            print(f'creation_traitement tentative {attempt + 1}/{max_retries}: {e}')

                            # Erreurs retryables
                            retryable_errors = [
                                "Record has changed",
                                "Deadlock found",
                                "Connection lost",
                                "Lost connection to MySQL server",
                                "MySQL server has gone away"
                            ]

                            is_retryable = any(error in str(e) for error in retryable_errors)

                            if is_retryable and attempt < max_retries - 1:
                                wait_time = 0.1 * (2 ** attempt)  # Backoff exponentiel
                                print(f"🔄 Retry dans {wait_time} seconde...")
                                await asyncio.sleep(wait_time)
                                continue

                            # Dernière tentative ou erreur non-retryable
                            print("🚫 Abandon, erreur finale")
                            raise e

    async def create_planning(self, traitement_id, date_debut, mois_debut, mois_fin, redondance, date_fin,
                              max_retries=3):

        for attempt in range(max_retries):
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        await conn.begin()
                        await cur.execute("""
                            INSERT INTO Planning (traitement_id, date_debut_planification, mois_debut, mois_fin, redondance, date_fin_planification) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (traitement_id, date_debut, mois_debut, mois_fin, redondance, date_fin))

                        await conn.commit()
                        planning_id = cur.lastrowid

                        print(f"✅ Planning créé avec succès, ID: {planning_id}")
                        return planning_id

                    except Exception as e:
                        await conn.rollback()
                        print(f'create_planning tentative {attempt + 1}/{max_retries}: {e}')

                        # Erreurs retryables
                        retryable_errors = [
                            "Record has changed",
                            "Deadlock found",
                            "Connection lost",
                            "Lost connection to MySQL server",
                            "MySQL server has gone away"
                        ]

                        is_retryable = any(error in str(e) for error in retryable_errors)

                        if is_retryable and attempt < max_retries - 1:
                            wait_time = 0.1 * (2 ** attempt)  # Backoff exponentiel
                            print(f"🔄 Retry dans {wait_time} seconde...")
                            await asyncio.sleep(wait_time)
                            continue

                        # Dernière tentative ou erreur non-retryable
                        print("🚫 Abandon, erreur finale")
                        raise e

    async def traitement_en_cours(self, year, month):
        async with self.lock:
            async with self.pool.acquire() as conn:
                traitements = []
                async with conn.cursor() as curseur:
                    try:
                        await curseur.execute(
                            """SELECT c.nom AS nom_client,
                                      tt.typeTraitement AS type_traitement,
                                      pdl.statut,
                                      pdl.date_planification,
                                      p.planning_id,
                                      c.axe
                                   FROM
                                      Client c
                                   JOIN
                                      Contrat co ON c.client_id = co.client_id
                                   JOIN
                                      Traitement t ON co.contrat_id = t.contrat_id
                                   JOIN
                                      TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                   JOIN
                                      Planning p ON t.traitement_id = p.traitement_id
                                   JOIN
                                      PlanningDetails pdl ON p.planning_id = pdl.planning_id
                                   WHERE
                                      MONTH(pdl.date_planification) = %s
                                   AND
                                      YEAR(pdl.date_planification) = %s
                                   ORDER BY
                                      pdl.date_planification; """,
                            (month,year)
                        )
                        rows = await curseur.fetchall()
                        for nom, traitement, statut, date_str, idplanning, axe in rows:
                            traitements.append({
                                "traitement": f'{traitement.partition("(")[0].strip()} pour {nom}',
                                "date": date_str,
                                'etat': statut,
                                'axe': axe
                            })
                        return traitements
                    except Exception as e:
                        print('en cours', e)

    async def traitement_prevision(self, year, month):
        async with self.lock:
            async with self.pool.acquire() as conn:
                traitements = []
                async with conn.cursor() as curseur:
                    try:
                        await curseur.execute(
                            """SELECT c.nom AS nom_client,
                                      tt.typeTraitement AS type_traitement,
                                      pdl.statut,
                                      MIN(pdl.date_planification),
                                      p.planning_id,
                                      c.axe
                                   FROM
                                      Client c
                                   JOIN
                                      Contrat co ON c.client_id = co.client_id
                                   JOIN
                                      Traitement t ON co.contrat_id = t.contrat_id
                                   JOIN
                                      TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                   JOIN
                                      Planning p ON t.traitement_id = p.traitement_id
                                   JOIN
                                      PlanningDetails pdl ON p.planning_id = pdl.planning_id
                                   WHERE p.planning_id NOT IN (
                                        SELECT DISTINCT 
                                            p.planning_id
                                        FROM 
                                            Planning p
                                        WHERE 
                                            MONTH(pdl.date_planification) = %s
                                        AND 
                                            YEAR(pdl.date_planification) = %s
                                   )
                                   AND 
                                      pdl.date_planification >= CURDATE()
                                   AND 
                                      p.redondance != 1
                                   GROUP BY
                                      p.planning_id, tt.typeTraitement
                                   ORDER BY
                                      pdl.date_planification; """,
                            (month,year)
                        )
                        rows = await curseur.fetchall()
                        for nom, traitement, statut, date_str, idplanning, axe in rows:
                            traitements.append({
                                "traitement": f'{traitement.partition("(")[0].strip()} pour {nom}',
                                "date": date_str,
                                'etat': statut,
                                'axe': axe
                            })
                        return traitements
                    except Exception as e:
                        print('Prevision', e)

    import asyncio
    import random
    from typing import Optional

    async def create_facture(self, planning_id, montant, date, axe, etat='Non payé', max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.lock:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "INSERT INTO Facture (planning_detail_id, montant, date_traitement, etat, axe) VALUES (%s, %s, %s, %s, %s)",
                                (planning_id, montant, date, etat, axe)
                            )
                            await conn.commit()
                            return cur.lastrowid

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour create_facture: {e}")
                await conn.rollback()

                # Si c'est la dernière tentative, on lève l'exception
                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                # Calcul du délai avec backoff exponentiel + jitter
                base_delay = 2 ** attempt  # 1s, 2s, 4s, 8s...
                jitter = random.uniform(0, 0.1 * base_delay)  # Ajoute un peu d'aléatoire
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None

    async def update_client(self, client_id, nom, prenom, email, telephone, adresse,nif, stat, categorie, axe, max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        try:
                            await conn.begin()
                            await cur.execute(
                                "UPDATE Client SET nom = %s, prenom = %s, email = %s, telephone = %s, adresse = %s,nif=%s, stat=%s, categorie = %s, axe = %s WHERE client_id = %s",
                                (nom, prenom, email, telephone, adresse,nif,stat, categorie, axe, client_id)
                            )
                            await conn.commit()
                            return True
                        except Exception as e:
                            await conn.rollback()

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour update_client: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return False

    async def create_planning_details(self, planning_id, date, statut='À venir', max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        try:
                            await conn.begin()
                            await cur.execute(
                                "INSERT INTO PlanningDetails (planning_id, date_planification, statut) VALUES (%s, %s, %s)",
                                (planning_id, date, statut)
                            )
                            await conn.commit()
                            return cur.lastrowid
                        except Exception as e:
                            await conn.rollback()

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour create_planning_details: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt  # 1s, 2s, 4s, 8s...
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None
    
    async def get_all_planning(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        """SELECT c.nom AS nom_client,
                                  tt.typeTraitement AS type_traitement,
                                  p.redondance ,
                                  p.planning_id
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              Planning p ON t.traitement_id = p.traitement_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           ORDER BY
                              c.nom ASC;"""
                    )
                    return await cursor.fetchall()
                except Exception as e:
                    print('all planning', e)

    async def get_details(self, planning_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("""SELECT
                                                date_planification, statut
                                            FROM
                                                PlanningDetails
                                            WHERE
                                                planning_id = %s""", (planning_id,))
                    return await cursor.fetchall()
                except Exception as e:
                    print('details', e)

    async def get_info_planning(self, planning_id, date, max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        try:
                            await cursor.execute("""SELECT c.nom AS nom_client,
                                                      tt.typeTraitement AS type_traitement,
                                                      p.duree_traitement,
                                                      co.date_debut,
                                                      co.date_fin,
                                                      c.client_id,
                                                      f.facture_id,
                                                      p.planning_id,
                                                      pdl.planning_detail_id,
                                                      pdl.date_planification

                                                FROM
                                                    Client c
                                                JOIN
                                                    Contrat co ON c.client_id = co.client_id
                                                JOIN
                                                    Traitement t ON co.contrat_id = t.contrat_id
                                                JOIN
                                                    Planning p ON t.traitement_id = p.traitement_id
                                                JOIN
                                                    TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                                JOIN
                                                    PlanningDetails pdl ON p.planning_id = pdl.planning_id
                                                JOIN
                                                    Facture f ON pdl.planning_detail_id = f.planning_detail_id
                                                WHERE
                                                    p.planning_id = %s AND pdl.date_planification = %s""",
                                                 (planning_id, date))
                            resultat = await cursor.fetchone()
                            return resultat
                        except Exception as e:
                            print('get_info', e)

            except Exception as e:
                print(f'tentive {attempt +1 } échouée pour get info planning: {e}')

                await conn.rollback()
                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None

    async def modifier_date_signalement(self,planning_id, planning_detail_id, option, interval):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    avancement = """UPDATE PlanningDetails 
                                    SET 
                                        date_planification =DATE_SUB(date_planification, INTERVAL %s MONTH)
                                    WHERE
                                        planning_id = %s
                                    AND
                                        planning_detail_id >= %s"""

                    décalage = """UPDATE PlanningDetails 
                                  SET 
                                     date_planification =DATE_ADD(date_planification, INTERVAL %s MONTH)
                                  WHERE
                                     planning_id = %s
                                  AND
                                     planning_detail_id >= %s"""

                    requete = décalage if option == 'décalage' else avancement
                    await conn.begin()
                    await cur.execute(requete, (interval, planning_id, planning_detail_id))
                    await conn.commit()

                except Exception as e:
                    await conn.rollback()
                    print('Changement de date', e)

    async def modifier_date(self, planning_detail_id, new_date):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await conn.begin()
                    await cur.execute('''UPDATE PlanningDetails
                                   SET
                                      date_planification = %s
                                   WHERE
                                      planning_detail_id = %s''', (new_date, planning_detail_id))
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()

    async def create_facture(self, planning_id, montant, date, axe, etat='Non payé', max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.lock:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            try:
                                await conn.begin()
                                await cur.execute(
                                    "INSERT INTO Facture (planning_detail_id, montant, date_traitement, etat, axe) VALUES (%s, %s, %s, %s, %s)",
                                    (planning_id, montant, date, etat, axe)
                                )
                                await conn.commit()
                                return cur.lastrowid
                            except Exception as e:
                                await conn.rollback()

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour create_facture: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None
    
    async def create_remarque(self,client, planning_details, facture, contenu, probleme, action):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                    "INSERT INTO Remarque (client_id, planning_detail_id, facture_id, contenu, issue, action) VALUES (%s, %s, %s, %s,%s, %s)",
                    (client, planning_details, facture, contenu, probleme, action))
                    await conn.commit()
                except Exception as e:
                    print("remarque",e)

    async def get_historique_remarque(self, planning_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """ SELECT
                                pdl.date_planification AS Date, 
                                COALESCE(NULLIF(r.contenu, ''), 'Aucune remarque') AS Remarque, 
                                COALESCE(sa.motif, 'Aucun') AS Avancement, 
                                COALESCE(sd.motif, 'Aucun') AS Décalage, 
                                COALESCE(NULLIF(r.issue, ''), 'Aucun problème') AS probleme, 
                                COALESCE(NULLIF(r.action, ''), 'Aucune action') AS action
                            FROM
                               Client c
                            JOIN
                               Contrat co ON c.client_id = co.client_id
                            JOIN
                               Traitement t ON co.contrat_id = t.contrat_id
                            JOIN
                               TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                            JOIN
                               Planning p ON t.traitement_id = p.traitement_id
                            JOIN
                               PlanningDetails pdl ON p.planning_id = pdl.planning_id
                            JOIN
                               Remarque r ON pdl.planning_detail_id = r.planning_detail_id
                            LEFT JOIN
                                Signalement sa ON r.planning_detail_id = sa.planning_detail_id AND sa.type = 'Avancement'
                            LEFT JOIN
                                Signalement sd ON r.planning_detail_id = sd.planning_detail_id AND sd.type = 'Décalage'
                            WHERE
                                p.planning_id = %s;""", (planning_id,))
                    return await cur.fetchall()

                except Exception as e:
                    print('histo remarque',e)

    async def update_etat_facture(self, facture, reference, payement, etablissement, date, num_cheque):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await conn.begin()
                    await cur.execute(
                        """ UPDATE Facture 
                            SET reference_facture = %s,
                                etablissement_payeur = %s, 
                                date_cheque = %s, 
                                numero_cheque = %s, 
                                etat = %s, 
                                mode = %s 
                            WHERE facture_id = %s ;""", (reference, etablissement, date, num_cheque, 'Payé', payement, facture))
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    print("update facture", e)

    async def update_etat_planning(self, details_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                    "UPDATE PlanningDetails SET statut = %s WHERE planning_detail_id = %s",('Effectué', details_id))
                    await conn.commit()
                except Exception as e:
                    print("update planning",e)

    async def creer_signalment(self,planning_detail, motif, option):
        async with self.pool.acquire() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute("""INSERT INTO Signalement (planning_detail_id, motif, type) VALUES (%s, %s, %s)""",
                                   (planning_detail, motif, option))
                    await conn.commit()
            except Exception as e:
                print('signalement', e)

    async def get_historic_par_client(self, nom):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(""" SELECT c.nom,
                                                co.duree,
                                                tt.typeTraitement,
                                                count(r.remarque_id),
                                                p.planning_id
                                             FROM
                                                Client c
                                             JOIN
                                                Contrat co ON c.client_id = co.client_id
                                             JOIN
                                                Traitement t ON co.contrat_id = t.contrat_id
                                             JOIN
                                                TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                             JOIN
                                                Planning p ON t.traitement_id = p.traitement_id
                                             JOIN
                                                PlanningDetails pdl ON p.planning_id = pdl.planning_id
                                             JOIN
                                                Remarque r ON pdl.planning_detail_id = r.planning_detail_id
                                             WHERE
                                                c.nom = %s
                                             GROUP BY
                                                tt.typetraitement
                                                """, (nom,))
                    result = await cursor.fetchall()
                    print(result)
                    return result
                except Exception as e:
                    print('histo',e)

    async def get_historic(self, categorie):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(""" SELECT c.nom,
                                                co.duree,
                                                tt.typeTraitement,
                                                count(r.remarque_id),
                                                p.planning_id
                                             FROM
                                                Client c
                                             JOIN
                                                Contrat co ON c.client_id = co.client_id
                                             JOIN
                                                Traitement t ON co.contrat_id = t.contrat_id
                                             JOIN
                                                TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                             JOIN
                                                Planning p ON t.traitement_id = p.traitement_id
                                             JOIN
                                                PlanningDetails pdl ON p.planning_id = pdl.planning_id
                                             JOIN
                                                Remarque r ON pdl.planning_detail_id = r.planning_detail_id
                                             WHERE
                                                tt.categorieTraitement = %s
                                                """, (categorie,))
                    result = await cursor.fetchall()
                    print(result)
                    return result
                except Exception as e:
                    print('histo',e)
                    
    async def get_current_contrat(self, client, date, traitement):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("""SELECT c.client_id AS id,
                                  c.nom AS nom_client,
                                  c.prenom AS prenom_client,
                                  c.categorie AS categorie,
                                  co.date_contrat,
                                  tt.typeTraitement AS type_traitement,
                                  co.duree AS duree_contrat,
                                  co.date_debut AS debut_contrat,
                                  co.date_fin AS fin_contrat,
                                  c.email,
                                  c.adresse,
                                  c.axe,
                                  c.telephone,
                                  p.planning_id,
                                  f.facture_id,
                                  c.nif,
                                  c.stat
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           JOIN
                               Planning p ON t.traitement_id = p.traitement_id
                           JOIN
                               PlanningDetails pld ON p.planning_id = pld.planning_id
                           JOIN
                               Facture f ON pld.planning_detail_id = f.planning_detail_id
                           WHERE
                              c.nom = %s AND co.date_contrat = %s AND tt.TypeTraitement = %s; """, (client, date, traitement))
                    resultat = await cursor.fetchone()
                    return resultat
                except Exception as e:
                    print(e)

    async def delete_client(self, id_contrat):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await conn.begin() #commencer une transaction
                    await cursor.execute("""DELETE FROM Client where client_id = %s""", (id_contrat,))
                    await conn.commit()
                except Exception as e:
                    await conn.rollback() #rollback en cas d'erreur
                    print("Delete",e)

    async def get_current_client(self, client, date):
        print(client, date)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("""SELECT c.client_id AS id,
                                  c.nom AS nom_client,
                                  c.prenom AS prenom_client,
                                  c.categorie AS categorie,
                                  co.date_contrat,
                                  tt.typeTraitement AS type_traitement,
                                  co.duree AS duree_contrat,
                                  co.date_debut AS debut_contrat,
                                  co.date_fin AS fin_contrat,
                                  c.email,
                                  c.adresse,
                                  c.axe,
                                  c.telephone,
                                  p.planning_id,
                                  f.facture_id,
                                  c.nif,
                                  c.stat
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           JOIN
                               Planning p ON t.traitement_id = p.traitement_id
                           JOIN
                               PlanningDetails pld ON p.planning_id = pld.planning_id
                           JOIN
                               Facture f ON pld.planning_detail_id = f.planning_detail_id
                           WHERE
                              c.nom = %s AND co.date_contrat = %s; """, (client, date))
                    resultat = await cursor.fetchone()
                    print(resultat)
                    return resultat
                except Exception as e:
                    print(e)
                    
    async def get_client(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        """SELECT DISTINCT c.nom ,
                                  co.date_contrat,
                                  tt.typeTraitement,
                                  GROUP_CONCAT(DISTINCT p.redondance),
                                  co.date_debut ,
                                  co.date_fin ,
                                  c.categorie ,
                                  count(t.traitement_id),
                                  c.client_id
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           JOIN
                              Planning p ON t.traitement_id = p.traitement_id
                           GROUP BY
                              c.client_id
                           ORDER BY
                              c.nom ASC;"""
                    )
                    result = await cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)
                    
    async def traitement_par_client(self, idclient):
        async with self.pool.acquire() as conn :
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        """SELECT c.nom AS nom_client,
                                  co.date_contrat,
                                  tt.typeTraitement AS type_traitement,
                                  co.duree_contrat AS duree_contrat,
                                  co.date_debut AS debut_contrat,
                                  co.date_fin AS fin_contrat,
                                  c.categorie AS categorie,
                                  p.redondance
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           JOIN
                              Planning p ON t.traitement_id = p.traitement_id
                           WHERE
                              c.client_id = %s;"""
                    , (idclient,))
                    result = await cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)

    import asyncio
    import random
    from typing import Optional

    async def create_facture(self, planning_id, montant, date, axe, etat='Non payé', max_retries=3):
        """
        Crée une facture avec retry automatique et backoff exponentiel

        Args:
            planning_id: ID du planning
            montant: Montant de la facture
            date: Date de traitement
            axe: Axe de la facture
            etat: État de la facture (défaut: 'Non payé')
            max_retries: Nombre maximum de tentatives (défaut: 3)

        Returns:
            ID de la facture créée ou None en cas d'échec
        """
        for attempt in range(max_retries + 1):
            try:
                async with self.lock:
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            await cur.execute(
                                "INSERT INTO Facture (planning_detail_id, montant, date_traitement, etat, axe) VALUES (%s, %s, %s, %s, %s)",
                                (planning_id, montant, date, etat, axe)
                            )
                            await conn.commit()
                            return cur.lastrowid

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour create_facture: {e}")
                await conn.rollback()

                # Si c'est la dernière tentative, on lève l'exception
                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                # Calcul du délai avec backoff exponentiel + jitter
                base_delay = 2 ** attempt  # 1s, 2s, 4s, 8s...
                jitter = random.uniform(0, 0.1 * base_delay)  # Ajoute un peu d'aléatoire
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return None

    async def update_client(self, client_id, nom, prenom, email, telephone, adresse, categorie, axe, max_retries=3):
        for attempt in range(max_retries + 1):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await conn.begin()
                        await cur.execute(
                            "UPDATE Client SET nom = %s, prenom = %s, email = %s, telephone = %s, adresse = %s, categorie = %s, axe = %s WHERE client_id = %s",
                            (nom, prenom, email, telephone, adresse, categorie, axe, client_id)
                        )
                        await conn.commit()
                        return True

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée pour update_client: {e}")
                await conn.rollback()

                if attempt == max_retries:
                    print(f"Échec définitif après {max_retries + 1} tentatives")
                    raise e

                base_delay = 2 ** attempt
                jitter = random.uniform(0, 0.1 * base_delay)
                delay = base_delay + jitter

                print(f"Retry dans {delay:.2f}s...")
                await asyncio.sleep(delay)

        return False

    async def un_jour(self, contrat_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await conn.begin()
                await cur.execute(
                    "UPDATE Contrat SET duree_contrat = 1 WHERE contrat_id = %s",
                    (contrat_id, ))
                await conn.commit()

    async def get_all_client_name(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """SELECT DISTINCT CONCAT(nom , ' ', prenom) From Client """
                    )
                    result = await cur.fetchall()
                    return result
                except Exception as e:
                    print('error get client ', e)

    async def get_facture_id(self, client_id, date):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        """SELECT f.facture_id
                           FROM Facture f
                           JOIN PlanningDetails pd ON f.planning_detail_id = pd.planning_detail_id
                           JOIN Planning p ON pd.planning_id = p.planning_id
                           JOIN Traitement t ON p.traitement_id = t.traitement_id
                           JOIN Contrat c ON t.contrat_id = c.contrat_id
                           WHERE c.client_id = %s
                           AND pd.date_planification = %s;""", (client_id, date)
                    )
                    result = await cursor.fetchone()
                    return result
                except Exception as e:
                    print("aaa", e)

    async def majMontantEtHistorique(self, facture_id: int, old_amount: float, new_amount: float,
                                     changed_by: str = 'System'):
        """
        Met à jour le montant d'une facture et enregistre l'ancien/nouveau montant
        dans la table d'historique.
        """

        print("ato")
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # Commencer une transaction explicite
                    await conn.begin()

                    # 1. Mettre à jour le montant dans la table Facture
                    update_query = "UPDATE Facture SET montant = %s WHERE facture_id = %s;"
                    await cursor.execute(update_query, (new_amount, facture_id))
                    print('fini')

                    # 2. Insérer l'entrée d'historique
                    insert_history_query = """
                        INSERT INTO Historique_prix
                        (facture_id, old_amount, new_amount, change_date, changed_by)
                        VALUES (%s, %s, %s, %s, %s);
                    """
                    await cursor.execute(insert_history_query,
                                         (facture_id, old_amount, new_amount, datetime.datetime.now(), changed_by))
                    print('fini 2')

                    # Valider la transaction
                    await conn.commit()
                    print("Transaction validée")
                    return True

                except Exception as e:
                    # Annuler la transaction en cas d'erreur
                    await conn.rollback()
                    print(f"Erreur lors de la modification de la facture et de l'enregistrement de l'historique : {e}")
                    return False

    #Pour les excels

    async def get_factures_data_for_client_comprehensive(self, client_name: str, start_date: datetime.date = None,
                                                         end_date: datetime.date = None):
        conn = None
        try:
            conn = await self.pool.acquire()
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = """
                        SELECT cl.nom                  AS client_nom,
                               COALESCE(cl.prenom, '') AS client_prenom,
                               cl.adresse              AS client_adresse,
                               cl.telephone            AS client_telephone,
                               cl.categorie            AS client_categorie,
                               cl.axe                  AS client_axe,
                               co.contrat_id,
                               co.reference_contrat    AS `Référence Contrat`,
                               co.date_contrat,
                               co.date_debut           AS contrat_date_debut,
                               co.date_fin             AS contrat_date_fin,
                               co.statut_contrat,
                               co.duree                AS contrat_duree_type,
                               f.reference_facture     AS `Numéro Facture`,
                               tt.typeTraitement       AS `Type de Traitement`,
                               pd.date_planification   AS `Date de Planification`,
                               pd.statut               AS `Etat du Planning`,
                               p.redondance            AS `Redondance (Mois)`,
                               f.date_traitement       AS `Date de Facturation`,
                               f.etat                  AS `Etat de Paiement`,
                               f.mode                  AS `Mode de Paiement`,
                               f.date_cheque         AS `Date de Paiement`,
                               f.numero_cheque         AS `Numéro du Chèque`,
                               f.etablissement_payeur   AS `Établissement Payeur`,
                               COALESCE(
                                       (SELECT hp.new_amount
                                        FROM Historique_prix hp
                                        WHERE hp.facture_id = f.facture_id
                                        ORDER BY hp.change_date DESC, hp.history_id DESC
                                        LIMIT 1),
                                       f.montant
                               )                       AS `Montant Facturé`
                        FROM Client cl
                                 JOIN Contrat co ON cl.client_id = co.client_id
                                 JOIN Traitement tr ON co.contrat_id = tr.contrat_id
                                 JOIN TypeTraitement tt ON tr.id_type_traitement = tt.id_type_traitement
                                 JOIN Planning p ON tr.traitement_id = p.traitement_id
                                 INNER JOIN PlanningDetails pd ON p.planning_id = pd.planning_id
                                 INNER JOIN Facture f ON pd.planning_detail_id = f.planning_detail_id
                        WHERE cl.nom = %s
                        """
                params = [client_name]

                if start_date and end_date:
                    query += " AND f.date_traitement BETWEEN %s AND %s"
                    params.append(start_date)
                    params.append(end_date)
                elif start_date:
                    query += " AND f.date_traitement >= %s"
                    params.append(start_date)
                elif end_date:
                    query += " AND f.date_traitement <= %s"
                    params.append(end_date)

                query += " ORDER BY `Date de Planification` ASC, `Date de Facturation` ASC;"

                await cursor.execute(query, tuple(params))
                result = await cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erreur lors de la récupération des données de facture complètes : {e}")
            return []
        finally:
            if conn:
                self.pool.release(conn)


    async def obtenirDataFactureClient(self, client_name: str, year: int, month: int):
        conn = None
        try:
            conn = await self.pool.acquire()
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = """
                        SELECT cl.nom                  AS client_nom,
                               COALESCE(cl.prenom, '') AS client_prenom,
                               cl.adresse              AS client_adresse,
                               cl.telephone            AS client_telephone,
                               cl.categorie            AS client_categorie,
                               cl.axe                  AS client_axe,
                               co.reference_contrat    AS `Référence Contrat`,
                               f.reference_facture     AS `Numéro Facture`,
                               f.date_traitement       AS `Date de traitement`,
                               tt.typeTraitement       AS `Traitement (Type)`,
                               pd.statut               AS `Etat traitement`,
                               f.etat                  AS `Etat paiement (Payée ou non)`,
                               f.mode                  AS `Mode de Paiement`,
                               f.date_cheque         AS `Date de Paiement`,
                               f.numero_cheque         AS `Numéro du Chèque`,
                               f.etablissement_payeur   AS `Établissement Payeur`,
                               COALESCE(
                                       (SELECT hp.new_amount
                                        FROM Historique_prix hp
                                        WHERE hp.facture_id = f.facture_id
                                        ORDER BY hp.change_date DESC, hp.history_id DESC
                                        LIMIT 1),
                                       f.montant
                               )                       AS montant_facture
                        FROM Facture f
                                 JOIN PlanningDetails pd ON f.planning_detail_id = pd.planning_detail_id
                                 JOIN Planning p ON pd.planning_id = p.planning_id
                                 JOIN Traitement tr ON p.traitement_id = tr.traitement_id
                                 JOIN TypeTraitement tt ON tr.id_type_traitement = tt.id_type_traitement
                                 JOIN Contrat co ON tr.contrat_id = co.contrat_id
                                 JOIN Client cl ON co.client_id = cl.client_id
                        WHERE cl.nom = %s
                          AND YEAR(f.date_traitement) = %s
                          AND MONTH(f.date_traitement) = %s
                        ORDER BY f.date_traitement;
                        """
                await cursor.execute(query, (client_name, year, month))
                result = await cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erreur lors de la récupération des données de facture : {e}")
            return []
        finally:
            if conn:
                self.pool.release(conn)

    async def get_traitements_for_month(self, year: int, month: int):
        conn = None
        try:
            conn = await self.pool.acquire()
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = """
                        SELECT pd.date_planification        AS `Date du traitement`,
                               tt.typeTraitement            AS `Traitement concerné`,
                               tt.categorieTraitement       AS `Catégorie du traitement`,
                               CONCAT(c.nom, ' ', c.prenom) AS `Client concerné`,
                               c.categorie                  AS `Catégorie du client`,
                               c.axe                        AS `Axe du client`,
                               pd.statut                    AS `Etat traitement` -- AJOUT DE CETTE COLONNE
                        FROM PlanningDetails pd
                                 JOIN
                             Planning p ON pd.planning_id = p.planning_id
                                 JOIN
                             Traitement t ON p.traitement_id = t.traitement_id
                                 JOIN
                             TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                                 JOIN
                             Contrat co ON t.contrat_id = co.contrat_id
                                 JOIN
                             Client c ON co.client_id = c.client_id
                        WHERE YEAR(pd.date_planification) = %s
                          AND MONTH(pd.date_planification) = %s
                        ORDER BY pd.date_planification;
                        """
                await cursor.execute(query, (year, month))
                result = await cursor.fetchall()
                return result
        except Exception as e:
            print(f"Erreur lors de la récupération des traitements : {e}")
            return []
        finally:
            if conn:
                self.pool.release(conn)

    #Abrogation contrat
    async def get_planningdetails_id(self, planning_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("""SELECT pdl.planning_detail_id,pdl.date_planification
                                            FROM PlanningDetails pdl
                                            JOIN Planning p ON pdl.planning_id = p.planning_id
                                            WHERE p.planning_id = %s 
                                            AND pdl.date_planification >= %s;""",
                                         (planning_id, datetime.datetime.today()))
                    result = await cursor.fetchone()
                    return result
                except Exception as e:
                    print('Get details', e)

    async def get_planning_detail_info(self, planning_detail_id: int):
        """
        Récupère les informations détaillées d'un planning_detail spécifique,
        incluant les IDs du planning, traitement et contrat associés.
        Prend le pool de connexions en argument.
        """
        conn = None
        try:
            conn = await self.pool.acquire()  # Obtenir une connexion du pool
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = """
                        SELECT pd.planning_detail_id, \
                               pd.planning_id, \
                               pd.date_planification, \
                               pd.statut, \
                               p.traitement_id, \
                               t.contrat_id
                        FROM PlanningDetails pd \
                                 JOIN \
                             Planning p ON pd.planning_id = p.planning_id \
                                 JOIN \
                             Traitement t ON p.traitement_id = t.traitement_id
                        WHERE pd.planning_detail_id = %s; \
                        """
                await cursor.execute(query, (planning_detail_id,))
                result = await cursor.fetchone()
                return result
        except Exception as e:
            print(f"Erreur lors de la récupération des informations du planning_detail {planning_detail_id}: {e}")
            return None
        finally:
            if conn:
                self.pool.release(conn)  # Relâcher la connexion dans le pool

    async def abrogate_contract(self, planning_detail_id: int):
        """
        Abroge un contrat à partir d'une date de résiliation.
        Supprime les traitements futurs et marque le contrat comme 'Terminé'.
        Prend le pool de connexions en argument.
        """
        date = datetime.date.today()
        conn = None
        try:
            conn = await self.pool.acquire()
            # 1. Récupérer les informations initiales pour obtenir planning_id et contrat_id
            # Passez le pool à get_planning_detail_info
            detail_info = await self.get_planning_detail_info(planning_detail_id)
            print(detail_info)
            if not detail_info:
                print(f"Impossible de trouver les informations pour planning_detail_id {planning_detail_id}.")
                return False

            current_planning_id = detail_info['planning_id']
            current_contrat_id = detail_info['contrat_id']

            print(current_contrat_id, current_planning_id)

            async with conn.cursor() as cursor:
                print('suppress')
                # 2. Supprimer les traitements (PlanningDetails) futurs pour ce planning
                try:
                    delete_query = """
                                   DELETE 
                                   FROM PlanningDetails
                                   WHERE planning_id = %s 
                                     AND date_planification > %s; 
                                   """
                    await cursor.execute(delete_query, (current_planning_id, date))
                    deleted_count = cursor.rowcount
                except Exception as e:
                    print(e)
                print(
                    f"{deleted_count} traitements futurs (PlanningDetails) associés au planning {current_planning_id} ont été supprimés après le {date}.")

                # 3. Mettre à jour le statut du contrat
                update_contract_query = """
                                        UPDATE Contrat
                                        SET statut_contrat = 'Terminé', 
                                            date_fin       = %s, 
                                            duree          = 'Déterminée'
                                        WHERE contrat_id = %s; 
                                        """
                await conn.begin()
                await cursor.execute(update_contract_query, (date, current_contrat_id))
                print('change')

                print(
                    f"Le contrat {current_contrat_id} a été marqué comme 'Terminé' avec date de fin {date} avec succès.")
                return True

        except Exception as e:
            print(f"Erreur lors de l'abrogation du contrat ou de la suppression des traitements: {e}")
            await conn.rollback()
            return False
        finally:
            if conn:
                self.pool.release(conn)

    async def close(self):
        """Ferme le pool de connexions."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()