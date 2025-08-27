#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application principale de gestion de présence biométrique
Connexion à une pointeuse ZKTeco et gestion complète de la présence du personnel
"""

import logging
import threading
import schedule
import time
from datetime import datetime
from gui.main_window import MainWindow
from db_manager import db_manager
from zk_manager import ZKManager
from employee_manager import employee_manager
from attendance_manager import attendance_manager
from config import ZK_IP, ZK_PORT, SYNC_INTERVAL, AUTO_SYNC_TIME, AUTO_SYNC_ENABLED, REQUIRE_SYNC_CONFIRMATION

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AttendanceApp:
    def __init__(self):
        self.main_window = None
        self.sync_thread = None
        self.running = False
        self.zk_manager = ZKManager(ZK_IP, ZK_PORT)
    
    def initialize(self):
        """Initialiser l'application"""
        try:
            logger.info("Initialisation de l'application de gestion de présence")
            
            # Initialiser la base de données
            logger.info("Initialisation de la base de données...")
            # La base de données est déjà initialisée via db_manager
            
            # Tenter la connexion à la pointeuse
            self._connect_to_zk()
            
            # Démarrer la synchronisation automatique
            self._start_auto_sync()
            
            logger.info("Application initialisée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            return False
    
    def _connect_to_zk(self):
        """Tenter de se connecter à la pointeuse ZKTeco avec gestion améliorée des erreurs"""
        try:
            logger.info(f"Tentative de connexion à la pointeuse ZKTeco ({ZK_IP}:{ZK_PORT})...")
            self.zk_manager.connect()
            logger.info("Connexion à la pointeuse établie avec succès")
            return True
        except Exception as e:
            logger.warning(f"Impossible de se connecter à la pointeuse: {e}")
            logger.info("L'application fonctionnera en mode hors ligne")
            
            # Ajouter un log de synchronisation pour l'échec de connexion
            try:
                db_manager.add_sync_log('connection', 0, 'error', f"Échec de connexion: {e}")
            except Exception as log_error:
                logger.error(f"Erreur lors de l'ajout du log de connexion: {log_error}")
                
            return False
    
    def _start_auto_sync(self):
        """Démarrer la synchronisation automatique"""
        try:
            if AUTO_SYNC_ENABLED:
                # Planifier la synchronisation quotidienne
                schedule.every().day.at(AUTO_SYNC_TIME).do(self._synchronize_all)
                
                # Démarrer le thread de planification
                self.running = True
                self.sync_thread = threading.Thread(target=self._schedule_runner, daemon=True)
                self.sync_thread.start()
                
                logger.info(f"Synchronisation automatique planifiée à {AUTO_SYNC_TIME} chaque jour")
            else:
                logger.info("Synchronisation automatique désactivée dans la configuration")
                
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la synchronisation automatique: {e}")
    
    def _schedule_runner(self):
        """Exécuteur des tâches planifiées"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _synchronize_all(self):
        """Synchroniser toutes les données avec la pointeuse avec gestion améliorée des erreurs"""
        try:
            logger.info("Début de la synchronisation automatique")
            
            # Vérifier si la confirmation est requise
            if REQUIRE_SYNC_CONFIRMATION:
                logger.info("Confirmation requise pour la synchronisation automatique - opération annulée")
                db_manager.add_sync_log('auto_sync', 0, 'warning', 'Confirmation requise - opération annulée')
                return
            
            # Vérifier la connexion et tenter de reconnecter si nécessaire
            if not self.zk_manager.zk:
                logger.info("Tentative de reconnexion pour la synchronisation automatique...")
                if not self._connect_to_zk():
                    logger.warning("Impossible de se connecter à la pointeuse pour la synchronisation automatique")
                    db_manager.add_sync_log('auto_sync', 0, 'error', 'Pointeuse non connectée')
                    return
            
            # Synchroniser les utilisateurs
            user_sync_result = self._synchronize_users()
            
            # Synchroniser la présence
            attendance_sync_result = self._synchronize_attendance()
            
            logger.info("Synchronisation automatique terminée")
            db_manager.add_sync_log('auto_sync', user_sync_result + attendance_sync_result, 'success', 
                                   f'Utilisateurs: {user_sync_result}, Présence: {attendance_sync_result}')
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation automatique: {e}")
            db_manager.add_sync_log('auto_sync', 0, 'error', str(e))
    
    def _synchronize_users(self):
        """Synchroniser les utilisateurs depuis la pointeuse"""
        try:
            if self.zk_manager.zk:
                users = self.zk_manager.import_users()
                if users:
                    imported_count = employee_manager.import_users_from_zk(users)
                    logger.info(f"{imported_count} utilisateurs synchronisés depuis la pointeuse")
                    db_manager.add_sync_log('users', imported_count, 'success')
                    return imported_count
                else:
                    logger.warning("Aucun utilisateur trouvé sur la pointeuse")
                    db_manager.add_sync_log('users', 0, 'warning', 'Aucun utilisateur trouvé')
                    return 0
            else:
                logger.warning("Impossible de synchroniser les utilisateurs: pointeuse non connectée")
                db_manager.add_sync_log('users', 0, 'error', 'Pointeuse non connectée')
                return 0
                
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation des utilisateurs: {e}")
            db_manager.add_sync_log('users', 0, 'error', str(e))
            return 0
    
    def _synchronize_attendance(self):
        """Synchroniser les données de présence depuis la pointeuse"""
        try:
            if self.zk_manager.zk:
                attendance_data = self.zk_manager.get_attendance_data()
                if attendance_data:
                    synced_count = attendance_manager.sync_attendance_data(attendance_data)
                    logger.info(f"{synced_count} logs de présence synchronisés depuis la pointeuse")
                    db_manager.add_sync_log('attendance', synced_count, 'success')
                    return synced_count
                else:
                    logger.warning("Aucune donnée de présence trouvée sur la pointeuse")
                    db_manager.add_sync_log('attendance', 0, 'warning', 'Aucune donnée de présence')
                    return 0
            else:
                logger.warning("Impossible de synchroniser la présence: pointeuse non connectée")
                db_manager.add_sync_log('attendance', 0, 'error', 'Pointeuse non connectée')
                return 0
                
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation de la présence: {e}")
            db_manager.add_sync_log('attendance', 0, 'error', str(e))
            return 0

    def synchronize_users_with_confirmation(self):
        """Synchroniser les utilisateurs avec confirmation de l'utilisateur"""
        try:
            if not self.zk_manager.zk:
                logger.warning("Impossible de synchroniser les utilisateurs: pointeuse non connectée")
                return False
            
            users = self.zk_manager.import_users()
            if not users:
                logger.warning("Aucun utilisateur trouvé sur la pointeuse")
                return False
            
            # Demander confirmation à l'utilisateur
            if REQUIRE_SYNC_CONFIRMATION:
                logger.info(f"{len(users)} utilisateurs trouvés sur la pointeuse - confirmation requise")
                # Dans l'interface graphique, cette confirmation sera gérée par une boîte de dialogue
                return False
            
            imported_count = employee_manager.import_users_from_zk(users)
            logger.info(f"{imported_count} utilisateurs synchronisés depuis la pointeuse")
            db_manager.add_sync_log('users', imported_count, 'success')
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation des utilisateurs: {e}")
            db_manager.add_sync_log('users', 0, 'error', str(e))
            return False

    def synchronize_attendance_with_confirmation(self):
        """Synchroniser la présence avec confirmation de l'utilisateur"""
        try:
            if not self.zk_manager.zk:
                logger.warning("Impossible de synchroniser la présence: pointeuse non connectée")
                return False
            
            attendance_data = self.zk_manager.get_attendance_data()
            if not attendance_data:
                logger.warning("Aucune donnée de présence trouvée sur la pointeuse")
                return False
            
            # Demander confirmation à l'utilisateur
            if REQUIRE_SYNC_CONFIRMATION:
                logger.info(f"{len(attendance_data)} logs de présence trouvés - confirmation requise")
                # Dans l'interface graphique, cette confirmation sera gérée par une boîte de dialogue
                return False
            
            synced_count = attendance_manager.sync_attendance_data(attendance_data)
            logger.info(f"{synced_count} logs de présence synchronisés depuis la pointeuse")
            db_manager.add_sync_log('attendance', synced_count, 'success')
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation de la présence: {e}")
            db_manager.add_sync_log('attendance', 0, 'error', str(e))
            return False
    
    def run_gui(self):
        """Lancer l'interface graphique"""
        try:
            logger.info("Lancement de l'interface graphique")
            self.main_window = MainWindow()
            self.main_window.run()
            
        except Exception as e:
            logger.error(f"Erreur lors du lancement de l'interface graphique: {e}")
            raise
    
    def cleanup(self):
        """Nettoyer les ressources avant la fermeture"""
        try:
            logger.info("Nettoyage des ressources...")
            self.running = False
            
            # Déconnecter la pointeuse
            if self.zk_manager.zk:
                self.zk_manager.disconnect()
            
            # Fermer la base de données
            db_manager.close()
            
            logger.info("Nettoyage terminé")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale"""
    app = AttendanceApp()
    
    try:
        # Initialiser l'application
        if not app.initialize():
            logger.error("Échec de l'initialisation de l'application")
            return
        
        # Lancer l'interface graphique
        app.run_gui()
        
    except KeyboardInterrupt:
        logger.info("Application interrompue par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
    finally:
        # Nettoyer avant de quitter
        app.cleanup()

if __name__ == "__main__":
    main()
