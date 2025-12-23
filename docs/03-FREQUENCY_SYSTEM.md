# Système de Fréquence et Redondance - Planificator

## 📌 Vue d'ensemble

La **fréquence** définit comment souvent un traitement doit être effectué. Elle est codée en BD sous le nom **redondance** (0-6).

## 🗂️ Mapping Fréquence

### Table de référence
```python
FREQUENCY_MAP = {
    0: {"label": "une seule fois", "dates_per_year": 1},
    1: {"label": "1 mois",         "dates_per_year": 12},
    2: {"label": "2 mois",         "dates_per_year": 6},
    3: {"label": "3 mois",         "dates_per_year": 4},
    4: {"label": "4 mois",         "dates_per_year": 3},
    5: {"label": "6 mois",         "dates_per_year": 2},
    6: {"label": "12 mois",        "dates_per_year": 1},
}
```

### Exemples de calcul
```
Redondance 0 (une seule fois)
  → 1 intervention total
  → Planifiée une fois

Redondance 1 (1 mois)
  → 12 interventions/an
  → Planifiée: 1/1, 1/2, 1/3, ..., 1/12

Redondance 2 (2 mois)
  → 6 interventions/an
  → Planifiée: 1/1, 1/3, 1/5, 1/7, 1/9, 1/11
  → Distribution: tous les 2 mois

Redondance 3 (3 mois)
  → 4 interventions/an
  → Planifiée: 1/1, 1/4, 1/7, 1/10

Redondance 6 (12 mois)
  → 1 intervention/an
  → Planifiée: 1/1 seulement
```

## 🔧 Implémentation technique

### Structure Planning
```sql
-- Table Planning
CREATE TABLE Planning (
    planning_id INT PRIMARY KEY,
    traitement_id INT NOT NULL,
    redondance INT NOT NULL,  -- 0-6 (défini ci-dessus)
    FOREIGN KEY (traitement_id) REFERENCES Traitement(traitement_id)
);

-- Table PlanningDetails (les dates réelles)
CREATE TABLE PlanningDetails (
    planning_detail_id INT PRIMARY KEY,
    planning_id INT NOT NULL,
    date_planification DATE,
    statut ENUM('À venir', 'Effectué', 'Classé sans suite'),
    FOREIGN KEY (planning_id) REFERENCES Planning(planning_id)
);
```

### Fonction de génération des dates

**Location**: `setting_bd.py`

```python
async def planning_per_year(self, year, redondance):
    """
    Génère les dates de planification pour une année donnée
    selon la redondance définie.
    
    Args:
        year: Année à planifier (e.g., 2025)
        redondance: 0-6 (fréquence du traitement)
    
    Returns:
        List[datetime]: Les dates planifiées
    """
    dates_per_year = FREQUENCY_MAP.get(redondance, {}).get("dates_per_year", 1)
    
    if dates_per_year == 1:
        # Une seule date: 1er janvier
        return [datetime(year, 1, 1)]
    
    # Distribution uniforme sur l'année
    dates = []
    days_between = 365 // dates_per_year
    
    for i in range(dates_per_year):
        day_of_year = i * days_between + 1
        date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        
        # Ajuster si on dépasse l'année
        if date.year == year:
            dates.append(date)
    
    return dates
```

### Distribution uniforme (exemple Redondance 2)

```
Année 2025: 365 jours
Fréquence: 2 mois = 6 dates/an
Intervalle: 365 / 6 = ~61 jours

Dates générées:
  1. 01/01/2025 (jour 1)
  2. 02/03/2025 (jour 1 + 61)
  3. 03/05/2025 (jour 1 + 122)
  4. 04/06/2025 (jour 1 + 183)
  5. 05/09/2025 (jour 1 + 244)
  6. 06/10/2025 (jour 1 + 305)
```

## 🎨 Affichage dans l'UI

### Tableaux concernés

| Tableau | Affichage |
|---------|-----------|
| liste_planning | Fréquence label (e.g., "1 mois") |
| all_treat | Fréquence label + couleur |
| planning | Fréquence label + nombre de mois |
| en_cours (home) | Statut couleur (effectué=vert) |

### Code d'affichage (main.py)

```python
def display_frequency(redondance):
    """Affiche le label français de la fréquence"""
    label = FREQUENCY_MAP.get(redondance, {}).get("label", "Inconnue")
    
    # Exemple: redondance=1 → "1 mois"
    # Exemple: redondance=3 → "3 mois"
    return label
```

### Affichage avec couleurs (home)

```python
def populate_tables(self):
    """Charge et affiche tableaux home avec couleurs"""
    
    data_current = []
    for i in data_en_cours:
        # Mapping statut → couleur
        etat = i['etat']  # 'À venir', 'Effectué', 'Classé sans suite'
        color = self.color_map.get(etat, "000000")
        
        data_current.append((
            f"[color={color}]{self.reverse_date(i['date'])}[/color]",
            f"[color={color}]{i['traitement']}[/color]",
            f"[color={color}]{i['etat']}[/color]",     # Affiche le statut
            f"[color={color}]{i['axe']}[/color]"
        ))
    
    # Color mapping
    # "À venir"          → 'ff0000' (rouge)
    # "Effectué"         → '008000' (vert) ← Quand facture payée
    # "Classé sans suite" → 'FFA500' (orange)
```

## 🔄 Cycle de vie d'un traitement

```
1. CRÉATION (statut: "À venir")
   ├── Contrat créé avec redondance = X
   └── planning_per_year() génère dates pour année courante
        └── Crée PlanningDetails pour chaque date
            └── Crée Facture pour chaque date

2. AFFICHAGE (Home: rouge)
   ├── traitement_en_cours() récupère en_cours du mois
   └── Affiche avec couleur rouge "À venir"

3. EFFECTUATION (statut: "Effectué", couleur: vert)
   ├── User clique → ajout_remarque (formulaire signalement)
   ├── Remplit: remarque, problème, action
   └── Coche "Payé" + mode paiement (espèce, chèque, etc)
        ├── create_remarque()
        ├── update_etat_planning(planning_detail_id) → 'Effectué'
        ├── update_etat_facture(facture_id) → 'Payé'
        └── populate_tables() [après 0.8s]
             └── Home affiche maintenant en VERT "Effectué"

4. FUTURE ANNÉE
   ├── New year trigger / cron
   └── planning_per_year(new_year, redondance) pour chaque traitement
        └── Génère les dates pour la nouvelle année
```

## 💾 Persistance en BD

### Tables impliquées

```
Contrat (redondance stockée ici)
├── client_id
├── date_contrat
├── duree (ex: "12 mois")
└── redondance ← Clé pour planning_per_year()
    │
    ├→ Planning
    │  └── traitement_id
    │      └── planning_id
    │          │
    │          └→ PlanningDetails (les dates)
    │             ├── date_planification
    │             ├── statut ('À venir' → 'Effectué')
    │             └── planning_detail_id
    │                 │
    │                 └→ Facture
    │                    ├── montant
    │                    ├── etat ('Non payé' → 'Payé')
    │                    └── facture_id
    │
    └→ Historique_prix (si prix modifié)
       ├── ancien_prix
       ├── nouveau_prix
       └── date_modification
```

## 🚀 Optimisations appliquées

### 1. Distribution uniforme
Au lieu de plages fixes (1er jour du mois), on distribue uniformément:
```python
day_of_year = i * (365 // dates_per_year) + 1
```
✅ Plus naturel, moins de surcharge certains mois

### 2. Cache du mapping
```python
FREQUENCY_MAP = {...}  # Défini une fois, réutilisé partout
```
✅ Une source de vérité
✅ Pas de duplication

### 3. Validation redondance
```python
dates_per_year = FREQUENCY_MAP.get(redondance, {}).get("dates_per_year", 1)
# Si redondance invalide → default à 1 date/an
```
✅ Pas de crash si redondance inattendue

## 📝 Notes pour la maintenance

### Ajouter une nouvelle fréquence
1. Ajouter entrée à FREQUENCY_MAP:
```python
7: {"label": "8 jours", "dates_per_year": 45},
```

2. Les calculs vont marcher automatiquement
3. Le label s'affichera dans tous les tableaux

### Déboguer fréquence incohérente

**Symptôme**: Affiche "1 mois" mais génère 6 dates
```python
# Debug:
# 1. Vérifier FREQUENCY_MAP[redondance]
# 2. Vérifier planning_per_year() retourne bon nombre
# 3. Vérifier UI affiche bon label
```

---

**Créé**: 23 décembre 2025
