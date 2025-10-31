"""
Database repository for managing drowsiness alerts.

This module handles SQLite database operations for storing and retrieving
drowsiness detection alerts with timestamps and metadata.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager


class AlertRepository:
    """Repository class for managing drowsiness alerts in SQLite database."""
    
    def __init__(self, db_path: str = "alerts.db"):
        """
        Initialize the AlertRepository.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ear_value REAL NOT NULL,
                    consecutive_frames INTEGER NOT NULL,
                    duration_seconds REAL DEFAULT 0.0,
                    severity TEXT DEFAULT 'LOW',
                    notes TEXT
                )
            ''')
            
            # Create sessions table for tracking detection sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_alerts INTEGER DEFAULT 0,
                    session_duration REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def log_alert(self, ear_value: float, consecutive_frames: int, 
                  duration: float = 0.0, severity: str = 'LOW', 
                  notes: str = '') -> int:
        """
        Log a drowsiness alert to the database.
        
        Args:
            ear_value: The EAR value that triggered the alert
            consecutive_frames: Number of consecutive frames below threshold
            duration: Duration of the drowsiness event in seconds
            severity: Alert severity level (LOW, MEDIUM, HIGH)
            notes: Additional notes about the alert
            
        Returns:
            The ID of the inserted alert record
        """
        timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (timestamp, ear_value, consecutive_frames, 
                                  duration_seconds, severity, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, ear_value, consecutive_frames, duration, severity, notes))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """
        Get recent alerts from the database.
        
        Args:
            limit: Maximum number of alerts to retrieve
            
        Returns:
            List of alert dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_alerts_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get alerts within a specific date range.
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            List of alert dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE date(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_alert_statistics(self) -> Dict:
        """
        Get statistics about alerts.
        
        Returns:
            Dictionary containing alert statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total alerts
            cursor.execute('SELECT COUNT(*) as total_alerts FROM alerts')
            total_alerts = cursor.fetchone()['total_alerts']
            
            # Alerts today
            today = datetime.now().date().isoformat()
            cursor.execute('''
                SELECT COUNT(*) as today_alerts FROM alerts 
                WHERE date(timestamp) = ?
            ''', (today,))
            today_alerts = cursor.fetchone()['today_alerts']
            
            # Average EAR in alerts
            cursor.execute('SELECT AVG(ear_value) as avg_ear FROM alerts')
            avg_ear_result = cursor.fetchone()['avg_ear']
            avg_ear = round(avg_ear_result, 3) if avg_ear_result else 0.0
            
            # Severity distribution
            cursor.execute('''
                SELECT severity, COUNT(*) as count 
                FROM alerts 
                GROUP BY severity
            ''')
            severity_dist = {row['severity']: row['count'] for row in cursor.fetchall()}
            
            # Most recent alert
            cursor.execute('''
                SELECT timestamp FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            last_alert_row = cursor.fetchone()
            last_alert = last_alert_row['timestamp'] if last_alert_row else None
            
            return {
                'total_alerts': total_alerts,
                'today_alerts': today_alerts,
                'average_ear': avg_ear,
                'severity_distribution': severity_dist,
                'last_alert': last_alert
            }
    
    def start_session(self) -> int:
        """
        Start a new detection session.
        
        Returns:
            Session ID
        """
        timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (start_time)
                VALUES (?)
            ''', (timestamp,))
            
            conn.commit()
            return cursor.lastrowid
    
    def end_session(self, session_id: int) -> None:
        """
        End a detection session.
        
        Args:
            session_id: ID of the session to end
        """
        timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get session start time to calculate duration
            cursor.execute('''
                SELECT start_time FROM sessions WHERE id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if row:
                start_time = datetime.fromisoformat(row['start_time'])
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Count alerts during this session
                cursor.execute('''
                    SELECT COUNT(*) as alert_count FROM alerts 
                    WHERE timestamp >= ?
                ''', (row['start_time'],))
                
                alert_count = cursor.fetchone()['alert_count']
                
                # Update session
                cursor.execute('''
                    UPDATE sessions 
                    SET end_time = ?, total_alerts = ?, session_duration = ?
                    WHERE id = ?
                ''', (timestamp, alert_count, duration, session_id))
                
                conn.commit()
    
    def clear_old_alerts(self, days_to_keep: int = 30) -> int:
        """
        Clear alerts older than specified days.
        
        Args:
            days_to_keep: Number of days of alerts to keep
            
        Returns:
            Number of alerts deleted
        """
        cutoff_date = datetime.now().date()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM alerts 
                WHERE date(timestamp) < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
    
    def export_alerts_to_csv(self, file_path: str) -> bool:
        """
        Export alerts to CSV file.
        
        Args:
            file_path: Path to save the CSV file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            import csv
            
            alerts = self.get_recent_alerts(limit=1000)  # Get last 1000 alerts
            
            with open(file_path, 'w', newline='') as csvfile:
                if alerts:
                    fieldnames = alerts[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for alert in alerts:
                        writer.writerow(alert)
            
            return True
        except Exception:
            return False