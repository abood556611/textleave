import sqlite3
import os
from datetime import datetime, timedelta
from config import Config


class Database:
    """Simple SQLite database for user subscriptions"""
    
    def __init__(self, db_path='textleaf.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_type TEXT,
                status TEXT,
                payment_id TEXT,
                amount REAL,
                currency TEXT,
                starts_at TEXT,
                expires_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_id TEXT UNIQUE,
                main_text TEXT,
                duration INTEGER,
                fps INTEGER,
                resolution TEXT,
                is_premium INTEGER,
                status TEXT,
                file_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, email):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (email) VALUES (?)', (email,))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            # User already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return row['id'] if row else None
        finally:
            conn.close()
    
    def get_user(self, user_id=None, email=None):
        """Get user by ID or email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        elif email:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        else:
            conn.close()
            return None
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_subscription(self, user_id, plan_type, payment_id, amount, currency='USD'):
        """Create a new subscription"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        starts_at = datetime.now()
        
        if plan_type == 'monthly':
            expires_at = starts_at + timedelta(days=30)
        elif plan_type == 'yearly':
            expires_at = starts_at + timedelta(days=365)
        else:
            expires_at = starts_at + timedelta(days=30)
        
        cursor.execute('''
            INSERT INTO subscriptions 
            (user_id, plan_type, status, payment_id, amount, currency, starts_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            plan_type,
            'active',
            payment_id,
            amount,
            currency,
            starts_at.isoformat(),
            expires_at.isoformat()
        ))
        
        subscription_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return subscription_id
    
    def get_subscription(self, subscription_id=None, user_id=None, payment_id=None):
        """Get subscription by ID, user ID, or payment ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if subscription_id:
            cursor.execute('SELECT * FROM subscriptions WHERE id = ?', (subscription_id,))
        elif user_id:
            cursor.execute('''
                SELECT * FROM subscriptions 
                WHERE user_id = ? AND status = "active"
                ORDER BY expires_at DESC LIMIT 1
            ''', (user_id,))
        elif payment_id:
            cursor.execute('SELECT * FROM subscriptions WHERE payment_id = ?', (payment_id,))
        else:
            conn.close()
            return None
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def is_subscription_active(self, user_id):
        """Check if user has active subscription"""
        subscription = self.get_subscription(user_id=user_id)
        
        if not subscription:
            return False
        
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        return expires_at > datetime.now()
    
    def create_video(self, video_id, main_text, duration, fps, resolution, is_premium, user_id=None):
        """Create a new video record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO videos
            (user_id, video_id, main_text, duration, fps, resolution, is_premium, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, video_id, main_text, duration, fps, resolution, int(is_premium), 'processing'))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def update_video_status(self, video_id, status, file_path=None):
        """Update video status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if file_path:
            cursor.execute('''
                UPDATE videos SET status = ?, file_path = ? WHERE video_id = ?
            ''', (status, file_path, video_id))
        else:
            cursor.execute('''
                UPDATE videos SET status = ? WHERE video_id = ?
            ''', (status, video_id))
        
        conn.commit()
        conn.close()
    
    def get_video(self, video_id):
        """Get video record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_user_videos(self, user_id, limit=10):
        """Get user's videos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM videos WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# Initialize database
db = Database()
