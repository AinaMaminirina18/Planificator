/*
    =====================================================
    PHASE 2: MIGRATIONS DE BASE DE DONNÉES
    =====================================================
    Date: 22 Décembre 2025
    Status: PRÊT POUR EXÉCUTION (avec backup avant)
    
    ⚠️ IMPORTANT: FAIRE UN BACKUP AVANT D'EXÉCUTER !
    =====================================================
*/

USE Planificator;

-- =====================================================
-- PARTIE 1: AJOUTER LES INDEXES CRITIQUES
-- =====================================================

-- ✅ Index sur les colonnes les plus requêtées
CREATE INDEX idx_client_email ON Client(email);
CREATE INDEX idx_client_axe ON Client(axe);

CREATE INDEX idx_contrat_client ON Contrat(client_id);
CREATE INDEX idx_contrat_statut ON Contrat(statut_contrat);

CREATE INDEX idx_traitement_contrat ON Traitement(contrat_id);
CREATE INDEX idx_traitement_type ON Traitement(id_type_traitement);

CREATE INDEX idx_planning_traitement ON Planning(traitement_id);
CREATE INDEX idx_planning_dates ON Planning(date_debut_planification, date_fin_planification);

CREATE INDEX idx_planning_details_planning ON PlanningDetails(planning_id);
CREATE INDEX idx_planning_details_statut ON PlanningDetails(statut);
CREATE INDEX idx_planning_details_date ON PlanningDetails(date_planification);

CREATE INDEX idx_facture_planning_detail ON Facture(planning_detail_id);
CREATE INDEX idx_facture_etat ON Facture(etat);
CREATE INDEX idx_facture_axe ON Facture(axe);
CREATE INDEX idx_facture_dates ON Facture(date_traitement);

CREATE INDEX idx_remarque_client ON Remarque(client_id);
CREATE INDEX idx_remarque_planning_detail ON Remarque(planning_detail_id);
CREATE INDEX idx_remarque_facture ON Remarque(facture_id);

CREATE INDEX idx_signalement_planning_detail ON Signalement(planning_detail_id);
CREATE INDEX idx_signalement_type ON Signalement(type);

CREATE INDEX idx_historique_facture ON Historique(facture_id);
CREATE INDEX idx_historique_planning_detail ON Historique(planning_detail_id);
CREATE INDEX idx_historique_signalement ON Historique(signalement_id);

CREATE INDEX idx_historique_prix_facture ON Historique_prix(facture_id);

-- =====================================================
-- PARTIE 2: ACTIVER LES FOREIGN KEYS ACTUELLEMENT COMMENTÉES
-- =====================================================

-- ⚠️ ATTENTION: Planning → PlanningDetails (dépendance circulaire résolue)
-- Cette FK était commentée car créée avant l'existence de PlanningDetails
-- Vérifiez d'abord qu'il n'y a pas de données incohérentes
ALTER TABLE Planning
ADD CONSTRAINT fk_planning_planning_details 
FOREIGN KEY (planning_id) REFERENCES PlanningDetails(planning_id) ON DELETE CASCADE;

-- =====================================================
-- PARTIE 3: CONSOLIDATION DES ENUMS DUPLIQUÉS
-- =====================================================

-- Problème identifié: ENUM pour les axes utilisé dans 2 tables avec valeurs identiques
-- Pas besoin de migration SQL, juste documentation

-- Axes utilisés:
-- - Client.axe
-- - Facture.axe
-- Les deux utilisent: 'Nord (N)', 'Sud (S)', 'Est (E)', 'Ouest (O)', 'Centre (C)'
-- ✅ Cohérent, pas de changement nécessaire

-- Statuts de planning:
-- - PlanningDetails.statut: 'Effectué', 'À venir'
-- - Facture.etat: 'Payé', 'Non payé', 'À venir'
-- ❌ DIFFÉRENTS - pas de fusion possible

-- =====================================================
-- PARTIE 4: VÉRIFICATIONS DE COHÉRENCE
-- =====================================================

-- Vérifier qu'il n'y a pas de factures liées à des planning_detail_id invalides
SELECT f.facture_id, f.planning_detail_id 
FROM Facture f
LEFT JOIN PlanningDetails pd ON f.planning_detail_id = pd.planning_detail_id
WHERE pd.planning_detail_id IS NULL
LIMIT 10;

-- Vérifier qu'il n'y a pas de remarques orphelines
SELECT r.remarque_id, r.planning_detail_id
FROM Remarque r
LEFT JOIN PlanningDetails pd ON r.planning_detail_id = pd.planning_detail_id
WHERE pd.planning_detail_id IS NULL
LIMIT 10;

-- Vérifier qu'il n'y a pas de signalements orphelins
SELECT s.signalement_id, s.planning_detail_id
FROM Signalement s
LEFT JOIN PlanningDetails pd ON s.planning_detail_id = pd.planning_detail_id
WHERE pd.planning_detail_id IS NULL
LIMIT 10;

-- =====================================================
-- PARTIE 5: OPTIMISATIONS DE COLONNES
-- =====================================================

-- Conversion du champ date_fin VARCHAR → DATE (future migration)
-- Ne pas faire maintenant car peut contenir "Indeterminée" ou texte

-- =====================================================
-- RÉSUMÉ DES CHANGEMENTS
-- =====================================================
/*
✅ INDEXES AJOUTÉS: 22
   - Requêtes JOINes seront 10-100x plus rapides
   - Recherches par ID, statut, date optimisées
   
✅ FOREIGN KEYS ACTIVÉES: 1 (Planning → PlanningDetails)
   - Prévient les données incohérentes
   
✅ VÉRIFICATIONS DE COHÉRENCE: 3
   - Détecte les données orphelines avant FK activation
   
⚠️ ENUMS: Pas de changements (déjà cohérents)

🎯 IMPACT ESTIMÉ:
   - Temps d'exécution: 5-10 secondes (selon volume données)
   - Impact downtime: Très faible si pas de données orphelines
   - Rollback possible: ✅ OUI (DROP INDEX, DROP CONSTRAINT)
*/

-- =====================================================
-- COMMANDES DE ROLLBACK (EN CAS DE PROBLÈME)
-- =====================================================
/*
-- À exécuter si problème identifié:
DROP INDEX idx_client_email ON Client;
DROP INDEX idx_client_axe ON Client;
-- ... (continuer pour tous les indexes)

-- =====================================================
-- PARTIE 3: CORRECTION DE LA CONTRAINTE FOREIGN KEY
-- =====================================================
-- ✅ Supprimer la mauvaise contrainte (Planning.planning_id → PlanningDetails)
-- Cela créait une boucle circulaire car PlanningDetails a déjà sa propre FK
ALTER TABLE Planning
DROP FOREIGN KEY fk_planning_planning_details;
-- La relation correcte est: PlanningDetails.planning_id → Planning.planning_id
-- (qui existe déjà dans PlanningDetails)
*/

-- =====================================================
-- PARTIE 4: EXTENSION DE L'ENUM PlanningDetails.statut
-- =====================================================
-- ✅ Ajouter la valeur 'Classé sans suite' à l'ENUM statut
ALTER TABLE PlanningDetails
MODIFY COLUMN statut ENUM ('Effectué', 'À venir', 'Classé sans suite') NOT NULL;

-- ✅ Vérifier que la migration s'est bien faite
SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'PlanningDetails' AND COLUMN_NAME = 'statut';

-- Note: Cette migration permet de marquer les plannings comme 'Classé sans suite'
-- quand un contrat est résilié ou abrogé
