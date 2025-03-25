"""
测试数据库连接和数据插入
"""
import sqlite3
import os
import logging
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 数据库路径
DB_PATH = "database/zhihu_hot_questions.db"

def ensure_db_path():
    """确保数据库目录存在"""
    try:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logging.info(f"创建数据库目录: {db_dir}")
        return True
    except Exception as e:
        logging.error(f"创建数据库目录失败: {e}")
        traceback.print_exc()
        return False

def init_db():
    """初始化数据库表结构"""
    if not ensure_db_path():
        return False
        
    conn = None
    try:
        logging.info(f"尝试连接数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        logging.info("数据库连接成功")
        
        cursor = conn.cursor()
        logging.info("执行表创建语句")
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
        logging.info("数据库表初始化成功")
        return True
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭")

# 测试数据 (简化为1条)
test_questions = [
    {
        "question_id": "15699023937",
        "title": "「订婚强奸案」男方拒绝缓刑，上诉书称双方未发生实质性关系，怎样从法律角度解读？",
        "hot_value": 10.0,
        "attention_increment": 95,
        "view_increment": 138000,
        "answer_increment": 96,
        "vote_increment": 4111,
        "tags": "#法律,#中国法律,#强奸案"
    }
]

def add_test_data():
    """添加测试数据到数据库"""
    conn = None
    try:
        logging.info(f"尝试连接数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        logging.info("数据库连接成功，准备添加测试数据")
        
        cursor = conn.cursor()
        saved_count = 0
        
        for question in test_questions:
            try:
                logging.info(f"尝试插入问题: {question['title']}")
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
                logging.info(f"问题插入成功: {question['title']}")
            except sqlite3.IntegrityError as e:
                logging.warning(f"问题ID已存在: {question['question_id']}, 错误: {e}")
                traceback.print_exc()
        
        conn.commit()
        logging.info(f"提交成功，共添加 {saved_count} 个测试问题到数据库")
        return saved_count
    except Exception as e:
        logging.error(f"保存问题数据失败: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭")

def check_data():
    """检查数据库中的数据"""
    conn = None
    try:
        logging.info(f"尝试连接数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        logging.info("数据库连接成功，准备查询数据")
        
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        table_exists = cursor.fetchone()
        if not table_exists:
            logging.error("questions表不存在!")
            return 0
        
        # 查询总数
        cursor.execute('SELECT COUNT(*) FROM questions')
        total_count = cursor.fetchone()[0]
        logging.info(f"数据库总问题数: {total_count}")
        
        # 查询最新数据
        if total_count > 0:
            cursor.execute('''
                SELECT * FROM questions 
                ORDER BY collected_at DESC
                LIMIT 5
            ''')
            questions = [dict(row) for row in cursor.fetchall()]
            
            logging.info(f"数据库中最新的问题:")
            for i, q in enumerate(questions):
                logging.info(f"{i+1}. {q['title']} (热力值: {q['hot_value']})")
        
        return total_count
    except Exception as e:
        logging.error(f"查询数据失败: {e}")
        traceback.print_exc()
        return 0
    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭")

if __name__ == "__main__":
    logging.info("开始执行测试数据库脚本")
    if init_db():
        logging.info("数据库初始化成功，尝试添加测试数据")
        add_test_data()
        check_data()
    logging.info("测试数据库脚本执行完毕") 