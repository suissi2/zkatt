# Configuration de l'application de gestion de présence biométrique

# Configuration ZKTeco
ZK_IP = "10.0.0.4"
ZK_PORT = 4370
ZK_TIMEOUT = 30

# Configuration base de données
DB_PATH = "attendance.db"

# Configuration des rapports
REPORTS_DIR = "reports"
EXCEL_TEMPLATE = "template.xlsx"

# Paramètres de synchronisation
SYNC_INTERVAL = 3600  # 1 heure en secondes
AUTO_SYNC_TIME = "08:00"  # Synchronisation automatique à 8h00
AUTO_SYNC_ENABLED = False  # Désactiver la synchronisation automatique par défaut
REQUIRE_SYNC_CONFIRMATION = True  # Demander confirmation avant synchronisation

# Chemins des fichiers
LOG_FILE = "app.log"

# Configuration interface
THEME = "light"  # dark, light, system
COLOR_THEME = "blue"  # blue, green, dark-blue

# Paramètres d'entreprise
COMPANY_NAME = "Votre Entreprise"
COMPANY_ADDRESS = "Adresse de l'entreprise"
COMPANY_PHONE = "+33 1 23 45 67 89"
