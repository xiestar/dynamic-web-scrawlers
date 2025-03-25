import sqlite3
import os
import logging
import threading
from datetime import datetime

class Database:
    def __init__(self, db_path="database/zhihu_hot_questions.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._thread_local = threading.local()  # 线程本地存储
        self._ensure_db_path()
        self._init_db()
        
    def _ensure_db_path(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _init_db(self):
        """初始化数据库表结构"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    hot_value REAL,
                    attention_increment INTEGER,
                    view_increment INTEGER,
                    answer_increment INTEGER,
                    vote_increment INTEGER,
                    tags TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
            raise
        finally:
            self._close_connection(conn)
    
    def _get_connection(self):
        """获取数据库连接（线程安全）"""
        if not hasattr(self._thread_local, 'conn') or self._thread_local.conn is None:
            self._thread_local.conn = sqlite3.connect(self.db_path)
            self._thread_local.conn.row_factory = sqlite3.Row
        return self._thread_local.conn
    
    def _close_connection(self, conn=None):
        """关闭数据库连接"""
        if conn:
            conn.close()
        elif hasattr(self._thread_local, 'conn') and self._thread_local.conn:
            self._thread_local.conn.close()
            self._thread_local.conn = None
    
    def save_questions(self, questions):
        """保存问题数据到数据库，实现去重逻辑"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            saved_count = 0
            for question in questions:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO questions 
                        (question_id, title, hot_value, attention_increment, view_increment, answer_increment, vote_increment, tags, collected_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        question['question_id'],
                        question['title'],
                        question.get('hot_value', 0),
                        question.get('attention_increment', 0),
                        question.get('view_increment', 0),
                        question.get('answer_increment', 0),
                        question.get('vote_increment', 0),
                        question.get('tags', ''),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    saved_count += 1
                except sqlite3.IntegrityError:
                    # 问题ID已存在，更新记录
                    pass
            
            conn.commit()
            return saved_count
        except Exception as e:
            logging.error(f"保存问题数据失败: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            # 不要立即关闭连接，以便在同一线程中重用
            pass
    
    def get_questions(self, limit=100, offset=0):
        """获取问题列表"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM questions 
                ORDER BY collected_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"获取问题列表失败: {e}")
            raise
        finally:
            # 不要立即关闭连接，以便在同一线程中重用
            pass
    
    def get_question_count(self):
        """获取问题总数"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM questions')
            return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"获取问题总数失败: {e}")
            raise
        finally:
            # 不要立即关闭连接，以便在同一线程中重用
            pass 