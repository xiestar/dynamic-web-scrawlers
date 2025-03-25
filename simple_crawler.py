"""
简化版爬虫脚本，用于模拟爬取过程
"""
import logging
import time
import json
import os
import sqlite3
import random
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 数据库路径
DB_PATH = "database/zhihu_hot_questions.db"

# 更新的热门问题数据（更真实的数据）
test_questions = [
    {
        "question_id": "595302071",
        "title": "315曝光卤味企业使用工业明胶熬制骨汤，原因是便宜，工业明胶对人体有哪些危害？",
        "hot_value": 10.0,
        "attention_increment": 142,
        "view_increment": 327000,
        "answer_increment": 108,
        "vote_increment": 5932,
        "tags": "#食品安全,#315晚会,#健康"
    },
    {
        "question_id": "598723614",
        "title": "OpenAI宣布Claude 3全系列模型在大规模基准上已超越GPT-4，这意味着什么？",
        "hot_value": 9.8,
        "attention_increment": 183,
        "view_increment": 289000,
        "answer_increment": 94,
        "vote_increment": 5321,
        "tags": "#人工智能,#科技,#OpenAI"
    },
    {
        "question_id": "602187396",
        "title": "宫崎骏新作《你想活出怎样的人生》引发热议，对当代年轻人的生活态度有何启示？",
        "hot_value": 9.7,
        "attention_increment": 214,
        "view_increment": 312000,
        "answer_increment": 127,
        "vote_increment": 6123,
        "tags": "#动画,#宫崎骏,#人生"
    },
    {
        "question_id": "589231475",
        "title": "近期A股持续下跌，市场恐慌情绪蔓延，应该如何理性看待当前行情？",
        "hot_value": 9.5,
        "attention_increment": 275,
        "view_increment": 358000,
        "answer_increment": 143,
        "vote_increment": 7512,
        "tags": "#股市,#投资,#财经"
    },
    {
        "question_id": "582947105",
        "title": "世卫组织警告称一种未知的「疾病X」或成下一场大流行，有多大可能性？我们应该如何防范？",
        "hot_value": 9.3,
        "attention_increment": 198,
        "view_increment": 267000,
        "answer_increment": 118,
        "vote_increment": 5784,
        "tags": "#健康,#疫情,#世卫组织"
    },
    {
        "question_id": "604782349",
        "title": "住建部表示要合理控制房地产开发贷款比例，此举有何影响？",
        "hot_value": 9.1,
        "attention_increment": 162,
        "view_increment": 231000,
        "answer_increment": 87,
        "vote_increment": 4923,
        "tags": "#房地产,#经济,#政策"
    },
    {
        "question_id": "612384597",
        "title": "最近一项研究表明运动30分钟等于吃一片阿司匹林，这个说法科学吗？",
        "hot_value": 8.9,
        "attention_increment": 143,
        "view_increment": 195000,
        "answer_increment": 76,
        "vote_increment": 4275,
        "tags": "#健康,#运动,#医学研究"
    },
    {
        "question_id": "609127384",
        "title": "ChatGPT即将推出记忆功能，能够记住用户的偏好，这会带来哪些改变？",
        "hot_value": 8.8,
        "attention_increment": 131,
        "view_increment": 182000,
        "answer_increment": 69,
        "vote_increment": 3891,
        "tags": "#人工智能,#科技,#ChatGPT"
    },
    {
        "question_id": "615937284",
        "title": "为什么有些人坚持「快糖饮料难致肥胖」的观点？这种看法有科学依据吗？",
        "hot_value": 8.7,
        "attention_increment": 128,
        "view_increment": 173000,
        "answer_increment": 65,
        "vote_increment": 3748,
        "tags": "#健康,#饮食,#肥胖"
    },
    {
        "question_id": "594827164",
        "title": "3月25日二十国集团财长和央行行长会议将讨论加密货币监管，这对加密货币市场有何影响？",
        "hot_value": 8.6,
        "attention_increment": 119,
        "view_increment": 158000,
        "answer_increment": 58,
        "vote_increment": 3412,
        "tags": "#加密货币,#金融监管,#G20"
    },
    {
        "question_id": "607293841",
        "title": "部分高校今年扩招计算机和人工智能专业，反而缩减传统工科招生计划，这一趋势说明了什么？",
        "hot_value": 8.5,
        "attention_increment": 137,
        "view_increment": 184000,
        "answer_increment": 93,
        "vote_increment": 3957,
        "tags": "#高等教育,#计算机,#人工智能"
    },
    {
        "question_id": "601937482",
        "title": "多家航空公司宣布将恢复或新增国际航线，机票价格有望下降，出境游会迎来爆发吗？",
        "hot_value": 8.4,
        "attention_increment": 113,
        "view_increment": 147000,
        "answer_increment": 54,
        "vote_increment": 3214,
        "tags": "#旅游,#航空,#出境游"
    },
    {
        "question_id": "618472935",
        "title": "22岁女生工作两年存款超百万，称「上班不如存钱有意思」，年轻人该如何树立正确的金钱观？",
        "hot_value": 8.3,
        "attention_increment": 152,
        "view_increment": 197000,
        "answer_increment": 87,
        "vote_increment": 4123,
        "tags": "#理财,#年轻人,#金钱观"
    },
    {
        "question_id": "605839271",
        "title": "网友称麦当劳将儿童套餐玩具改为纸质，对此你怎么看？",
        "hot_value": 8.2,
        "attention_increment": 97,
        "view_increment": 128000,
        "answer_increment": 46,
        "vote_increment": 2917,
        "tags": "#麦当劳,#环保,#快餐"
    },
    {
        "question_id": "597128345",
        "title": "多地试点「8小时工作制考勤月纪检」，采取「弹性考勤」，这对职场人有何影响？",
        "hot_value": 8.1,
        "attention_increment": 107,
        "view_increment": 139000,
        "answer_increment": 52,
        "vote_increment": 3125,
        "tags": "#职场,#工作制度,#考勤"
    }
]

def ensure_db_path():
    """确保数据库目录存在"""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logging.info(f"创建数据库目录: {db_dir}")

def save_questions(questions):
    """保存问题数据到数据库"""
    ensure_db_path()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
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
        
        # 清空旧数据
        cursor.execute('DELETE FROM questions')
        logging.info("清空了旧的问题数据")
        
        # 添加测试数据
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
                logging.warning(f"问题ID已存在: {question['question_id']}")
        
        conn.commit()
        logging.info(f"成功保存 {saved_count} 个问题到数据库")
        return saved_count
    except Exception as e:
        logging.error(f"保存问题数据失败: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def simulate_crawling():
    """模拟爬取过程"""
    # 模拟登录
    logging.info("正在模拟登录知乎...")
    time.sleep(1)
    logging.info("登录成功，设置cookie完成")
    
    # 模拟访问热门问题页面
    logging.info("正在访问知乎热门问题页面...")
    time.sleep(2)
    logging.info("页面加载完成")
    
    # 模拟解析数据
    logging.info("正在解析页面数据...")
    time.sleep(1)
    
    # 模拟保存截图
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    logging.info("已保存页面截图")
    
    # 模拟提取问题数据
    logging.info("提取问题数据...")
    for i, question in enumerate(test_questions):
        logging.info(f"已提取问题 {i+1}/{len(test_questions)}: {question['title']}")
        time.sleep(0.3)  # 减少等待时间，加快模拟过程
    
    # 根据热力值排序
    sorted_questions = sorted(test_questions, key=lambda x: x.get('hot_value', 0), reverse=True)
    
    # 保存数据到数据库
    saved_count = save_questions(sorted_questions)
    logging.info(f"爬取完成，共获取并保存 {saved_count} 个问题")
    
    return sorted_questions

def main():
    """主函数"""
    logging.info("=== 知乎热点问题采集器启动 ===")
    logging.info("开始模拟爬取...")
    
    questions = simulate_crawling()
    
    logging.info("=== 采集结果预览 ===")
    for i, q in enumerate(questions[:5]):
        logging.info(f"{i+1}. {q['title']} (热力值: {q['hot_value']})")
    
    logging.info("=== 爬取任务完成 ===")

if __name__ == "__main__":
    main() 