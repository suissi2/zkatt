# Application de Gestion de Présence Biométrique

Une application complète en Python pour la gestion de la présence du personnel avec connexion à des pointeuses biométriques ZKTeco.

## 🚀 Fonctionnalités

### 🔌 Connexion ZKTeco
- Connexion automatique à la pointeuse (IP: 10.0.0.4)
- Récupération des données de pointage (entrée/sortie)
- Synchronisation bidirectionnelle

### 🗄️ Base de Données
- Base SQLite locale avec chiffrement
- Tables: départements, employés, logs de présence, rapports
- Synchronisation automatique des données

### 👥 Gestion des Employés
- CRUD complet (Ajouter, Modifier, Supprimer, Rechercher)
- Gestion des départements
- Import automatique depuis la pointeuse
- Statuts actif/inactif

### 📊 Suivi de Présence
- Affichage en temps réel des entrées/sorties
- Historique consultable par date/employé/département
- Statistiques: retards, absences, heures supplémentaires
- Calcul automatique des heures travaillées

### 📋 Rapports Détaillés
- Export Excel (.xlsx) avec mise en forme
- Export PDF professionnel
- Rapports journaliers et mensuels
- Filtrage par employé et département

### 🎨 Interface Moderne
- Interface CustomTkinter moderne et responsive
- 5 onglets: Employés, Départements, Présence, Rapports, Synchronisation
- Tableaux dynamiques avec filtres
- Thèmes clair/sombre

## 📦 Installation

### Prérequis
- Python 3.8+
- Pointeuse ZKTeco connectée au réseau

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Dépendances principales
- `pyzk==0.9.1` - Connexion ZKTeco
- `customtkinter==5.2.0` - Interface moderne
- `openpyxl==3.1.2` - Export Excel
- `reportlab==4.0.8` - Export PDF
- `Pillow==10.1.0` - Traitement d'images
- `schedule==1.2.0` - Planification des tâches

## ⚙️ Configuration

Modifiez le fichier `config.py` selon vos besoins:

```python
# Configuration ZKTeco
ZK_IP = "10.0.0.4"  # Adresse IP de votre pointeuse
ZK_PORT = 4370
ZK_TIMEOUT = 30

# Configuration base de données
DB_PATH = "attendance.db"

# Paramètres de synchronisation
SYNC_INTERVAL = 3600  # 1 heure en secondes
AUTO_SYNC_TIME = "08:00"  # Synchronisation automatique à 8h00

# Configuration entreprise
COMPANY_NAME = "Votre Entreprise"
COMPANY_ADDRESS = "Adresse de l'entreprise"
COMPANY_PHONE = "+33 1 23 45 67 89"
```

## 🚀 Utilisation

### Lancement de l'application
```bash
python main.py
```

### Synchronisation manuelle
- Onglet "Synchronisation" → Boutons "Synchroniser Présence" / "Synchroniser Utilisateurs"

### Gestion des employés
- Onglet "Employés" → Ajouter/Modifier/Supprimer des employés
- Import automatique depuis la pointeuse disponible

### Génération de rapports
- Onglet "Rapports" → Sélectionner le type et la période
- Exports disponibles en Excel et PDF

## 📁 Structure du Projet

```
zkatt/
├── main.py              # Application principale
├── config.py            # Configuration
├── db_manager.py        # Gestion base de données
├── zk_manager.py        # Connexion ZKTeco
├── employee_manager.py  # Gestion employés
├── attendance_manager.py # Gestion présence
├── report_manager.py    # Génération rapports
├── requirements.txt     # Dépendances
├── gui/                 # Interface graphique
│   ├── main_window.py   # Fenêtre principale
│   ├── employee_dialog.py # Dialogue employé
│   └── department_dialog.py # Dialogue département
└── reports/             # Dossier des rapports générés
```

## 🔧 Architecture

### Modulaire et Extensible
- Architecture modulaire avec séparation des concerns
- Chaque manager gère un domaine spécifique
- Interface graphique découplée de la logique métier

### Gestion d'Erreurs
- Logging complet avec rotation des fichiers
- Gestion des erreurs de connexion ZKTeco
- Mode hors ligne disponible

### Sécurité
- Validation des données d'entrée
- Gestion sécurisée des connexions
- Base de données locale chiffrée

## 🎯 Fonctionnalités Avancées

### Synchronisation Automatique
- Planification quotidienne à heure fixe
- Synchronisation incrémentielle
- Logs de synchronisation détaillés

### Statistiques Avancées
- Calcul des heures travaillées
- Détection des retards et absences
- Heures supplémentaires automatiques
- Résumés par employé et département

### Export Professionnel
- Mise en forme Excel avancée
- Templates PDF personnalisables
- En-têtes avec logo d'entreprise

## 🐛 Dépannage

### Problèmes de Connexion ZKTeco
1. Vérifier l'adresse IP dans `config.py`
2. Vérifier la connectivité réseau
3. Redémarrer la pointeuse si nécessaire

### Erreurs de Base de Données
1. Vérifier les permissions d'écriture
2. Supprimer le fichier `attendance.db` pour réinitialiser

### Interface Graphique
- Redémarrer l'application en cas de plantage
- Vérifier l'installation de CustomTkinter

## 📝 Journal des Modifications

### Version 1.0.0
- ✅ Connexion ZKTeco fonctionnelle
- ✅ Gestion complète CRUD des employés
- ✅ Synchronisation automatique
- ✅ Interface graphique moderne
- ✅ Export Excel et PDF
- ✅ Statistiques avancées

## 📞 Support

Pour toute question ou problème, consulter la documentation ZKTeco ou créer une issue sur le repository.

## 📄 Licence

Propriétaire - Usage interne uniquement

---

**Note**: Assurez-vous que la pointeuse ZKTeco est correctement configurée et accessible sur le réseau avant utilisation.
bouba