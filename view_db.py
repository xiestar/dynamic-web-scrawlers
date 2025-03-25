"""
数据库查询工具 - 显示知乎热门问题数据
"""
import sqlite3
import json
from datetime import datetime
import os

# 数据库文件路径
DB_PATH = 'database/zhihu_hot_questions.db'

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def view_questions(limit=10):
    """查看热门问题数据"""
    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库文件 {DB_PATH} 不存在!")
        return
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 使结果以字典形式返回
        cursor = conn.cursor()
        
        # 获取问题数量
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        count = cursor.fetchone()['count']
        
        # 查询最新问题
        cursor.execute(f"""
            SELECT * FROM questions 
            ORDER BY hot_value DESC 
            LIMIT {limit}
        """)
        
        questions = [dict(row) for row in cursor.fetchall()]
        
        # 打印问题数量
        print_header("数据库统计")
        print(f"数据库中共有 {count} 个问题")
        
        # 打印热门问题
        print_header(f"热门问题 TOP {limit}")
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q['title']} (热度: {q['hot_value']})")
            print(f"   问题ID: {q['question_id']}")
            print(f"   标签: {q.get('tags', [])}")
            
            # 格式化时间
            collected_at = q.get('collected_at')
            if collected_at:
                try:
                    dt = datetime.fromisoformat(collected_at)
                    collected_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            print(f"   收集时间: {collected_at or '未知'}")
            print("-" * 80)
        
        # 关闭连接
        conn.close()
        
    except Exception as e:
        print(f"查询数据库时出错: {e}")

if __name__ == "__main__":
    view_questions(limit=15)  # 显示前15个热门问题 