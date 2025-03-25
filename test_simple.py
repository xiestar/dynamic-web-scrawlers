"""
简化版测试脚本，主要测试配置和数据库功能
"""
import os
import asyncio
import logging
from config import Config
from database import Database
from scraper import ZhihuHotQuestionScraper
import sqlite3
import time
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def test_config():
    """测试配置管理类"""
    # 创建临时配置文件
    test_config_path = "test_config.json"
    
    # 清理之前的测试文件
    if os.path.exists(test_config_path):
        os.remove(test_config_path)
    
    # 测试创建默认配置
    config = Config(test_config_path)
    
    print(f"默认采集数量: {config.get('scrape_count')}")
    print(f"默认采集间隔: {config.get('scrape_interval')} 秒")
    
    # 测试更新配置
    config.set("scrape_count", 10)
    print(f"更新后采集数量: {config.get('scrape_count')}")
    
    # 测试解析cookies
    test_cookies = "key1=value1; key2=value2"
    cookies_dict = config.parse_cookies(test_cookies)
    print(f"解析cookies: {cookies_dict}")
    
    # 测试通过
    print("配置类测试通过 ✓")
    
    # 清理测试文件
    if os.path.exists(test_config_path):
        os.remove(test_config_path)
    
    return config

def test_database():
    """测试数据库管理类"""
    # 创建测试数据库
    test_db_path = "test_database.db"
    
    # 清理之前的测试文件
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # 初始化数据库
    db = Database(test_db_path)
    
    # 测试保存问题
    test_questions = [
        {
            "question_id": "12345",
            "title": "测试问题1",
            "hot_value": 100,
            "attention_increment": 10,
            "view_increment": 1000,
            "answer_increment": 5,
            "vote_increment": 20
        },
        {
            "question_id": "67890",
            "title": "测试问题2",
            "hot_value": 200,
            "attention_increment": 20,
            "view_increment": 2000,
            "answer_increment": 10,
            "vote_increment": 40
        }
    ]
    
    saved_count = db.save_questions(test_questions)
    print(f"保存问题数: {saved_count}")
    
    # 测试查询问题
    questions = db.get_questions(limit=10)
    print(f"查询问题数: {len(questions)}")
    print(f"第一个问题: {questions[0]['title']}")
    
    # 测试查询总数
    count = db.get_question_count()
    print(f"问题总数: {count}")
    
    # 测试去重逻辑
    duplicate_question = [
        {
            "question_id": "12345",  # 相同ID
            "title": "测试问题1更新版",
            "hot_value": 150,
            "attention_increment": 15
        }
    ]
    
    db.save_questions(duplicate_question)
    questions = db.get_questions(limit=10)
    print(f"去重后问题数: {len(questions)}")
    
    # 测试通过
    print("数据库类测试通过 ✓")
    
    # 清理测试文件
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    return db

async def test_crawler():
    """简单测试爬虫功能"""
    # 使用项目配置
    config = Config()
    
    print(f"当前cookies长度: {len(config.get('cookies', ''))}")
    
    # 创建爬虫实例
    scraper = ZhihuHotQuestionScraper(config)
    
    try:
        # 执行爬取
        questions = await scraper.scrape()
        
        # 输出结果
        print(f"爬取到 {len(questions)} 个问题")
        
        if questions:
            print("\n前3个问题：")
            for i, q in enumerate(questions[:3]):
                print(f"{i+1}. {q['title']} (热力值: {q['hot_value']})")
        
        # 保存到数据库
        if questions:
            db = Database()
            saved_count = db.save_questions(questions)
            print(f"成功保存 {saved_count} 个问题到数据库")
        
    except Exception as e:
        print(f"爬取过程中发生错误: {e}")
    
    finally:
        # 关闭爬虫
        await scraper.close()

if __name__ == "__main__":
    print("\n=== 测试配置管理类 ===")
    test_config()
    
    print("\n=== 测试数据库管理类 ===")
    test_database()
    
    print("\n=== 测试爬虫功能 ===")
    asyncio.run(test_crawler())

# 确保数据库目录存在
db_dir = "database"
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"创建数据库目录: {db_dir}")

# 数据库路径
db_path = "database/zhihu_hot_questions.db"

# 测试数据
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
    },
    {
        "question_id": "625762414",
        "title": "为何很多人在谈论AI威胁时都在强调「智能」，而不是「自主」?",
        "hot_value": 8.5,
        "attention_increment": 57,
        "view_increment": 93000,
        "answer_increment": 85,
        "vote_increment": 3520,
        "tags": "#人工智能,#AI,#技术"
    }
]

print("开始添加测试数据...")

try:
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
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
    print("表创建成功")
    
    # 添加测试数据
    saved_count = 0
    for question in test_questions:
        try:
            print(f"尝试插入问题: {question['title'][:20]}...")
            cursor.execute('''
                INSERT OR REPLACE INTO questions 
                (question_id, title, hot_value, attention_increment, view_increment, answer_increment, vote_increment, tags, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                question["question_id"],
                question["title"],
                question.get("hot_value", 0),
                question.get("attention_increment", 0),
                question.get("view_increment", 0),
                question.get("answer_increment", 0),
                question.get("vote_increment", 0),
                question.get("tags", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            saved_count += 1
            print(f"插入成功: {question['title'][:20]}...")
        except Exception as e:
            print(f"插入失败: {e}")
    
    # 提交事务
    conn.commit()
    print(f"成功添加 {saved_count} 个问题到数据库")
    
    # 查询验证
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_count = cursor.fetchone()[0]
    print(f"数据库中的问题总数: {total_count}")
    
    cursor.execute("SELECT title, hot_value FROM questions LIMIT 5")
    rows = cursor.fetchall()
    
    print("\n数据库中的问题:")
    for i, row in enumerate(rows):
        print(f"{i+1}. {row[0]} (热力值: {row[1]})")

except Exception as e:
    print(f"出错了: {e}")
finally:
    if conn:
        conn.close()
        print("数据库连接已关闭") 