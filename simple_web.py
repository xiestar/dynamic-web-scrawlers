"""
简化版Web服务启动脚本，包含数据库初始化
"""
import os
import sqlite3
import logging
from flask import Flask, jsonify, render_template, request
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 数据库路径
DB_PATH = "database/zhihu_hot_questions.db"

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
    },
    {
        "question_id": "557628284",
        "title": "如何看待3月25日特斯拉官宣「中国业务总裁朱晓彤因个人原因离职」?",
        "hot_value": 9.2,
        "attention_increment": 142,
        "view_increment": 210000,
        "answer_increment": 63,
        "vote_increment": 2835,
        "tags": "#特斯拉,#电动汽车,#商业"
    },
    {
        "question_id": "621934578",
        "title": "当下年轻人为什么开始流行「厨房手账」？记录做饭过程有什么意义？",
        "hot_value": 7.8,
        "attention_increment": 124,
        "view_increment": 81000,
        "answer_increment": 45,
        "vote_increment": 1890,
        "tags": "#美食,#生活方式,#手账"
    },
    {
        "question_id": "590283465",
        "title": "ChatGPT、Midjourney等AI工具是否正在威胁设计师的工作？",
        "hot_value": 8.0,
        "attention_increment": 178,
        "view_increment": 135000,
        "answer_increment": 92,
        "vote_increment": 3248,
        "tags": "#AI,#设计,#职业发展"
    },
    {
        "question_id": "671235892",
        "title": "2025年高考改革将全面实施，对未来考生有何影响？",
        "hot_value": 9.8,
        "attention_increment": 198,
        "view_increment": 257000,
        "answer_increment": 87,
        "vote_increment": 4320,
        "tags": "#教育,#高考,#升学"
    },
    {
        "question_id": "512873461",
        "title": "为什么越来越多年轻人选择「低欲望生活」？",
        "hot_value": 9.5,
        "attention_increment": 215,
        "view_increment": 189000,
        "answer_increment": 112,
        "vote_increment": 5247,
        "tags": "#生活方式,#年轻人,#社会"
    },
    {
        "question_id": "637218945",
        "title": "长时间看手机对视力的影响有多大？如何保护眼睛？",
        "hot_value": 8.6,
        "attention_increment": 219,
        "view_increment": 203000,
        "answer_increment": 74,
        "vote_increment": 3980,
        "tags": "#健康,#眼睛,#手机"
    },
    {
        "question_id": "532789421",
        "title": "数字人民币的普及将会给我们的生活带来哪些变化？",
        "hot_value": 8.4,
        "attention_increment": 167,
        "view_increment": 106000,
        "answer_increment": 59,
        "vote_increment": 2950,
        "tags": "#金融,#数字货币,#经济"
    },
    {
        "question_id": "597821345",
        "title": "春季如何预防花粉过敏？有哪些有效的方法？",
        "hot_value": 7.9,
        "attention_increment": 132,
        "view_increment": 91000,
        "answer_increment": 38,
        "vote_increment": 2156,
        "tags": "#健康,#过敏,#春季"
    }
]

# 最新的热门问题数据（用于更新）
latest_questions = [
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

def init_database():
    """初始化数据库，创建表并添加测试数据"""
    # 确保数据库目录存在
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logging.info(f"创建数据库目录: {db_dir}")
    
    try:
        # 连接数据库
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
        
        # 添加测试数据
        saved_count = 0
        for question in test_questions:
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
                logging.info(f"添加问题成功: {question['title'][:30]}...")
            except Exception as e:
                logging.error(f"添加问题失败: {e}")
        
        conn.commit()
        
        # 查询数据库中的问题总数
        cursor.execute('SELECT COUNT(*) FROM questions')
        total_questions = cursor.fetchone()[0]
        logging.info(f"数据库初始化完成，共有 {total_questions} 条问题数据")
        
        return True
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_database_with_latest():
    """使用最新数据更新数据库"""
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 清空原有数据
        cursor.execute('DELETE FROM questions')
        logging.info("清空了原有问题数据")
        
        # 添加最新数据
        saved_count = 0
        for question in latest_questions:
            try:
                cursor.execute('''
                    INSERT INTO questions 
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
                logging.info(f"添加最新问题成功: {question['title'][:30]}...")
            except Exception as e:
                logging.error(f"添加最新问题失败: {e}")
        
        conn.commit()
        
        # 查询数据库中的问题总数
        cursor.execute('SELECT COUNT(*) FROM questions')
        total_questions = cursor.fetchone()[0]
        logging.info(f"数据库更新完成，共有 {total_questions} 条最新问题数据")
        
        return saved_count
    except Exception as e:
        logging.error(f"数据库更新失败: {e}")
        return 0
    finally:
        if conn:
            conn.close()

# 创建Flask应用
app = Flask(__name__, 
            static_folder='web/static',
            template_folder='web/templates')

# 定义路由
@app.route('/')
def index():
    """首页"""
    return render_template('index.html', title="知乎热点问题采集系统")

@app.route('/api/questions')
def get_questions():
    """获取问题列表API"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取问题列表
        cursor.execute('''
            SELECT * FROM questions 
            ORDER BY hot_value DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        questions = [dict(row) for row in cursor.fetchall()]
        
        # 获取问题总数
        cursor.execute('SELECT COUNT(*) FROM questions')
        total = cursor.fetchone()[0]
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': {
                'questions': questions,
                'total': total,
                'page': page,
                'limit': limit
            }
        })
    except Exception as e:
        logging.error(f"获取问题列表失败: {e}")
        return jsonify({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': None
        })
    finally:
        if conn:
            conn.close()

@app.route('/api/update', methods=['POST'])
def update_questions():
    """更新问题数据API"""
    try:
        count = update_database_with_latest()
        return jsonify({
            'code': 0,
            'msg': '数据更新成功',
            'data': {
                'updated_count': count
            }
        })
    except Exception as e:
        logging.error(f"更新问题数据失败: {e}")
        return jsonify({
            'code': 500,
            'msg': f'更新失败: {str(e)}',
            'data': None
        })

if __name__ == "__main__":
    # 初始化数据库
    init_database()
    
    # 启动Web服务
    logging.info("启动Web服务，监听端口: 5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 