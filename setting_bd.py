import aiomysql

class DatabaseManager:
    """Gestionnaire de la base de données utilisant aiomysql."""
    def __init__(self, loop):
        self.loop = loop
        self.pool = None

    async def connect(self):
        """Crée un pool de connexions à la base de données."""
        self.pool = await aiomysql.create_pool(
            host="localhost",
            port=3306,
            user="root",
            password="root",
            db="Planificator",
            loop=self.loop
        )

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
    
    async def create_planning(self, traitement_id, date_debut, mois_debut, mois_fin, mois_pause, redondance, date_fin):
        """Crée un planning pour un traitement donné."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT INTO Planning (traitement_id,date_debut_planification, mois_debut, mois_fin, mois_pause, redondance, date_fin_planification) VALUES (%s, %s, %s, %s, %s, %s,%s)",
                        (traitement_id, date_debut, mois_debut, mois_fin, mois_pause, redondance, date_fin))
                    await conn.commit()
                    return cur.lastrowid
           
                except Exception as e:
                    print("planning",e)
                    
    async def create_planning_details(self, planning_id, mois ,statut='À venir'):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT INTO PlanningDetails (planning_id, mois, statut) VALUES ( %s, %s, %s)",
                        (planning_id, mois, statut))
                    await conn.commit()
                    return cur.lastrowid
                except Exception as e:
                    print("detail",e)
    
    async def create_facture(self, planning_id, montant, axe,etat = 'Non payé'):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT INTO Facture (planning_detail_id, montant, etat,  axe) VALUES (%s, %s, %s, %s)",
                        (planning_id, montant,etat,  axe))
                    await conn.commit()
                    return cur.lastrowid
                except Exception as e:
                    print("facture",e)
    
    async def create_remarque(self,client, planning_details, facture, contenu):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    cur.execute(
                    "INSERT INTO Remarque (client_id, planning_detail_id, facture_id, contenu) VALUES (%s, %s, %s, %s, %s)",
                    (client, planning_details, facture, contenu))
                    await conn.commit()
                except Exception as e:
                    print("remarque",e)
                
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
                              c.nom = %s AND co.date_contrat = %s AND tt.TypeTraitement = %s; """, (client, date, traitement))
                    resultat = await cursor.fetchone()
                    return resultat
                except Exception as e:
                    print(e)
                    
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
                                  co.duree AS duree_contrat,
                                  co.date_debut AS debut_contrat,
                                  co.date_fin AS fin_contrat,
                                  c.categorie AS categorie,
                                  count(c.client_id)
                           FROM
                              Client c
                           JOIN
                              Contrat co ON c.client_id = co.client_id
                           JOIN
                              Traitement t ON co.contrat_id = t.contrat_id
                           JOIN
                              TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
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