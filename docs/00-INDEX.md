# Documentation Planificator - Index

## 📚 Table des matières

1. **[Structure et Architecture](01-STRUCTURE.md)** - Vue d'ensemble de l'architecture
2. **[Problèmes et Solutions](02-PROBLEMES_SOLUTIONS.md)** - Tous les bugs identifiés et corrigés
3. **[Fréquence et Redondance](03-FREQUENCY_SYSTEM.md)** - Logique de la fréquence de traitement
4. **[Pagination et Navigation](04-PAGINATION.md)** - Système de pagination des tableaux
5. **[Base de Données](05-DATABASE.md)** - Structure et requêtes critiques
6. **[Stack Technique](06-TECH_STACK.md)** - Technologies utilisées

## 🎯 Résumé rapide

### Session de correction
**Période**: Décembre 2025  
**Commits**: 18+ corrections majeures  
**Bugs corrigés**: 15+ problèmes critiques  
**État**: ✅ Stable et fonctionnel

### Technologies
- **Frontend**: Kivy + KivyMD (Python 3.13)
- **Backend**: MySQL 8.0+
- **Communication BD**: aiomysql + asyncio

### Points clés
- ✅ Pagination système corrigée (index_global = (page-1) * rows_num + row_num)
- ✅ Fréquence mappée correctement (0-6 = une seule fois à 6 mois)
- ✅ Client ID basé (pas de conflits avec noms dupliqués)
- ✅ Rafraîchissement automatique des tableaux après MAJ
- ✅ Gestion d'erreur complète avec timeouts

---

**Dernière mise à jour**: 23 décembre 2025
