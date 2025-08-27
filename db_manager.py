import sqlite3
import logging
from datetime import datetime
from config import DB_PATH

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Établir la connexion à la base de données SQLite"""
        try:
            self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info("Connexion à la base de données établie")
        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            raise
    
    def create_tables(self):
        """Créer les tables nécessaires dans la base de données"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                department_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                datetime TIMESTAMP NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('IN', 'OUT')),
                sync_status TEXT DEFAULT 'synced',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                file_path TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT NOT NULL,
                records_count INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                error_message TEXT,
                sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        try:
            cursor = self.connection.cursor()
            for table in tables:
                cursor.execute(table)
            self.connection.commit()
            logger.info("Tables créées avec succès")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la création des tables: {e}")
            raise
    
    def add_department(self, name):
        """Ajouter un nouveau département"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO departments (name) VALUES (?)", (name,))
            self.connection.commit()
            logger.info(f"Département ajouté: {name}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout du département: {e}")
            return None
    
    def get_departments(self):
        """Récupérer tous les départements"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM departments ORDER BY name")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des départements: {e}")
            return []
    
    def add_employee(self, employee_id, first_name, last_name, department_id=None, status='active'):
        """Ajouter un nouvel employé"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO employees (employee_id, first_name, last_name, department_id, status) VALUES (?, ?, ?, ?, ?)",
                (employee_id, first_name, last_name, department_id, status)
            )
            self.connection.commit()
            logger.info(f"Employé ajouté: {first_name} {last_name}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout de l'employé: {e}")
            return None
    
    def get_employees(self, department_id=None, status=None):
        """Récupérer les employés avec filtres optionnels"""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT e.*, d.name as department_name 
                FROM employees e 
                LEFT JOIN departments d ON e.department_id = d.id
            """
            params = []
            
            if department_id or status:
                query += " WHERE "
                conditions = []
                if department_id:
                    conditions.append("e.department_id = ?")
                    params.append(department_id)
                if status:
                    conditions.append("e.status = ?")
                    params.append(status)
                query += " AND ".join(conditions)
            
            query += " ORDER BY e.last_name, e.first_name"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            # Convert rows to a list of dictionaries
            employees = [
                {**row} for row in rows
            ]
            return employees
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des employés: {e}")
            return []
    
    def add_attendance_log(self, employee_id, datetime_str, log_type):
        """Ajouter un log de présence"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO attendance_logs (employee_id, datetime, type) VALUES (?, ?, ?)",
                (employee_id, datetime_str, log_type)
            )
            self.connection.commit()
            logger.info(f"Log de présence ajouté: employé {employee_id}, {log_type} à {datetime_str}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout du log de présence: {e}")
            return None
    
    def get_attendance_logs(self, start_date=None, end_date=None, employee_id=None, department_id=None):
        """Récupérer les logs de présence avec filtres"""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT al.*, e.first_name, e.last_name, e.employee_id, d.name as department_name
                FROM attendance_logs al
                JOIN employees e ON al.employee_id = e.id
                LEFT JOIN departments d ON e.department_id = d.id
            """
            params = []
            
            conditions = []
            if start_date:
                conditions.append("DATE(al.datetime) >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("DATE(al.datetime) <= ?")
                params.append(end_date)
            if employee_id:
                conditions.append("al.employee_id = ?")
                params.append(employee_id)
            if department_id:
                conditions.append("e.department_id = ?")
                params.append(department_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY al.datetime DESC"
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des logs de présence: {e}")
            return []
    
    def add_report(self, report_type, start_date, end_date, file_path):
        """Ajouter un rapport généré"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO reports (report_type, start_date, end_date, file_path) VALUES (?, ?, ?, ?)",
                (report_type, start_date, end_date, file_path)
            )
            self.connection.commit()
            logger.info(f"Rapport ajouté: {report_type} du {start_date} au {end_date}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout du rapport: {e}")
            return None
    
    def add_sync_log(self, sync_type, records_count, status, error_message=None):
        """Ajouter un log de synchronisation"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO sync_logs (sync_type, records_count, status, error_message) VALUES (?, ?, ?, ?)",
                (sync_type, records_count, status, error_message)
            )
            self.connection.commit()
            logger.info(f"Log de synchronisation ajouté: {sync_type}, {status}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout du log de synchronisation: {e}")
            return None
    
    def close(self):
        """Fermer la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            logger.info("Connexion à la base de données fermée")

    def get_sync_logs(self):
        """Récupérer tous les logs de synchronisation"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM sync_logs ORDER BY sync_time DESC")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des logs de synchronisation: {e}")
            return []
        
# Instance globale de la base de données
db_manager = DatabaseManager()
