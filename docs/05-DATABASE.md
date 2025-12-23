# Base de Données - Planificator

## 📊 Vue d'ensemble

La BD MySQL 8.0+ stocke tous les clients, contrats, traitements, plannings et factures de l'application.

## 🗃️ Schéma complet

### Table Client
```sql
CREATE TABLE Client (
    client_id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telephone VARCHAR(15),
    adresse VARCHAR(255),
    axe VARCHAR(100),              -- "Santé", "Hygiène", etc
    categorie ENUM('Particulier', 'Entreprise'),
    nif VARCHAR(20),
    stat VARCHAR(20),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Points clés**:
- `client_id` est la clé primaire (unique)
- `CONCAT(nom, ' ', prenom)` = nom complet
- `axe` = domaine d'activité du client

### Table Contrat
```sql
CREATE TABLE Contrat (
    contrat_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    reference_contrat VARCHAR(50) UNIQUE,
    date_contrat DATE NOT NULL,
    date_debut DATE,
    date_fin DATE,
    duree VARCHAR(50),             -- "12 mois", "Indéterminée", etc
    duree_contrat VARCHAR(50),     -- Durée réelle
    categorie VARCHAR(100),        -- Type de contrat
    statut_contrat ENUM('Actif', 'Terminé') DEFAULT 'Actif',
    
    FOREIGN KEY (client_id) REFERENCES Client(client_id)
        ON DELETE CASCADE
);
```

**Points clés**:
- `date_contrat` = date signage du contrat
- `duree` = durée affichée ("12 mois" ou "Indéterminée")
- `duree_contrat` = durée réelle (en jours/mois)
- Plusieurs contrats par client possible
- Cascade delete: supprimer client → supprime contrats

### Table TypeTraitement
```sql
CREATE TABLE TypeTraitement (
    id_type_traitement INT PRIMARY KEY AUTO_INCREMENT,
    categorieTraitement VARCHAR(100),   -- "Dératisation", "Désinsectisation"
    typeTraitement VARCHAR(255)         -- "Dératisation (Appâts)" 
);
```

**Points clés**:
- Référence les types de traitement disponibles
- Exemple: "Dératisation pour Particulier (Appâts)"

### Table Traitement
```sql
CREATE TABLE Traitement (
    traitement_id INT PRIMARY KEY AUTO_INCREMENT,
    contrat_id INT NOT NULL,
    id_type_traitement INT NOT NULL,
    
    FOREIGN KEY (contrat_id) REFERENCES Contrat(contrat_id)
        ON DELETE CASCADE,
    FOREIGN KEY (id_type_traitement) REFERENCES TypeTraitement(id_type_traitement)
);
```

**Points clés**:
- Lie un contrat à un type de traitement
- Un contrat peut avoir plusieurs traitements
- Cascade delete

### Table Planning
```sql
CREATE TABLE Planning (
    planning_id INT PRIMARY KEY AUTO_INCREMENT,
    traitement_id INT NOT NULL,
    redondance INT DEFAULT 0,          -- 0-6 (fréquence)
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (traitement_id) REFERENCES Traitement(traitement_id)
        ON DELETE CASCADE
);
```

**Points clés**:
- `redondance` = fréquence (0=une fois, 1=mensuel, 2=bimensuel, etc)
- Un planning = un traitement avec sa fréquence
- Peut avoir plusieurs PlanningDetails (les occurrences)

### Table PlanningDetails
```sql
CREATE TABLE PlanningDetails (
    planning_detail_id INT PRIMARY KEY AUTO_INCREMENT,
    planning_id INT NOT NULL,
    date_planification DATE NOT NULL,
    statut ENUM('À venir', 'Effectué', 'Classé sans suite') 
        DEFAULT 'À venir',
    axe VARCHAR(100),
    
    FOREIGN KEY (planning_id) REFERENCES Planning(planning_id)
        ON DELETE CASCADE,
    
    INDEX idx_statut (statut),
    INDEX idx_date (date_planification)
);
```

**Points clés**:
- Chaque ligne = une occurrence du traitement planifié
- `date_planification` = la date de l'intervention
- `statut`:
  - 'À venir' = pas encore effectué (affiché en rouge)
  - 'Effectué' = traitement fait et facture payée (vert)
  - 'Classé sans suite' = intervention annulée (orange)

### Table Facture
```sql
CREATE TABLE Facture (
    facture_id INT PRIMARY KEY AUTO_INCREMENT,
    planning_detail_id INT NOT NULL,
    reference_facture VARCHAR(50),
    montant DECIMAL(10, 2),
    etat ENUM('Payé', 'Non payé') DEFAULT 'Non payé',
    mode VARCHAR(50),                  -- "Espèce", "Chèque", "Virement"
    etablissement_payeur VARCHAR(100), -- Pour chèques
    date_cheque DATE,
    numero_cheque VARCHAR(50),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (planning_detail_id) REFERENCES PlanningDetails(planning_detail_id)
        ON DELETE CASCADE
);
```

**Points clés**:
- Une facture par planning_detail
- `etat` = 'Payé' quand user effectue le signalement avec paiement
- `mode` = moyen de paiement
- Cascade delete (si planning_detail supprimé → facture supprimée)

### Table Historique_remarque
```sql
CREATE TABLE Historique_remarque (
    historique_id INT PRIMARY KEY AUTO_INCREMENT,
    planning_detail_id INT NOT NULL,
    traitement_id INT NOT NULL,
    facture_id INT NOT NULL,
    remarque TEXT,
    probleme TEXT,
    action TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (planning_detail_id) REFERENCES PlanningDetails(planning_detail_id),
    FOREIGN KEY (traitement_id) REFERENCES Traitement(traitement_id),
    FOREIGN KEY (facture_id) REFERENCES Facture(facture_id)
);
```

**Points clés**:
- Enregistre observations du signalement
- Traçabilité complète de ce qui s'est passé
- Lié à la planification, traitement et facture

### Table Historique_prix
```sql
CREATE TABLE Historique_prix (
    historique_id INT PRIMARY KEY AUTO_INCREMENT,
    facture_id INT NOT NULL,
    ancien_prix DECIMAL(10, 2),
    nouveau_prix DECIMAL(10, 2),
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motif VARCHAR(255),
    
    FOREIGN KEY (facture_id) REFERENCES Facture(facture_id)
);
```

**Points clés**:
- Traçabilité des changements de prix
- Enregistre ancien et nouveau prix
- Date du changement
- Permet d'auditer les modifications tarifaires

## 🔑 Relations clés

```
Client (1) ──┬──→ (N) Contrat (1) ──→ (N) Traitement
             │                              ↓
             │                         (1) Planning (1) ──→ (N) PlanningDetails
             │                                              ↓
             └──────────────────────────────────────→ (1) Facture

PlanningDetails:
  ├── Historique_remarque (observations signalement)
  └── Facture (montant et état paiement)
        └── Historique_prix (changements de prix)
```

## 🔍 Requêtes critiques

### 1. Récupérer tous les clients avec leur dernier contrat

```sql
SELECT 
    c.client_id,
    CONCAT(c.nom, ' ', c.prenom) AS nom_complet,
    c.email,
    c.adresse,
    MAX(co.date_contrat) AS derniere_date_contrat
FROM Client c
LEFT JOIN Contrat co ON c.client_id = co.client_id
GROUP BY c.client_id, c.nom, c.prenom, c.email, c.adresse
ORDER BY c.nom ASC;
```

**Usage**: Affichage liste_client dans Gestion Clients

### 2. Récupérer infos complètes d'un client pour un contrat donné

```sql
SELECT 
    c.client_id,
    c.nom,
    c.prenom,
    c.categorie,
    co.date_contrat,
    tt.typeTraitement,
    co.duree,
    co.date_debut,
    co.date_fin,
    c.email,
    c.adresse,
    c.axe,
    c.telephone,
    p.planning_id,
    f.facture_id,
    c.nif,
    c.stat
FROM Client c
JOIN Contrat co ON c.client_id = co.client_id
JOIN Traitement t ON co.contrat_id = t.contrat_id
JOIN TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
JOIN Planning p ON t.traitement_id = p.traitement_id
JOIN PlanningDetails pld ON p.planning_id = pld.planning_id
JOIN Facture f ON pld.planning_detail_id = f.planning_detail_id
WHERE c.client_id = ? AND co.date_contrat = ?;
```

**Usage**: Affichage popup option_client

### 3. Traitements du mois courant (en cours)

```sql
SELECT 
    c.nom AS nom_client,
    tt.typeTraitement,
    pdl.statut,
    pdl.date_planification,
    p.planning_id,
    c.axe
FROM Client c
JOIN Contrat co ON c.client_id = co.client_id
JOIN Traitement t ON co.contrat_id = t.contrat_id
JOIN TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
JOIN Planning p ON t.traitement_id = p.traitement_id
JOIN PlanningDetails pdl ON p.planning_id = pdl.planning_id
WHERE MONTH(pdl.date_planification) = MONTH(NOW())
  AND YEAR(pdl.date_planification) = YEAR(NOW())
  AND pdl.statut != 'Classé sans suite'
ORDER BY pdl.date_planification;
```

**Usage**: Affichage home, tableau en_cours (avec couleurs)

### 4. Dernière date de contrat d'un client

```sql
SELECT co.date_contrat
FROM Contrat co
WHERE co.client_id = ?
ORDER BY co.date_contrat DESC
LIMIT 1;
```

**Usage**: Quand user clique sur client, récupérer le contrat actif

### 5. Tous les traitements d'un client

```sql
SELECT 
    c.nom,
    c.prenom,
    tt.typeTraitement,
    pdl.date_planification,
    p.redondance,
    pdl.statut
FROM Client c
JOIN Contrat co ON c.client_id = co.client_id
JOIN Traitement t ON co.contrat_id = t.contrat_id
JOIN TypeTraitement tt ON t.id_type_traitement = tt.id_type_traitement
JOIN Planning p ON t.traitement_id = p.traitement_id
JOIN PlanningDetails pdl ON p.planning_id = pdl.planning_id
WHERE c.client_id = ? OR CONCAT(c.nom, ' ', c.prenom) = ?;
```

**Usage**: Affichage tableau all_treat (tous les traitements d'un client)

## 🔄 Transactions critiques

### Effectuer un traitement (signalement)

```python
async def save_remarque(planning_detail_id, facture_id, paye):
    await conn.begin()
    try:
        # 1. Créer remarque
        INSERT INTO Historique_remarque (...)
        
        # 2. Marquer planning comme effectué
        UPDATE PlanningDetails 
        SET statut = 'Effectué' 
        WHERE planning_detail_id = ?
        
        # 3. Si payé, marquer facture
        if paye:
            UPDATE Facture
            SET etat = 'Payé', mode = ?, ...
            WHERE facture_id = ?
        
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise e
```

### Mettre à jour prix d'une facture

```python
async def majMontantEtHistorique(facture_id, new_price):
    await conn.begin()
    try:
        # 1. Récupérer planning_id
        planning_id = SELECT planning_id FROM Facture WHERE facture_id = ?
        
        # 2. Récupérer ancien prix
        old_price = SELECT montant FROM Facture WHERE facture_id = ?
        
        # 3. Mettre à jour TOUTES factures du planning
        UPDATE Facture 
        SET montant = new_price
        WHERE planning_id = planning_id  # ← TOUTES les factures!
        
        # 4. Enregistrer historique
        INSERT INTO Historique_prix (facture_id, ancien_prix, nouveau_prix, ...)
        
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise e
```

**Why**: Toutes les factures du même planning doivent avoir le même prix

## 📈 Indexes de performance

```sql
-- Déjà créés (voir setting_bd.py)
INDEX idx_client_id ON Contrat(client_id)
INDEX idx_client_id ON Traitement(contrat_id)
INDEX idx_traitement_id ON Planning(traitement_id)
INDEX idx_planning_id ON PlanningDetails(planning_id)
INDEX idx_planning_detail_id ON Facture(planning_detail_id)
INDEX idx_statut ON PlanningDetails(statut)          -- Pour filtrer "À venir"
INDEX idx_date ON PlanningDetails(date_planification) -- Pour filtrer par mois
```

## 🚨 Constraints importantes

```sql
-- Cascade delete
FOREIGN KEY (client_id) REFERENCES Client(client_id) ON DELETE CASCADE
-- → Supprimer client → suppr contrats, traitements, plannings, factures

-- UNIQUE
UNIQUE INDEX (email) ON Client
UNIQUE INDEX (reference_contrat) ON Contrat
-- → Pas de doublons email ou contrats
```

## 📝 Notes de maintenance

### Sauvegarder la BD
```bash
mysqldump -u root -p Planificator > backup.sql
```

### Restaurer la BD
```bash
mysql -u root -p Planificator < backup.sql
```

### Vérifier intégrité FK
```sql
SELECT * FROM Facture 
WHERE planning_detail_id NOT IN 
  (SELECT planning_detail_id FROM PlanningDetails);
-- Devrait retourner 0 lignes
```

---

**Créé**: 23 décembre 2025
**Version BD**: MySQL 8.0+
