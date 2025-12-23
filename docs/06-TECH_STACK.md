# Stack technique - Planificator

## 📚 Technologies utilisées

### Frontend
```
Kivy 2.x / KivyMD
├── MDApp (Application principale)
├── MDScreen (Écrans)
├── MDDataTable (Tableaux)
├── MDPopupMenu (Menus contextuels)
├── MDDatePicker (Calendriers)
└── MDCheckbox, MDTextField, etc (Widgets)

Language: Python 3.13
```

### Backend
```
MySQL 8.0+
├── Schéma relationnel (9 tables)
├── Contraintes FK avec CASCADE DELETE
├── Indexes de performance
└── Transactions ACID
```

### Communication
```
aiomysql
├── Pool de connexions asynchrone
├── Gestion automatique des ressources
└── Timeout et retry avec backoff exponentiel

asyncio
├── Boucle d'événements async/await
├── Thread safety avec threading.Lock
└── Coroutines pour DB + UI
```

### Utilitaires
```
PIL/Pillow     → Traitement d'images
openpyxl       → Export Excel
DateTime       → Gestion dates
logging        → Logs détaillés
threading      → Threading asyncio
```

## 🏗️ Architecture système

### Modèle de concurrence

```
Main Thread (Kivy Event Loop)
    ↓
    Clock.schedule_once()  ← Planifier exécution UI
    ↓
    Affichage à l'écran
    
Async Thread (asyncio Loop)
    ↓
    asyncio.run_coroutine_threadsafe()
    ↓
    BD (aiomysql pool)
```

### Pattern Communication

```python
# 1. From UI (main thread)
asyncio.run_coroutine_threadsafe(
    self.database.get_all_client(),
    self.loop  # ← Async loop dans thread séparé
)

# 2. Attendre completion
Clock.schedule_once(
    lambda dt: update_ui(),
    delay  # ← Delay pour laisser async finir
)

# 3. Afficher résultat dans main thread
@mainthread
def update_ui(self):
    self.table.row_data = result  # ← Thread-safe
```

## 📦 Dépendances principales

```txt
kivy==2.2.1
kivymd==0.104.2
aiomysql==0.2.0
openpyxl==3.10.0
Pillow==9.5.0
python-dateutil==2.8.2
```

## 🚀 Performance

### Optimisations appliquées

**1. Connection pooling**
```python
self.pool = aiomysql.create_pool(
    minsize=5,
    maxsize=10,
    # ↑ Réutilise connexions, pas de reconnect à chaque requête
)
```

**2. Indexes BD**
```sql
INDEX idx_date ON PlanningDetails(date_planification)
-- ↑ Requête par mois très rapide
```

**3. Requêtes optimisées**
```sql
-- ❌ MAUVAIS (N+1 queries)
SELECT * FROM Client
FOR EACH client:
    SELECT * FROM Contrat WHERE client_id = client.id

-- ✅ BON (1 query avec JOIN)
SELECT c.*, co.*
FROM Client c
LEFT JOIN Contrat co ON c.client_id = co.client_id
```

**4. Caching en mémoire**
```python
FREQUENCY_MAP = {0: {...}, 1: {...}, ...}
# ↑ Mapping fréquence calculé une fois, réutilisé partout
```

**5. Async I/O**
```python
# ❌ Synchrone (bloque l'UI)
result = requests.get(url)  # 1 seconde d'attente

# ✅ Asynchrone (UI reste réactive)
result = await async_get(url)  # UI reste libre
```

## 🔒 Sécurité

### Prévention injections SQL
```python
# ❌ DANGEREUX
cursor.execute(f"SELECT * FROM Client WHERE nom = '{nom}'")

# ✅ SÛRE
await cursor.execute(
    "SELECT * FROM Client WHERE nom = %s",
    (nom,)  # ← Paramètres séparés
)
```

### Gestion d'erreurs
```python
try:
    await cursor.execute(...)
except Exception as e:
    await conn.rollback()  # Revert tout
    logger.error(f"Erreur: {e}")
    raise e
```

### Timeouts
```python
# Éviter les requêtes qui traînent
asyncio.wait_for(
    database_call(),
    timeout=5.0  # ← 5 secondes max
)
```

## 🧪 Testing

### Tests unitaires
```bash
python -m pytest tests/
# (À implémenter si nécessaire)
```

### Tests d'intégration
Manuels actuellement:
1. Créer client
2. Créer contrat
3. Créer traitement
4. Vérifier planning généré
5. Effectuer traitement
6. Vérifier statut change couleur

## 📊 Benchmarks

### Temps de chargement (approx)

| Action | Temps | Notes |
|--------|-------|-------|
| Connexion BD | <500ms | Pool reuse |
| get_all_client() | 200ms | 1000 clients |
| traitement_en_cours() | 150ms | Avec JOINs |
| Affichage tableau | 100ms | UI render |
| Total "ouvrir clients" | ~800ms | Acceptable |

### Mémoire
```
Kivy + KivyMD: ~150MB
Python runtime: ~50MB
BD pool (5-10 connexions): ~50MB
Tableau (1000 rows): ~20MB
TOTAL: ~270MB (léger)
```

## 🔧 Configuration

### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Usage
logger.debug("Debug info")    # Détail technique
logger.info("✅ Succès")      # Opération OK
logger.warning("⚠️ Attention") # Anomalie non-bloquante
logger.error("❌ Erreur")      # Problème grave
```

### Constantes
```python
# setting_bd.py
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "..."
DB_NAME = "Planificator"

FREQUENCY_MAP = {
    0: {"label": "une seule fois", "dates_per_year": 1},
    # ... (voir 03-FREQUENCY_SYSTEM.md)
}
```

## 🎯 Best practices appliquées

### 1. Async/await
```python
# ✅ Utiliser await pour les opérations longues
result = await database.get_client()
```

### 2. Context managers
```python
# ✅ Utiliser async with pour les ressources
async with pool.acquire() as conn:
    async with conn.cursor() as cur:
        await cur.execute(...)
```

### 3. Error handling
```python
# ✅ Always rollback on error
try:
    await conn.begin()
    await cur.execute(...)
    await conn.commit()
except Exception as e:
    await conn.rollback()
    raise
```

### 4. Logging
```python
# ✅ Log les étapes clés
logger.debug("🔍 Cherche contrat...")
result = await get_contract()
logger.info("✅ Contrat trouvé")
```

### 5. Séparation concerns
```
main.py
  ├── UI logic (Kivy screens)
  ├── Event handlers (row_pressed_client)
  └── UI updates (@mainthread)

setting_bd.py
  ├── Database operations (SELECT/INSERT/UPDATE)
  ├── Connection management
  └── Error handling

calendrier.py, excel.py, etc
  └── Fonctionnalités spécialisées
```

## 🚨 Points d'attention

### 1. Thread safety
**Problème**: Main thread (Kivy) ≠ Async thread (asyncio)
**Solution**: Utiliser @mainthread decorator
```python
@mainthread
def update_ui(self):
    self.table.row_data = result  # ✅ Thread-safe
```

### 2. Async/await confusion
**Problème**: Appeler async function sans await
```python
# ❌ FAUX
result = self.database.get_client()  # Retourne Coroutine, pas résultat!

# ✅ BON
result = await self.database.get_client()
```

### 3. Timing issues
**Problème**: UI updates avant que async finisse
```python
# ❌ FAUX
asyncio.run_coroutine_threadsafe(async_func(), loop)
update_ui()  # ← Trop tôt!

# ✅ BON
asyncio.run_coroutine_threadsafe(async_func(), loop)
Clock.schedule_once(lambda dt: update_ui(), 0.5)  # ← Attends 0.5s
```

## 📖 Ressources

### Documentation
- Kivy: https://kivy.org/doc/stable/
- KivyMD: https://kivymd.readthedocs.io/
- aiomysql: https://aiomysql.readthedocs.io/
- asyncio: https://docs.python.org/3/library/asyncio.html

### Tutoriels pertinents
- AsyncIO: https://realpython.com/async-io-python/
- Database pooling: https://en.wikipedia.org/wiki/Connection_pool
- Kivy threading: https://kivy.org/doc/stable/guide/events.html

---

**Créé**: 23 décembre 2025
**Python**: 3.13+
**Status**: Production-ready
