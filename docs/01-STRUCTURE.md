# Structure et Architecture - Planificator

## 📁 Structure du projet

```
Planificator/
├── docs/                          # Documentation (nouveau)
│   ├── 00-INDEX.md
│   ├── 01-STRUCTURE.md
│   ├── 02-PROBLEMES_SOLUTIONS.md
│   └── ...
├── screen/                        # Interfaces Kivy
│   ├── about.kv
│   ├── main.kv
│   ├── client/
│   │   ├── Client.kv
│   │   ├── ajout_info_client.kv
│   │   ├── modification_client.kv
│   │   ├── option_client.kv
│   │   └── save_info_client.kv
│   ├── contrat/
│   │   ├── contrat.kv
│   │   ├── about_treatment.kv
│   │   ├── new-contrat.kv
│   │   └── ...
│   ├── planning/
│   │   ├── planning.kv
│   │   ├── ajout_remarque.kv
│   │   ├── selection_planning.kv
│   │   └── ...
│   └── historique/
│       ├── historique.kv
│       └── histo_remarque.kv
├── scripts/
│   ├── Planificator.sql          # Création BD
│   └── Migration.sql
├── main.py                        # Point d'entrée (3266 lignes)
├── setting_bd.py                  # Gestionnaire BD (1821 lignes)
├── calendrier.py                  # Gestion calendrier
├── email_verification.py
├── excel.py
├── gestion_ecran.py
└── requirements.txt
```

## 🏗️ Architecture générale

### Couche présentation (Kivy + KivyMD)
```
main.py
├── Class: Screen (MDApp)
│   ├── __init__()                  # Initialisation UI + BD
│   ├── build()                     # Construction écrans KV
│   ├── build_screens()             # Chargement dynamique écrans
│   └── Gestion des écrans
│
├── MDDataTable customisée
│   ├── liste_client (4 colonnes)
│   ├── liste_planning (4 colonnes)
│   ├── liste_contrat (4 colonnes)
│   ├── all_treat (3 colonnes)
│   ├── facture (3 colonnes)
│   ├── en_cours (4 colonnes)
│   └── prevision (4 colonnes)
│
└── Gestion événements
    ├── row_pressed_client()        # Clic sur client
    ├── row_pressed_contrat()       # Clic sur contrat
    ├── traitement_par_client()     # Liste traitements
    └── populate_tables()           # Rafraîchissement home
```

### Couche métier (Base de données)
```
setting_bd.py
├── Class: DatabaseManager
│   ├── Connexion pool (aiomysql)
│   │
│   ├── Lectures (SELECT)
│   │   ├── get_all_client()        # Tous clients
│   │   ├── traitement_par_client() # Traitements d'un client
│   │   ├── traitement_en_cours()   # Planning actuel
│   │   ├── get_latest_contract_date_for_client() # Dernier contrat
│   │   └── get_current_client()    # Info client complet
│   │
│   ├── Écritures (INSERT/UPDATE)
│   │   ├── create_remarque()       # Ajouter remarque
│   │   ├── update_etat_planning()  # Marquer effectué
│   │   ├── update_etat_facture()   # Marquer payé
│   │   └── majMontantEtHistorique() # Mise à jour prix
│   │
│   └── Gestion transactionnelle
│       ├── begin/commit/rollback
│       └── Gestion erreurs + retry
```

### Schéma Base de Données

```
Client
├── client_id (PK)
├── nom, prenom
├── email, telephone
├── adresse, axe
├── categorie (Particulier/Entreprise)
└── nif, stat

Contrat
├── contrat_id (PK)
├── client_id (FK)
├── date_contrat, date_debut, date_fin
├── duree, duree_contrat
├── categorie
└── reference_contrat

Traitement
├── traitement_id (PK)
├── contrat_id (FK)
└── id_type_traitement (FK)

TypeTraitement
├── id_type_traitement (PK)
├── categorieTraitement
└── typeTraitement

Planning
├── planning_id (PK)
├── traitement_id (FK)
└── redondance (0-6 = fréquence)

PlanningDetails
├── planning_detail_id (PK)
├── planning_id (FK)
├── date_planification
├── statut (À venir, Effectué, Classé sans suite)
└── axe

Facture
├── facture_id (PK)
├── planning_detail_id (FK)
├── montant, etat (Payé/Non payé)
├── mode (Espèce, Chèque, etc)
└── date_cheque, numero_cheque

Historique_prix
├── historique_id (PK)
├── facture_id (FK)
├── ancien_prix, nouveau_prix
└── date_modification
```

## 🔄 Flux de données principal

### 1. Affichage liste clients
```
User clique "Gestion Clients"
  ↓
switch_to_client()
  ↓
get_all_client() [async]
  ├── SELECT client_id, nom, prenom, email, adresse, MAX(date_contrat)
  ├── LEFT JOIN Contrat
  └── GROUP BY client_id
  ↓
update_client_table_and_switch()
  ├── row_data = [(id, nom, email, adresse, date) ...]
  ├── client_id_map = {idx: id ...}  ← Mapping pour éviter doublons
  └── Affiche tableau liste_client
```

### 2. Sélection d'un client
```
User clique sur client dans tableau
  ↓
row_pressed_client(row)
  ├── index_global = (page-1) * 8 + row_num  ← Pagination correction
  ├── client_id = client_id_map[index_global]
  │
  └── current_client_info_async(client_id)
      ├── get_latest_contract_date_for_client(client_id)
      │   └── SELECT co.date_contrat WHERE client_id = %s
      │
      └── get_current_client(client_id, date)
          └── SELECT * avec JOINs (Client, Contrat, Traitement, etc)
  ↓
maj_ecran() [après 1.0s]
  └── Affiche popup "option_client" avec infos
```

### 3. Mise à jour facture (paiement)
```
User remplit formulaire signalement
  ├── remarque, problème, action
  ├── date_payement
  └── Mode paiement (espèce, chèque, etc)
  ↓
save_remarque()
  ├── create_remarque() → Historique_remarque
  ├── update_etat_planning() → PlanningDetails.statut = 'Effectué'
  └── update_etat_facture() → Facture.etat = 'Payé'
  ↓
populate_tables() [après 0.8s]
  ├── traitement_en_cours(year, month)
  └── traitement_prevision(year, month)
  ↓
home affiche tableau avec couleur VERTE + "Effectué"
```

## 🎯 Points critiques de l'architecture

### 1. Pagination
**Formule**: `index_global = (page - 1) * rows_per_page + row_num`
- Chaque table a 8 lignes par page (MyDatatable)
- Correction appliquée à: row_pressed_client(), row_pressed_contrat()

### 2. Client ID Mapping
**Problème original**: Conflits avec noms dupliqués
**Solution**: Mapper client_index → client_id
```python
self.client_id_map = {idx: i[0] for idx, i in enumerate(client_data)}
```

### 3. Timing asynchrone
**Pattern utilisé**:
```python
# 1. Lancer async
asyncio.run_coroutine_threadsafe(async_func(), self.loop)

# 2. Mettre à jour UI après délai
Clock.schedule_once(lambda dt: sync_func(), delay)
```

### 4. Gestion d'erreur
- Try/except avec rollback en BD
- Affichage dialogs utilisateur
- Logs détaillés (DEBUG, INFO, WARNING, ERROR)

## 📊 Tableaux de l'application

| Tableau | Colonnes | Source | Lieu |
|---------|----------|--------|------|
| liste_client | Client, Email, Adresse, Date contrat | get_all_client() | Gestion Clients |
| liste_planning | Client, Traitement, Fréquence, Options | traitement_par_client() | Contrats → Planning |
| liste_contrat | Client, Type traitement, Fréquence, Date | get_contrat() | Gestion Contrats |
| all_treat | Date traitement, Type, Fréquence | traitement_par_client() | Option Client |
| facture | Date, Montant, État | get_facture() | Détail planning |
| en_cours | Date, Traitement, État, Axe | traitement_en_cours() | Home |
| prevision | Date, Traitement, État, Axe | traitement_prevision() | Home |

---

**Créé**: 23 décembre 2025
