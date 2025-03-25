"""
数据库测试脚本
"""
import sqlite3
import json
from datetime import datetime
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库路径
DB_PATH = 'database/zhihu_hot_questions.db'

def ensure_db_exists():
    """确保数据库和表存在"""
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建问题表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT UNIQUE,
        title TEXT,
        hot_value REAL,
        attention_increment INTEGER DEFAULT 0,
        view_increment INTEGER DEFAULT 0,
        answer_increment INTEGER DEFAULT 0,
        vote_increment INTEGER DEFAULT 0,
        tags TEXT,
        collected_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    logging.info(f"数据库初始化完成: {DB_PATH}")

def add_test_data():
    """添加测试数据"""
    zhihu_hot_questions = [
        {
            'question_id': '661583285',
            'title': '如何看待美舰被胡塞武装用导弹击中？',
            'hot_value': 10.0,
            'tags': ['国际关系', '军事', '中东局势']
        },
        {
            'question_id': '661617384',
            'title': '如何评价《一人之下》漫画 656 话？',
            'hot_value': 9.8,
            'tags': ['动漫', '漫画', '国漫']
        },
        {
            'question_id': '661632458',
            'title': '女子定了一晚498的酒店，到店后前台说只剩9998的总统套房，如何看待酒店这种行为？',
            'hot_value': 9.6,
            'tags': ['社会', '酒店', '消费']
        },
        {
            'question_id': '661647895',
            'title': '《英雄联盟》S14冠军DK公布冠军皮肤选择，如何评价？',
            'hot_value': 9.4,
            'tags': ['游戏', '电竞', '英雄联盟']
        },
        {
            'question_id': '661581476',
            'title': '如何看待医生这个职业？',
            'hot_value': 9.2,
            'tags': ['医疗', '职业', '健康']
        }
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空表
    cursor.execute("DELETE FROM questions")
    
    # 添加数据
    for question in zhihu_hot_questions:
        cursor.execute(
            "INSERT INTO questions (question_id, title, hot_value, tags, collected_at) VALUES (?, ?, ?, ?, ?)",
            (
                question['question_id'],
                question['title'],
                question['hot_value'],
                json.dumps(question['tags'], ensure_ascii=False),
                datetime.now().isoformat()
            )
        )
    
    conn.commit()
    conn.close()
    logging.info(f"成功添加 {len(zhihu_hot_questions)} 条测试数据")

def view_data():
    """查看数据库数据"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取数据数量
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    count = cursor.fetchone()['count']
    logging.info(f"数据库中共有 {count} 条数据")
    
    # 获取所有数据
    cursor.execute("SELECT * FROM questions ORDER BY hot_value DESC")
    questions = cursor.fetchall()
    
    if not questions:
        logging.info("数据库中没有数据")
        return
    
    logging.info("数据库内容:")
    for i, q in enumerate(questions, 1):
        tags = json.loads(q['tags']) if q['tags'] else []
        print(f"{i}. {q['title']} (热度: {q['hot_value']})")
        print(f"   问题ID: {q['question_id']}")
        print(f"   标签: {tags}")
        print(f"   收集时间: {q['collected_at']}")
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    ensure_db_exists()
    add_test_data()
    view_data() 