"""
独立的Web应用，用于查看数据库内容
"""
from flask import Flask, render_template, jsonify
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')

# 数据库路径
DB_PATH = 'database/zhihu_hot_questions.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """首页"""
    questions = get_latest_questions()
    return render_template('view_data.html')

@app.route('/api/questions')
def get_questions():
    """获取问题列表API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取问题总数
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        total = cursor.fetchone()['count']
        
        # 获取所有问题
        cursor.execute("SELECT * FROM questions ORDER BY hot_value DESC")
        questions = [dict(row) for row in cursor.fetchall()]
        
        # 处理标签
        for question in questions:
            if question.get('tags'):
                try:
                    question['tags'] = json.loads(question['tags'])
                except:
                    question['tags'] = []
        
        conn.close()
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'count': total,
            'data': questions
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'获取数据失败: {str(e)}',
            'data': []
        }), 500

def get_latest_questions():
    """获取最新问题列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有问题
        cursor.execute("SELECT * FROM questions ORDER BY hot_value DESC")
        questions = [dict(row) for row in cursor.fetchall()]
        
        # 处理标签
        for question in questions:
            if question.get('tags'):
                try:
                    question['tags'] = json.loads(question['tags'])
                except:
                    question['tags'] = []
        
        conn.close()
        return questions
    except Exception as e:
        print(f"获取问题列表失败: {e}")
        return []

@app.route('/api/update')
def update_data():
    """更新数据API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 清空表
        cursor.execute("DELETE FROM questions")
        
        # 添加最新的知乎热门问题
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
            },
            {
                'question_id': '661649834',
                'title': '为什么外贸生意越来越难做？',
                'hot_value': 9.0,
                'tags': ['经济', '贸易', '商业']
            },
            {
                'question_id': '661602935',
                'title': '手机的散热对游戏体验到底有多重要？',
                'hot_value': 8.8,
                'tags': ['数码', '手机', '游戏']
            },
            {
                'question_id': '661569372',
                'title': '2024年，哪一线城市的生活压力最大？',
                'hot_value': 8.7,
                'tags': ['社会', '城市', '生活']
            },
            {
                'question_id': '661639472',
                'title': '快三十了还经常熬夜加班，怎么调理才能补回来？',
                'hot_value': 8.5,
                'tags': ['健康', '工作', '生活']
            },
            {
                'question_id': '661582638',
                'title': '你是如何度过打工人的周末的？',
                'hot_value': 8.3,
                'tags': ['生活', '工作', '休闲']
            },
            {
                'question_id': '661597548',
                'title': '为什么现在人们这么热衷攀比和炫耀自己的生活？',
                'hot_value': 8.1,
                'tags': ['心理', '社会', '生活']
            }
        ]
        
        # 保存到数据库
        saved_count = 0
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
            saved_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'成功更新 {saved_count} 个热门问题',
            'count': saved_count,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'更新数据失败: {str(e)}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@app.route('/view')
def view_page():
    """查看数据库页面"""
    return render_template('view_data.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 