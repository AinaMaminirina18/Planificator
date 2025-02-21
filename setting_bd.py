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

    async def add_user(self, username, prenom, email, password, type_compte):
        """Ajoute un utilisateur dans la base de données."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO Account (nom, prenom, email, password, type_compte)VALUES (%s, %s, %s, %s, %s)",
                    (username, prenom, email, password, type_compte)
                )
                await conn.commit()

    async def verify_user(self, username, password):
        """Vérifie si un utilisateur existe avec les informations données."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM Account;"
                )
                result = await cursor.fetcall()
                return result

    async def close(self):
        """Ferme le pool de connexions."""
        await self.pool.close()
        await self.pool.wait_closed()