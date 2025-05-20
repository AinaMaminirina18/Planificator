import aiomysql

class DatabaseManager:
    """Gestionnaire de la base de données utilisant aiomysql."""
    def __init__(self, loop):
        self.loop = loop
        self.pool = None

    async def connect(self):
        try:
            """Crée un pool de connexions à la base de données."""
            self.pool = await aiomysql.create_pool(
                host="localhost",
                port=3306,
                user="root",
                password="root",
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
    
    async def create_contrat(self, client_id, date_contrat, date_debut, date_fin, duree, duree_contrat, categorie):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT INTO Contrat (client_id, date_contrat, date_debut, date_fin, duree_contrat, duree, categorie) VALUES (%s, %s, %s,%s, %s, %s, %s)",
                        (client_id, date_contrat, date_debut, date_fin, duree, duree_contrat, categorie))
                    await conn.commit()
                    return cur.lastrowid
                except Exception as e:
                    print(e)
            
    async def create_client(self, nom, prenom, email, telephone, adresse, date_ajout, categorie, axe):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO Client (nom, prenom, email, telephone, adresse, date_ajout, categorie, axe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (nom, prenom, email, telephone, adresse, date_ajout, categorie, axe))
                await conn.commit()
                return cur.lastrowid
            
    async def get_all_client(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT DISTINCT nom, email, adresse, date_ajout FROM Client ORDER BY nom ASC")
                return await cur.fetchall()
                
    async def typetraitement(self,categorie, type):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("INSERT INTO TypeTraitement (categorieTraitement, typeTraitement) VALUES (%s,%s)",
                                            (categorie,type))
                    await conn.commit()
                    return cursor.lastrowid
                except Exception as e:
                    print(e)
    
    async def creation_traitement(self, contrat_id, id_type_traitement):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute("INSERT INTO Traitement (contrat_id, id_type_traitement) VALUES (%s, %s)",
                                      (contrat_id, id_type_traitement))
                    await conn.commit()
                    return cur.lastrowid
                except Exception as e:
                    print(e)
    
    async def create_planning(self, traitement_id, date_debut, mois_debut, mois_fin, redondance, date_fin):
        """Crée un planning pour un traitement donné."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """INSERT INTO Planning (traitement_id,date_debut_planification, mois_debut, mois_fin, redondance, date_fin_planification) 
                            VALUES (%s, %s, %s, %s, %s,%s)""",
                        (traitement_id, date_debut, mois_debut, mois_fin, redondance, date_fin))
                    await conn.commit()
                    return cur.lastrowid
           
                except Exception as e:
                    print("planning",e)

    async def traitement_en_cours(self, year, month):
        async with self.pool.acquire() as conn:
            traitements = []
            async with conn.cursor() as curseur:
                try:
                    await curseur.execute(
                        """SELECT c.nom AS nom_client,
                                  tt.typeTraitement AS type_traitement,
                                  pdl.statut,
                                  pdl.date_planification,
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
                               WHERE
                                  MONTH(pdl.date_planification) = %s
                               AND
                                  YEAR(pdl.date_planification) = %s
                               ORDER BY
                                  pdl.date_planification; """,
                        (month,year)
                    )
                    rows = await curseur.fetchall()
                    for nom, traitement, statut, date_str, idplanning in rows:
                        traitements.append({
                            "traitement": f'{traitement.partition('(')[0].strip()} pour {nom}',
                            "date": date_str,
                            'etat': statut
                        })
                    return traitements
                except Exception as e:
                    print('en cours', e)

    async def traitement_prevision(self, year, month):
        async with self.pool.acquire() as conn:
            traitements = []
            async with conn.cursor() as curseur:
                try:
                    await curseur.execute(
                        """SELECT c.nom AS nom_client,
                                  tt.typeTraitement AS type_traitement,
                                  pdl.statut,
                                  MIN(pdl.date_planification),
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
                    for nom, traitement, statut, date_str, idplanning in rows:
                        traitements.append({
                            "traitement": f'{traitement.partition('(')[0].strip()} pour {nom}',
                            "date": date_str,
                            'etat': statut
                        })
                    return traitements
                except Exception as e:
                    print('Prevision', e)

    async def create_planning_details(self, planning_id, date,statut='À venir'):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT INTO PlanningDetails (planning_id, date_planification, statut) VALUES ( %s, %s, %s)",
                        (planning_id, date, statut))
                    await conn.commit()
                    return cur.lastrowid
                except Exception as e:
                    print("detail",e)
    
    async def get_all_planning(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        """SELECT c.nom AS nom_client,
                                  tt.typeTraitement AS type_traitement,
                                  co.duree AS duree_contrat,
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
    
    async def get_info_planning(self, planning_id, date):
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
                                              p.planning_id = %s AND pdl.date_planification = %s""", (planning_id,date))
                    resulta = await cursor.fetchone()
                    return resulta
                except Exception as e:
                    print('get_info', e)

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

                    await cur.execute(requete, (interval, planning_id, planning_detail_id))
                    await conn.commit()

                except Exception as e:
                    print('Changement de date', e)

    async def modifier_date(self, planning_detail_id, new_date):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute('''UPDATE PlanningDetails
                               SET
                                  date_planification = %s
                               WHERE
                                  planning_detail_id = %s''', (new_date, planning_detail_id))
                await conn.commit()

    async def create_facture(self, planning_id, montant, date, axe, etat = 'Non payé'):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT INTO Facture (planning_detail_id, montant,date_traitement, etat,  axe) VALUES (%s, %s, %s,%s, %s)",
                        (planning_id, montant, date, etat, axe))
                    await conn.commit()
                    return cur.lastrowid
                except Exception as e:
                    print("facture",e)
    
    async def create_remarque(self,client, planning_details, facture, contenu):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                    "INSERT INTO Remarque (client_id, planning_detail_id, facture_id, contenu) VALUES (%s, %s, %s, %s)",
                    (client, planning_details, facture, contenu))
                    await conn.commit()
                except Exception as e:
                    print("remarque",e)

    async def get_historique_remarque(self, planning_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """ SELECT  pdl.date_planification,
                                    r.contenu,
                                    co.duree,
                                    tt.typeTraitement
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
                                    p.planning_id = %s """, (planning_id,)
                    )
                    return await cur.fetchall()

                except Exception as e:
                    print('histo remarque',e)

    async def update_etat_facture(self, facture):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                    "UPDATE Facture SET etat = %s WHERE facture_id = %s",('Payé', facture))
                    await conn.commit()
                except Exception as e:
                    print("update facture",e)

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
                                                count(r.remarque_id)
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
                                  c.telephone
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           WHERE
                              c.nom = %s AND co.date_contrat = %s; """, (client, date))
                    resultat = await cursor.fetchone()
                    return resultat
                except Exception as e:
                    print(e)
                    
    async def get_client(self):
        async with self.pool.acquire() as conn:
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
                                  count(t.traitement_id)
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           GROUP BY
                              c.nom
                           ORDER BY
                              c.nom ASC;"""
                    )
                    result = await cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)
                    
    async def traitement_par_client(self, nom):
        async with self.pool.acquire() as conn :
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(
                        """SELECT c.nom AS nom_client,
                                  co.date_contrat,
                                  tt.typeTraitement AS type_traitement,
                                  co.duree AS duree_contrat,
                                  co.date_debut AS debut_contrat,
                                  co.date_fin AS fin_contrat,
                                  c.categorie AS categorie
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
                           WHERE
                              c.nom = %s;"""
                    , (nom,))
                    result = await cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)

    async def update_client(self, client_id, nom, prenom, email, telephone, adresse, categorie, axe):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE Client SET nom = %s, prenom = %s, email = %s, telephone = %s, adresse = %s, categorie = %s, axe = %s WHERE client_id = %s",
                    (nom, prenom, email, telephone, adresse, categorie, axe, client_id))
                await conn.commit()
                
    async def close(self):
        """Ferme le pool de connexions."""
        self.pool.close()
        await self.pool.wait_closed()