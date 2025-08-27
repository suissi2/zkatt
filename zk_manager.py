import socket
from zk import ZK, const
import logging
from config import ZK_TIMEOUT

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZKManager:
    def __init__(self, ip_address=None, port=None):
        self.zk = None
        self.ip_address = ip_address
        self.port = port

    def connect(self, ip_address=None, port=None):
        """Établir la connexion avec la pointeuse ZKTeco"""
        try:
            # Utiliser les paramètres fournis ou ceux de l'instance
            ip_to_use = ip_address if ip_address else self.ip_address
            port_to_use = port if port else self.port
            
            if not ip_to_use or not port_to_use:
                logger.error("Adresse IP ou port non configuré")
                raise ValueError("Adresse IP ou port non configuré")
                
            self.zk = ZK(ip_to_use, port=port_to_use, timeout=ZK_TIMEOUT, force_udp=True)
            self.zk.connect()
            logger.info(f"Connexion à la pointeuse ZKTeco établie ({ip_to_use}:{port_to_use})")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à la pointeuse: {e}")
            raise

    def disconnect(self):
        """Déconnecter la pointeuse ZKTeco"""
        if self.zk:
            self.zk.disconnect()
            logger.info("Déconnexion de la pointeuse ZKTeco")

    def get_attendance_data(self):
        """Récupérer les données de pointage (entrée/sortie)"""
        try:
            if not self.zk:
                logger.error("La pointeuse n'est pas connectée")
                return []

            attendance_data = self.zk.get_attendance()
            logger.info(f"Données de pointage récupérées: {len(attendance_data)} enregistrements")
            
            # Convertir les données pour avoir le format attendu par la base de données
            converted_data = []
            for attendance in attendance_data:
                # Créer un nouvel objet avec le statut converti
                converted_attendance = type('Attendance', (), {
                    'user_id': attendance.user_id,
                    'timestamp': attendance.timestamp,
                    'status': self._convert_status_code(attendance.status)
                })()
                converted_data.append(converted_attendance)
            
            return converted_data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de pointage: {e}")
            return []
    
    def _convert_status_code(self, status_code):
        """Convertir le code de statut ZKTeco en type IN/OUT"""
        # Selon la documentation ZKTeco:
        # 0: Check-In (Entrée)
        # 1: Check-Out (Sortie)
        # 15: Check-In (Entrée) - valeur courante
        if status_code in [0, 15]:
            return 'IN'
        elif status_code == 1:
            return 'OUT'
        else:
            # Pour les autres codes, on utilise 'IN' par défaut
            logger.warning(f"Code de statut inconnu: {status_code}, utilisation de 'IN' par défaut")
            return 'IN'

    def import_users(self):
        """Importer les utilisateurs depuis la pointeuse"""
        try:
            if not self.zk:
                logger.error("La pointeuse n'est pas connectée")
                return

            users = self.zk.get_users()
            logger.info(f"Utilisateurs récupérés: {len(users)} utilisateurs")
            return users
        except Exception as e:
            logger.error(f"Erreur lors de l'importation des utilisateurs: {e}")

# Instance globale de la gestion de la pointeuse
zk_manager = ZKManager()
