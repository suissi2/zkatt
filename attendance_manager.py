import logging
from datetime import datetime, timedelta
from db_manager import db_manager
from employee_manager import employee_manager

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttendanceManager:
    def __init__(self):
        self.db = db_manager
    
    def sync_attendance_data(self, zk_attendance_data):
        """Synchroniser les données de pointage depuis la pointeuse"""
        try:
            synced_count = 0
            for attendance in zk_attendance_data:
                # Vérifier si le log existe déjà
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    SELECT id FROM attendance_logs 
                    WHERE employee_id = ? AND datetime = ? AND type = ?
                """, (attendance.user_id, attendance.timestamp, attendance.status))
                existing = cursor.fetchone()
                
                if not existing:
                    # Ajouter le nouveau log
                    self.db.add_attendance_log(attendance.user_id, attendance.timestamp, attendance.status)
                    synced_count += 1
            
            logger.info(f"{synced_count} nouveaux logs de présence synchronisés")
            return synced_count
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation des données de présence: {e}")
            return 0
    
    def get_daily_attendance(self, date=None):
        """Récupérer les présences pour une journée spécifique"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            attendance_data = self.db.get_attendance_logs(start_date=date, end_date=date)
            
            # Organiser les données par employé
            employees_attendance = {}
            for log in attendance_data:
                emp_id = log['employee_id']
                if emp_id not in employees_attendance:
                    employees_attendance[emp_id] = {
                        'employee': f"{log['first_name']} {log['last_name']}",
                        'department': log['department_name'],
                        'logs': []
                    }
                employees_attendance[emp_id]['logs'].append({
                    'time': log['datetime'],
                    'type': log['type']
                })
            
            return employees_attendance
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des présences quotidiennes: {e}")
            return {}
    
    def calculate_attendance_stats(self, start_date, end_date, employee_id=None, department_id=None):
        """Calculer les statistiques de présence"""
        try:
            logs = self.db.get_attendance_logs(start_date, end_date, employee_id, department_id)
            
            stats = {
                'total_employees': 0,
                'present_employees': 0,
                'late_employees': 0,
                'absent_employees': 0,
                'overtime_hours': 0,
                'total_work_hours': 0
            }
            
            # Logique de calcul des statistiques
            employee_days = {}
            for log in logs:
                emp_id = log['employee_id']
                log_date = log['datetime'].split()[0]  # Extraire la date
                
                if emp_id not in employee_days:
                    employee_days[emp_id] = {
                        'name': f"{log['first_name']} {log['last_name']}",
                        'days': {}
                    }
                
                if log_date not in employee_days[emp_id]['days']:
                    employee_days[emp_id]['days'][log_date] = {'in': None, 'out': None}
                
                if log['type'] == 'IN':
                    employee_days[emp_id]['days'][log_date]['in'] = log['datetime']
                elif log['type'] == 'OUT':
                    employee_days[emp_id]['days'][log_date]['out'] = log['datetime']
            
            # Calculer les statistiques
            for emp_id, emp_data in employee_days.items():
                stats['total_employees'] += 1
                present_days = 0
                
                for day, times in emp_data['days'].items():
                    if times['in'] and times['out']:
                        present_days += 1
                        # Calculer les heures de travail
                        in_time = datetime.strptime(times['in'], '%Y-%m-%d %H:%M:%S')
                        out_time = datetime.strptime(times['out'], '%Y-%m-%d %H:%M:%S')
                        work_hours = (out_time - in_time).total_seconds() / 3600
                        stats['total_work_hours'] += work_hours
                        
                        # Vérifier les heures supplémentaires
                        if work_hours > 8:
                            stats['overtime_hours'] += work_hours - 8
                        
                        # Vérifier les retards
                        if in_time.time() > datetime.strptime('09:00:00', '%H:%M:%S').time():
                            stats['late_employees'] += 1
                
                if present_days > 0:
                    stats['present_employees'] += 1
                else:
                    stats['absent_employees'] += 1
            
            return stats
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de présence: {e}")
            return {}
    
    def get_employee_attendance_summary(self, employee_id, start_date, end_date):
        """Récupérer le résumé de présence d'un employé"""
        try:
            logs = self.db.get_attendance_logs(start_date, end_date, employee_id)
            
            summary = {
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'late_days': 0,
                'early_departures': 0,
                'total_hours': 0,
                'overtime_hours': 0
            }
            
            days_data = {}
            for log in logs:
                log_date = log['datetime'].split()[0]
                if log_date not in days_data:
                    days_data[log_date] = {'in': None, 'out': None}
                
                if log['type'] == 'IN':
                    days_data[log_date]['in'] = log['datetime']
                elif log['type'] == 'OUT':
                    days_data[log_date]['out'] = log['datetime']
            
            summary['total_days'] = len(days_data)
            
            for day, times in days_data.items():
                if times['in'] and times['out']:
                    summary['present_days'] += 1
                    
                    in_time = datetime.strptime(times['in'], '%Y-%m-%d %H:%M:%S')
                    out_time = datetime.strptime(times['out'], '%Y-%m-%d %H:%M:%S')
                    work_hours = (out_time - in_time).total_seconds() / 3600
                    summary['total_hours'] += work_hours
                    
                    # Vérifier les retards
                    if in_time.time() > datetime.strptime('09:00:00', '%H:%M:%S').time():
                        summary['late_days'] += 1
                    
                    # Vérifier les départs anticipés
                    if out_time.time() < datetime.strptime('17:00:00', '%H:%M:%S').time():
                        summary['early_departures'] += 1
                    
                    # Vérifier les heures supplémentaires
                    if work_hours > 8:
                        summary['overtime_hours'] += work_hours - 8
                else:
                    summary['absent_days'] += 1
            
            return summary
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du résumé de présence: {e}")
            return {}

# Instance globale du gestionnaire de présence
attendance_manager = AttendanceManager()
