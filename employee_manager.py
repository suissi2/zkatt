import logging
from db_manager import db_manager

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmployeeManager:
    def __init__(self):
        self.db = db_manager
    
    def add_employee(self, employee_id, first_name, last_name, department_id=None, status='active'):
        """Ajouter un nouvel employé"""
        try:
            employee_id = self.db.add_employee(employee_id, first_name, last_name, department_id, status)
            if employee_id:
                logger.info(f"Employé ajouté avec succès: {first_name} {last_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de l'employé: {e}")
            return False
    
    def update_employee(self, employee_id, first_name=None, last_name=None, department_id=None, status=None):
        """Mettre à jour les informations d'un employé"""
        try:
            cursor = self.db.connection.cursor()
            updates = []
            params = []
            
            if first_name:
                updates.append("first_name = ?")
                params.append(first_name)
            if last_name:
                updates.append("last_name = ?")
                params.append(last_name)
            if department_id is not None:
                updates.append("department_id = ?")
                params.append(department_id)
            if status:
                updates.append("status = ?")
                params.append(status)
            
            if not updates:
                return False
                
            params.append(employee_id)
            query = f"UPDATE employees SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.db.connection.commit()
            
            logger.info(f"Employé {employee_id} mis à jour avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'employé: {e}")
            return False
    
    def delete_employee(self, employee_id):
        """Supprimer un employé"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            self.db.connection.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Employé {employee_id} supprimé avec succès")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'employé: {e}")
            return False
    
    def get_employee(self, employee_id):
        """Récupérer un employé spécifique"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT e.*, d.name as department_name 
                FROM employees e 
                LEFT JOIN departments d ON e.department_id = d.id 
                WHERE e.id = ?
            """, (employee_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'employé: {e}")
            return None
    
    def search_employees(self, search_term, department_id=None, status=None):
        """Rechercher des employés par nom, prénom ou matricule"""
        try:
            cursor = self.db.connection.cursor()
            query = """
                SELECT e.*, d.name as department_name 
                FROM employees e 
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE (e.first_name LIKE ? OR e.last_name LIKE ? OR e.employee_id LIKE ?)
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if department_id:
                query += " AND e.department_id = ?"
                params.append(department_id)
            if status:
                query += " AND e.status = ?"
                params.append(status)
            
            query += " ORDER BY e.last_name, e.first_name"
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'employés: {e}")
            return []
    
    def get_employees_by_department(self, department_id):
        """Récupérer tous les employés d'un département"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT e.*, d.name as department_name 
                FROM employees e 
                LEFT JOIN departments d ON e.department_id = d.id 
                WHERE e.department_id = ? 
                ORDER BY e.last_name, e.first_name
            """, (department_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des employés par département: {e}")
            return []
    
    def import_users_from_zk(self, zk_users):
        """Importer les utilisateurs depuis la pointeuse ZKTeco"""
        try:
            imported_count = 0
            for user in zk_users:
                # Vérifier si l'utilisateur existe déjà
                cursor = self.db.connection.cursor()
                cursor.execute("SELECT id FROM employees WHERE employee_id = ?", (user.user_id,))
                existing = cursor.fetchone()
                
                if not existing:
                    # Ajouter le nouvel utilisateur
                    self.add_employee(
                        employee_id=user.user_id,
                        first_name=user.name.split(' ')[0] if user.name else 'Inconnu',
                        last_name=' '.join(user.name.split(' ')[1:]) if user.name and len(user.name.split(' ')) > 1 else user.name or 'Inconnu'
                    )
                    imported_count += 1
            
            logger.info(f"{imported_count} nouveaux utilisateurs importés depuis la pointeuse")
            return imported_count
        except Exception as e:
            logger.error(f"Erreur lors de l'importation des utilisateurs: {e}")
            return 0

# Instance globale du gestionnaire d'employés
employee_manager = EmployeeManager()
