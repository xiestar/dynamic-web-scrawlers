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
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    """获取问题列表API"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'code': 0,
                'msg': '数据库尚未创建，请等待爬虫首次运行',
                'count': 0,
                'data': []
            })
            
        cursor = conn.cursor()
        
        # 获取问题总数
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        total = cursor.fetchone()['count']
        
        # 获取所有问题，按热度值降序排序
        cursor.execute("""
            SELECT * FROM questions 
            WHERE collected_at >= datetime('now', '-1 day')  
            ORDER BY hot_value DESC
        """)
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

@app.route('/api/update')
def update_data():
    """更新数据API"""
    return jsonify({
        'code': 0,
        'msg': '数据更新由爬虫自动完成，请等待下一次爬取',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/view')
def view_page():
    """查看数据库页面"""
    return render_template('view_data.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 