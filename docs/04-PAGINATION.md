# Système de Pagination - Planificator

## 📋 Vue d'ensemble

La **pagination** divise les listes longues en pages de 8 lignes chacune. Chaque tableau avec MDDataTable utilise ce système.

## 🔢 Formule clé

```python
index_global = (page - 1) * rows_per_page + row_num

Exemple:
  page = 1, row = 0 → index_global = (1-1)*8 + 0 = 0    ✅ Client 1
  page = 1, row = 5 → index_global = (1-1)*8 + 5 = 5    ✅ Client 6
  page = 2, row = 0 → index_global = (2-1)*8 + 0 = 8    ✅ Client 9
  page = 2, row = 5 → index_global = (2-1)*8 + 5 = 13   ✅ Client 14
  page = 3, row = 2 → index_global = (3-1)*8 + 2 = 18   ✅ Client 19
```

## ❌ Bug original (pagination cassée)

### Symptômes
```
Page 1: Clic client 5 → Affiche client 5 ✅
Page 2: Clic client 5 → Affiche client 13 ❌ (devrait être client 13 mais mauvaise logique)
```

### Code cassé
```python
# ❌ AVANT (FAUX)
def row_pressed_client(self, table, row):
    index = int(row.index / len(table.column_data))  # Seulement le num local
    row_value = table.row_data[index]  # ❌ Ne tient pas compte de la page!
```

Le problème: `row.index` est l'index dans la PAGE (0-7), pas dans la liste complète!

### Mathématiques du bug
```
Supposons 100 clients (pages 1-13):

PAGE 1 (clients 1-8):
  row.index = 0 → veut client 1 → index = 0 ✅ Chance!

PAGE 2 (clients 9-16):
  row.index = 0 → veut client 9
  Mais index = 0 → affiche client 1 ❌ BUG!
  
  row.index = 4 → veut client 13
  Mais index = 4 → affiche client 5 ❌ BUG!
```

## ✅ Solution: Formule correcte

```python
# ✅ APRÈS (CORRECT)
def row_pressed_client(self, table, row):
    row_num = int(row.index / len(table.column_data))
    index_global = (self.main_page - 1) * 8 + row_num  # ← Formule magique!
    row_value = table.row_data[index_global]
```

### Vérification
```
PAGE 2, row.index = 0 (veut client 9):
  row_num = 0
  index_global = (2-1) * 8 + 0 = 8  ← Client 9 (index 8 dans la liste) ✅

PAGE 2, row.index = 4 (veut client 13):
  row_num = 4
  index_global = (2-1) * 8 + 4 = 12  ← Client 13 (index 12 dans la liste) ✅

PAGE 3, row.index = 0 (veut client 17):
  row_num = 0
  index_global = (3-1) * 8 + 0 = 16  ← Client 17 (index 16 dans la liste) ✅
```

## 📊 Tableaux avec pagination

### Liste complète

| Tableau | Rows/page | Var. page | Location | Fichier |
|---------|-----------|-----------|----------|---------|
| liste_client | 8 | self.main_page | Gestion Clients | main.py |
| liste_contrat | 8 | self.contrat_page | Gestion Contrats | main.py |
| liste_planning | 8 | self.planning_page | Planning | main.py |
| all_treat | 8 | (auto) | Détail Client | main.py |
| facture | 8 | (auto) | Détail Planning | main.py |
| en_cours | 8 | (auto) | Home | main.py |
| prevision | 8 | (auto) | Home | main.py |

### Tableaux SANS pagination
- historique (8 rows mais unique)
- histo_remarque (8 rows mais unique)

## 🔧 Implémentation code

### Initialisation

```python
class Screen(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.main_page = 1          # Page actuelle liste_client
        self.contrat_page = 1       # Page actuelle liste_contrat
        self.planning_page = 1      # Page actuelle liste_planning
        # ... autres variables page
```

### Gestion du changement de page

```python
def on_press_page(direction, instance=None):
    """Gère clic sur bouton prev/next"""
    
    max_page = (len(row_data) - 1) // 8 + 1  # Calcul pages
    
    if direction == 'moins' and self.main_page > 1:
        self.main_page -= 1  # Page précédente
    elif direction == 'plus' and self.main_page < max_page:
        self.main_page += 1  # Page suivante
    
    # Mettre à jour tableau
    refresh_tableau()
```

### Application lors du clic ligne

```python
def row_pressed_client(self, table, row):
    """Clic sur une ligne du tableau"""
    
    # ✅ Formule pagination
    row_num = int(row.index / len(table.column_data))
    index_global = (self.main_page - 1) * 8 + row_num
    
    # Récupérer l'item correct
    if 0 <= index_global < len(table.row_data):
        row_value = table.row_data[index_global]
        client_id = self.client_id_map[index_global]  # ← Client ID unique
        
        # Traiter...
        load_client_details(client_id)
```

## 🎨 UI - Boutons pagination

### KV structure
```yaml
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        
        # Tableau
        MDDataTable:
            id: liste_client
            column_data: [("Client", ...), ...]
            row_data: []
            on_row_press: app.row_pressed_client
        
        # Pagination
        BoxLayout:
            size_hint_y: 0.1
            
            MDIconButton:
                icon: 'chevron-left'
                on_release: app.on_press_page('moins')  # Page -1
            
            MDLabel:
                text: "Page X/Y"
                halign: 'center'
            
            MDIconButton:
                icon: 'chevron-right'
                on_release: app.on_press_page('plus')   # Page +1
```

## 📐 Calculs utiles

### Nombre total de pages
```python
total_pages = (len(items) - 1) // 8 + 1

Exemples:
  8 items → (8-1)//8 + 1 = 1 page
  9 items → (9-1)//8 + 1 = 2 pages
  16 items → (16-1)//8 + 1 = 2 pages
  17 items → (17-1)//8 + 1 = 3 pages
```

### Première item d'une page
```python
first_item = (page - 1) * 8

Page 1: (1-1)*8 = 0   → Item 1 (index 0)
Page 2: (2-1)*8 = 8   → Item 9 (index 8)
Page 3: (3-1)*8 = 16  → Item 17 (index 16)
```

### Dernière item d'une page
```python
last_item = page * 8 - 1

Page 1: 1*8-1 = 7   → Item 8 (index 7)
Page 2: 2*8-1 = 15  → Item 16 (index 15)
Page 3: 3*8-1 = 23  → Item 24 (index 23)
```

## 🚨 Pièges courants

### Piège 1: Oublier la formule
```python
# ❌ FAUX (ancien code)
index = row.index  # Seulement numéro dans page

# ✅ BON
index = (page - 1) * 8 + row.index // columns
```

### Piège 2: Confusion rows et colonnes
```python
# row.index augmente à chaque COLONNE, pas chaque LIGNE
# Exemple avec 4 colonnes:
#   Ligne 1: row.index = 0, 1, 2, 3
#   Ligne 2: row.index = 4, 5, 6, 7
#   Ligne 3: row.index = 8, 9, 10, 11

# Solution: diviser par nombre colonnes
row_num = int(row.index / len(table.column_data))
```

### Piège 3: Pas de vérification bounds
```python
# ❌ CRASH si index_global >= len(row_data)
row_value = table.row_data[index_global]

# ✅ SÛRE
if 0 <= index_global < len(table.row_data):
    row_value = table.row_data[index_global]
```

## 📝 Checklist implémentation pagination

Pour chaque nouveau tableau:
- [ ] Définir rows_per_page = 8
- [ ] Créer variable page (e.g., self.planning_page)
- [ ] Ajouter boutons prev/next
- [ ] Implémenter on_press_page()
- [ ] Dans row_clicked: calculer index_global
- [ ] Vérifier bounds (0 <= index < len)
- [ ] Tester page 1 (doit marcher)
- [ ] Tester page 2+ (doit marcher aussi)

## 🧪 Cas de test

### Test 1: 8 clients (1 page)
```
Clic client 1 → OK
Clic client 8 → OK
Pas de page 2
```

### Test 2: 16 clients (2 pages)
```
Page 1:
  Clic client 1 → OK
  Clic client 8 → OK
  
Page 2:
  Clic client 1 (affichage) → Charge client 9 ✅
  Clic client 8 (affichage) → Charge client 16 ✅
```

### Test 3: 25 clients (4 pages)
```
Page 1: clients 1-8 ✅
Page 2: clients 9-16 ✅
Page 3: clients 17-24 ✅
Page 4: client 25 ✅
```

---

**Créé**: 23 décembre 2025
**Correction appliquée**: Commit #5 (pagination fix)
